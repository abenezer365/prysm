"""Portable static evaluation figures; no plotting dependency during inference."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json


def plot_evaluation(output, frame, curves, metrics, selected):
    directory = output / "figures"
    directory.mkdir()
    config = json.loads((output / "config.json").read_text(encoding="utf-8"))
    plt.rcParams.update({"font.size": 10, "figure.dpi": 140})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    c = curves[curves.experiment.eq(selected["name"])]
    for split, color in (("train", "#16767c"), ("validation", "#c35d22")):
        rows = c[c.split.eq(split)]
        for ax, field in zip(axes.flat, ("bce", "precision", "recall", "f1")):
            ax.plot(rows.epoch, rows[field], label=split, color=color)
            ax.set(xlabel="Epoch", ylabel=field.upper(), title=field.upper()+" (post-update)")
            ax.grid(alpha=.2)
            ax.legend()
    fig.suptitle(f"{selected['name']} training monitor — metrics at training-config threshold {selected['config']['threshold']}")
    fig.savefig(directory / "training.png")
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    splits = ("train", "validation", "test")
    counts = [frame[frame.split.eq(s)].target.value_counts() for s in splits]
    axes[0, 0].bar(splits, [v.get(False, 0) for v in counts], label="Normal", color="#16767c")
    axes[0, 0].bar(splits, [v.get(True, 0) for v in counts], bottom=[v.get(False, 0) for v in counts], label="Suspicious", color="#c35d22")
    axes[0, 0].set(title="Case distribution", ylabel="Cases")
    axes[0, 0].legend()
    test = frame[frame.split.eq("test")]
    for target, label, color in ((False, "Normal", "#16767c"), (True, "Suspicious", "#c35d22")):
        axes[0, 1].hist(test.loc[test.target.eq(target), "overall_strength"], bins=np.linspace(0, 1, 21), alpha=.7, label=label, color=color)
    axes[0, 1].axvline(config["fusion"]["moderate"], color="black", linestyle="--", label="Review threshold")
    axes[0, 1].set(title="Test fusion scores", xlabel="Attention score", ylabel="Cases")
    axes[0, 1].legend()
    names = ("rules", "anomaly", "network", "gnn", "fusion")
    x = np.arange(len(names))
    for offset, field, color in ((-.25, "fp", "#16767c"), (0, "fn", "#c35d22")):
        axes[1, 0].bar(x+offset, [metrics["test"][n]["confusion"][field] for n in names], width=.25, label=field.upper(), color=color)
    axes[1, 0].bar(x+.25, [metrics["test"][n]["unavailable"] for n in names], width=.25, label="Unavailable", color="#858585")
    axes[1, 0].set(xticks=x, xticklabels=names, ylabel="Cases", title="Test component errors (broad target)")
    axes[1, 0].legend()
    for split in ("validation", "test"):
        ranks = metrics[split]["fusion"]["ranking"]
        for field, style in (("precision", "-"), ("recall", "--")):
            axes[1, 1].plot([int(k) for k in ranks], [r[field] for r in ranks.values()], style, marker="o", label=f"{split} {field}")
    axes[1, 1].set(title="Fusion ranking quality", xlabel="K", ylabel="Fraction", ylim=(0, 1.05))
    axes[1, 1].legend(fontsize=8)
    fig.suptitle("Controlled synthetic benchmark — not real-world accuracy")
    fig.savefig(directory / "evaluation.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    for name, rows in curves[curves.split.eq("validation")].groupby("experiment"):
        axes[0].plot(rows.epoch, rows.bce, label=name)
        axes[1].plot(rows.epoch, rows.f1, label=name)
    for ax, field in zip(axes, ("Unweighted BCE", "F1 at training-config threshold")):
        ax.set(xlabel="Epoch", ylabel=field)
        ax.legend()
        ax.grid(alpha=.2)
    fig.suptitle("Validation monitoring across controlled GNN experiments")
    fig.savefig(directory / "experiments.png")
    plt.close(fig)
