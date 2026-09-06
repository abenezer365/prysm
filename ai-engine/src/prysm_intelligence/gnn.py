"""Two-layer relational mean GraphSAGE, fully trained with NumPy backpropagation.

Each layer learns from self features plus five neighbor means. A subject/graph
readout learns the synthetic observed-scenario target. All message weights learn;
there are no learned identity embeddings or frozen random feature projections.
"""
from dataclasses import replace
import numpy as np

from .graph import NODE_FEATURES, RELATIONS


class RelationalSAGE:
    VERSION = "relational-mean-sage-v2"

    def __init__(self, config, seed):
        self.config, self.seed = config, seed
        h, d, r = config["hidden_dim"], len(NODE_FEATURES), len(RELATIONS)+1
        rng = np.random.default_rng(seed)
        self.parameters = {
            "w1": rng.normal(0, 1/np.sqrt(d*r), (d*r, h)), "b1": np.zeros(h),
            "w2": rng.normal(0, 1/np.sqrt(h*r), (h*r, h)), "b2": np.zeros(h),
            "out": rng.normal(0, 1/np.sqrt(h*2), h*2), "bias": np.zeros(1),
        }
        self.center, self.scale = np.zeros(d), np.ones(d)
        self.losses = []
        self.fitted = False

    def _forward(self, sample):
        if not np.isfinite(sample.x).all() or sample.x.shape[1] != len(NODE_FEATURES):
            raise ValueError("Invalid GNN input features")
        if sample.adjacency.shape != (len(RELATIONS), len(sample.x), len(sample.x)) or (sample.adjacency < 0).any() or not np.isfinite(sample.adjacency).all():
            raise ValueError("Invalid GNN adjacency")
        if not 0 <= sample.root < len(sample.x):
            raise ValueError("Invalid GNN root")
        a = sample.adjacency/np.maximum(sample.adjacency.sum(axis=2, keepdims=True), 1.)
        x = np.clip((sample.x-self.center)/self.scale, -8, 8)
        p = self.parameters
        b0 = np.concatenate([x, *(channel@x for channel in a)], axis=1)
        h1 = np.tanh(b0@p["w1"]+p["b1"])
        b1 = np.concatenate([h1, *(channel@h1 for channel in a)], axis=1)
        h2 = np.tanh(b1@p["w2"]+p["b2"])
        readout = np.concatenate([h2[sample.root], h2.mean(axis=0)])
        logit = float(readout@p["out"]+p["bias"][0])
        return logit, (a, b0, h1, b1, h2, readout)

    def loss_gradient(self, sample, target, weight=1.):
        logit, (a, b0, h1, b1, h2, readout) = self._forward(sample)
        probability = float(1/(1+np.exp(-np.clip(logit, -40, 40))))
        loss = float(weight*(np.logaddexp(0, logit)-target*logit))
        delta = weight*(probability-target)
        p, h = self.parameters, self.config["hidden_dim"]
        gradients = {"out": readout*delta, "bias": np.asarray([delta])}
        d_readout = p["out"]*delta
        d_h2 = np.tile(d_readout[h:]/len(h2), (len(h2), 1))
        d_h2[sample.root] += d_readout[:h]
        d_z2 = d_h2*(1-h2*h2)
        gradients["w2"], gradients["b2"] = b1.T@d_z2, d_z2.sum(axis=0)
        d_b1 = d_z2@p["w2"].T
        d_h1 = d_b1[:, :h].copy()
        for r, channel in enumerate(a):
            d_h1 += channel.T@d_b1[:, (r+1)*h:(r+2)*h]
        d_z1 = d_h1*(1-h1*h1)
        gradients["w1"], gradients["b1"] = b0.T@d_z1, d_z1.sum(axis=0)
        return loss, gradients

    def fit(self, samples, labels, observer=None):
        labels = np.asarray(labels, float)
        if len(samples) != len(labels) or set(labels) != {0., 1.}:
            raise ValueError("GNN training requires matching observations and both binary classes")
        values = np.concatenate([s.x for s in samples])
        self.center, self.scale = values.mean(axis=0), np.maximum(values.std(axis=0), .2)
        weights = np.where(labels == 1, len(labels)/(2*labels.sum()), len(labels)/(2*(len(labels)-labels.sum())))
        first = {k: np.zeros_like(v) for k, v in self.parameters.items()}
        second = {k: np.zeros_like(v) for k, v in self.parameters.items()}
        self.losses = []
        for epoch in range(1, self.config["epochs"]+1):
            gradients = {k: np.zeros_like(v) for k, v in self.parameters.items()}
            loss = 0.
            for sample, label, weight in zip(samples, labels, weights):
                value, grad = self.loss_gradient(sample, label, weight)
                loss += value/len(samples)
                for key in gradients:
                    gradients[key] += grad[key]/len(samples)
            self.losses.append(loss)
            for key, parameter in self.parameters.items():
                gradient = gradients[key]+self.config["l2"]*parameter
                gradient = np.clip(gradient, -5, 5)
                first[key] = .9*first[key]+.1*gradient
                second[key] = .999*second[key]+.001*gradient*gradient
                parameter -= self.config["learning_rate"]*(first[key]/(1-.9**epoch))/(np.sqrt(second[key]/(1-.999**epoch))+1e-8)
            # Read-only evaluation hook: held-out samples never enter gradients.
            if observer is not None and (epoch == 1 or epoch % 10 == 0 or epoch == self.config["epochs"]):
                observer(self, epoch)
        self.fitted = True
        return self

    def predict(self, sample):
        if not self.fitted:
            raise RuntimeError("GNN is not fitted")
        logit, _ = self._forward(sample)
        return float(1/(1+np.exp(-np.clip(logit, -40, 40))))

    def explain(self, sample, limit=5):
        """Bounded edge ablation with features held fixed; sensitivity, not causality."""
        baseline = self.predict(sample)
        items = []
        # Remove all transactions between an account pair together: this avoids
        # identical parallel-edge normalization masking any individual removal.
        groups = {}
        for tid, channels in sample.transaction_channels.items():
            groups.setdefault(tuple(channels), []).append(tid)
        for channels, tids in sorted(groups.items()):
            ablated = sample.adjacency.copy()
            for channel, row, col in channels:
                ablated[channel, row, col] = 0
            score = self.predict(replace(sample, adjacency=ablated))
            if baseline-score > 1e-6:
                items.append({"transaction_ids": sorted(tids), "score_drop": baseline-score,
                              "source_node": sample.node_keys[channels[0][2]], "target_node": sample.node_keys[channels[0][1]]})
        return sorted(items, key=lambda item: (-item["score_drop"], item["transaction_ids"]))[:limit]

    def to_dict(self):
        return {"version": self.VERSION, "config": self.config, "seed": self.seed,
                "task": "synthetic retrospective primary-subject node classification",
                "node_features": list(NODE_FEATURES), "relations": list(RELATIONS), "fitted": self.fitted,
                "center": self.center.tolist(), "scale": self.scale.tolist(), "training_loss": self.losses,
                "parameters": {k: v.tolist() for k, v in self.parameters.items()},
                "is_fraud_probability": False}

    @classmethod
    def from_dict(cls, artifact):
        if artifact["version"] != cls.VERSION or artifact["node_features"] != list(NODE_FEATURES) or artifact["relations"] != list(RELATIONS):
            raise ValueError("GNN artifact contract mismatch")
        model = cls(artifact["config"], artifact["seed"])
        for key, template in model.parameters.items():
            value = np.asarray(artifact["parameters"][key], float)
            if value.shape != template.shape or not np.isfinite(value).all():
                raise ValueError("Invalid GNN artifact parameters")
            model.parameters[key] = value
        model.center, model.scale = np.asarray(artifact["center"]), np.asarray(artifact["scale"])
        if model.center.shape != (len(NODE_FEATURES),) or model.scale.shape != model.center.shape or not np.isfinite(model.center).all() or not np.isfinite(model.scale).all() or (model.scale <= 0).any():
            raise ValueError("Invalid GNN preprocessing")
        model.fitted, model.losses = artifact["fitted"], artifact["training_loss"]
        return model
