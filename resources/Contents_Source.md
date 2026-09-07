motto
  Track the flow,
  parase the relatoin,
  Expose Frauds.

# Ethical AI

## Intelligence without compromising the integrity of the data.

Prysm is built around a simple idea:

**Financial intelligence should help us understand data without changing what the data actually says.**

The financial records used by Prysm represent the underlying activity of people, accounts, businesses, and transactions. Those records are treated as the foundation of an investigation, not as something for the AI to rewrite or reinterpret into a different reality.

Prysm separates the **source of truth** from the **intelligence derived from it**.

PostgreSQL remains responsible for storing operational facts and workflow state. The AI Engine analyzes those facts. Relationship intelligence examines connections between entities. RAG retrieves relevant information and produces grounded explanations.

The intelligence layer can calculate, compare, identify, connect, and explain.

**It does not get to rewrite the underlying financial reality.**

> **“Analyze the data. Preserve the truth.”**

---

# Data Integrity Comes First

Prysm does not treat financial data as disposable input for an AI model.

The data has an established place in the system.

Operational financial facts remain in the database, while analytical systems work from that information to produce additional intelligence.

This creates an important distinction between:

**What actually happened**

and

**What the system concludes may be important about what happened.**

For example, if a transaction exists in the underlying system, Prysm's analytical process may identify it as part of an unusual pattern, include it in a behavioral analysis, or connect it to other transactions through relationship intelligence.

But the analytical result does not replace the original transaction.

The original record remains the reference point.

The AI may produce:

**“This transaction contributes to an unusual velocity pattern.”**

It does not transform the transaction itself into:

**“Fraudulent transaction.”**

That distinction is fundamental to how Prysm approaches ethical financial intelligence.

> **“The analysis can change. The underlying fact should not.”**

---

# We Don't Let the AI Rewrite Reality

Large language models are exceptionally good at producing human-readable explanations.

They are not, however, the authoritative source of financial truth.

Prysm therefore does not position the language model as the place where financial facts are created.

The analytical systems determine what the data indicates.

The retrieval layer gathers relevant supporting information.

The language model can then help explain that information in a form that investigators can understand.

This creates a deliberate separation:

**Data → Analysis → Evidence → Explanation**

rather than:

**Data → AI imagination → conclusion**

The language model is therefore an interface for understanding intelligence, not a replacement for the underlying data.

If the database says one thing and a generated response says something else, the generated response is not allowed to become the new financial fact.

> **“The AI explains the evidence. It does not become the evidence.”**

---

# The Data Remains the Data

Prysm's intelligence process may calculate new information from existing financial records.

It may derive:

* behavioral patterns,
* transaction velocity,
* anomaly indicators,
* relationship structures,
* graph representations,
* analytical findings,
* investigation context,
* and explanations.

These are **derived intelligence**, not replacements for the original financial records.

This means Prysm can create a richer understanding of the data without pretending that its interpretation is the data itself.

A transaction remains a transaction.

A relationship remains a relationship.

A timestamp remains a timestamp.

An account remains an account.

The AI adds intelligence **around the information** rather than rewriting the information itself.

> **“Derived intelligence should enrich the record, not rewrite the record.”**

---

# Controlled Data Flow

Prysm does not allow every component to freely access everything.

The architecture establishes boundaries between the frontend, backend, database, AI Engine, and RAG system.

The browser communicates with the backend rather than directly communicating with the AI Engine or RAG service.

The backend is responsible for authentication, authorization, trusted context, orchestration, persistence, and auditing.

The database remains responsible for operational facts.

The AI Engine performs analytical processing.

RAG retrieves knowledge and produces grounded explanations.

This separation means that intelligence is produced through a controlled pipeline rather than by allowing an AI model unrestricted access to the entire system.

> **“Every component should have access to what it needs — and nothing more.”**

---

# We Analyze; We Don't Alter

Prysm's AI exists to **observe and analyze financial activity**.

It can inspect historical behavior.

It can compare transactions.

It can identify unusual activity.

It can discover relationships.

It can construct graph-based representations.

It can produce analytical findings.

But these operations are fundamentally different from modifying the original financial facts.

Think of Prysm as a layer of intelligence placed above the financial record.

The database answers:

**“What happened?”**

The intelligence layer asks:

**“What does this activity look like?”**

The investigation layer asks:

**“Why might this matter?”**

And the investigator ultimately asks:

**“What should we do about it?”**

This separation allows the system to become more intelligent without giving the AI authority over the underlying financial record.

> **“Observe first. Interpret carefully. Preserve the record.”**

---

# Intelligence Is Derived, Not Fabricated

Prysm can derive new intelligence from existing information.

For example, thousands of individual transactions can be analyzed together to identify a behavioral pattern.

Multiple relationships can be represented as a graph.

Several signals can contribute to an investigation finding.

Relevant information can be retrieved to help explain that finding.

These outputs are valuable because they transform raw information into something easier to understand.

But derived intelligence must remain distinguishable from original evidence.

A calculated anomaly score is not an original transaction.

A graph connection is not an original account.

An AI-generated explanation is not an original financial record.

They are different layers of information with different levels of authority.

Prysm's architecture is designed around these boundaries.

> **“Derived insight is valuable precisely because we know it is derived.”**

---

# No Silent Changes to Financial Reality

A responsible intelligence platform should never silently transform the information it is supposed to investigate.

Prysm therefore separates operational persistence from analytical processing.

The database stores the operational facts.

Analytical services consume those facts to perform their specialized tasks.

This means that an anomaly detector can say:

**“This behavior differs from the established pattern.”**

without modifying the underlying transaction history.

A graph model can identify a structural relationship without changing the underlying ownership or transaction records.

An LLM can explain an investigation without becoming the system of record.

This gives every layer a clear responsibility.

> **“Intelligence can evolve. The evidence must remain traceable.”**

---

# Privacy Through Controlled Context

Prysm does not need to expose the entire financial dataset to every AI operation.

Instead, intelligence can be constructed around a specific investigation and its authorized context.

This matters because financial data contains far more information than may be relevant to a particular question.

An investigator asking about one account should not require unrestricted exposure of every account in the system.

The objective is therefore not:

**“Give the AI everything.”**

The objective is:

**“Give the AI enough relevant information to perform the task responsibly.”**

This creates a more controlled relationship between the AI and sensitive information.

> **“More data does not always mean better intelligence.”**

---

# Data Minimization by Design

Prysm's investigation architecture places boundaries around analytical context rather than treating the entire database as one unrestricted source of information.

The system can work with defined investigation scope, historical windows, relationship depth, and other contextual boundaries.

This allows an investigation to remain focused.

Instead of allowing an AI system to wander through unrelated financial information, Prysm can construct a relevant context around the specific investigation.

This is important not only for privacy, but also for analytical quality.

Unnecessary information can introduce noise.

Irrelevant relationships can create misleading connections.

Unrelated transactions can distort behavioral interpretation.

A smaller, relevant context can therefore produce both **better intelligence and better data governance.**

> **“Use the relevant data. Respect the irrelevant data.”**

---

# The AI Does Not Own the Data

Prysm treats AI as a processing and intelligence layer — not as the owner of the financial information.

This distinction becomes especially important when language models or external AI services are involved.

The model receives information for a defined purpose.

It processes that information.

It produces an explanation or analytical response.

But ownership and authority remain within the platform's controlled data architecture.

The LLM does not become the system of record simply because it generated a response about that record.

> **“The model may process intelligence. It does not own the intelligence.”**

---

# Evidence Before Explanation

Prysm's RAG architecture reinforces another important ethical boundary.

The system should retrieve relevant information before asking a language model to explain it.

This means the explanation layer is connected to an evidence layer.

Instead of asking the model:

**“What do you think happened?”**

the system can provide relevant context and ask:

**“Explain what this evidence indicates.”**

That difference matters.

It reduces the role of free-form generation and increases the role of grounded explanation.

The model becomes a translator of complex intelligence into understandable language rather than an independent investigator inventing facts.

> **“Retrieve first. Explain second.”**

---

# No Fabricated Financial Facts

Prysm's AI should never need to invent a transaction, relationship, account, customer, or investigative event to make an explanation sound convincing.

If the evidence is unavailable, the system should communicate that limitation.

If an analytical component is unavailable, the system should not pretend that the analysis was performed.

If the available evidence is insufficient, the system should not manufacture certainty.

This is particularly important for a financial-intelligence platform because a convincing fictional statement can be more dangerous than an obvious error.

Prysm therefore places value on **grounded intelligence over impressive-sounding intelligence.**

> **“A useful answer is better than a convincing invention.”**

---

# Protecting Context

Data can become misleading when it is removed from its original context.

A transaction amount without its timestamp may mean something different.

A relationship without its type may be misleading.

A behavioral anomaly without its historical baseline may be difficult to interpret.

A graph connection without its underlying relationship may create the wrong impression.

Prysm's intelligence architecture therefore treats context as part of the evidence.

The goal is not simply to collect more information.

The goal is to preserve the information necessary to understand what the data actually represents.

> **“Context is part of the evidence.”**

---

# Ethical Intelligence Is About Restraint

The most powerful AI system is not necessarily the system that does the most.

Sometimes responsible intelligence means **not doing something**.

Not accessing information that is irrelevant.

Not exposing information to an unauthorized component.

Not changing the original record.

Not presenting an anomaly as confirmed fraud.

Not inventing an explanation when evidence is missing.

Not allowing a relationship to become an accusation.

Not allowing a generated response to become a financial fact.

Prysm's ethical architecture is therefore partly defined by what the system deliberately refuses to do.

> **“Responsible intelligence is knowing where to stop.”**

---

# Human Context Completes Machine Analysis

Prysm can process information at a scale that would be difficult for a human investigator to examine manually.

But scale does not equal understanding.

The system may recognize that a pattern is unusual.

The investigator may know why it is unusual.

The system may identify a relationship.

The investigator may understand the legitimate reason behind it.

The system may surface a financial anomaly.

The investigator may discover the business event that explains it.

This is why Prysm's ethical model keeps humans within the investigative process.

The AI provides computational scale.

The data provides evidence.

The investigator provides context and judgment.

> **“Machines can process the pattern. People understand the context.”**

---

# A Clear Boundary Between Fact and Interpretation

Prysm can be understood through three layers:

### FACT

What exists in the underlying financial records.

### SIGNAL

What the analytical systems identify from those records.

### INTERPRETATION

What investigators understand those signals to mean.

These layers should not be collapsed into one another.

A fact is not automatically a signal.

A signal is not automatically a conclusion.

And a conclusion should not be rewritten into a fact simply because an AI produced it.

This boundary is at the heart of Prysm's approach to ethical intelligence.

> **“Fact. Signal. Interpretation. Keep them distinct.”**

---

# Our Ethical Data Principle

Prysm does not promise that AI will never make a mistake.

Instead, Prysm is designed so that an AI mistake does not automatically become a new financial reality.

The underlying records remain the reference point.

Analytical outputs remain analytical outputs.

Generated explanations remain explanations.

Investigative decisions remain human decisions.

This separation gives the system room to use powerful AI while maintaining a clear boundary around the information that AI is allowed to interpret.

That is the principle behind Prysm's approach:

> ## **“Analyze deeply. Change nothing that should remain factual.”**

---

# Prysm's Commitment

Prysm is designed to make financial information easier to understand without making the information itself less trustworthy.

We use AI to discover patterns.

We use graph intelligence to understand relationships.

We use analytical models to identify unusual behavior.

We use retrieval to ground explanations.

And we use human investigation to put those findings into context.

Through all of these layers, one principle remains constant:

**The intelligence may become richer, but the evidence must remain recognizable.**

Prysm does not need to rewrite the financial world to understand it.

It needs to understand the information that already exists — carefully, transparently, and within controlled boundaries.

Because the purpose of financial intelligence is not to create a more convenient version of reality.

It is to create a **clearer understanding of reality.**

> ## **“Don't change the evidence. Change how clearly we can understand it.”**


# Human Oversight

## AI can find what deserves attention. Humans decide what deserves action.

Prysm is designed around a simple boundary:

**The AI can assist an investigation, but it does not become the investigator.**

Financial intelligence often involves incomplete information, unusual circumstances, complex relationships, and decisions that cannot responsibly be reduced to a model output.

Prysm's AI Engine can process large amounts of financial activity, identify behavioral anomalies, analyze transaction patterns, examine relationships, and surface information that may otherwise be difficult to discover.

But those capabilities are deliberately positioned as **investigative assistance**.

The final interpretation remains with the human investigator.

Prysm therefore does not treat an AI finding as the end of an investigation.

It treats it as the beginning of a better-informed one.

> **“AI finds the signal. Humans determine the meaning.”**

---

# The Human Remains in the Loop

Prysm's workflow is not designed as:

**Data → AI → Automatic Decision**

Instead, the intended flow is:

**Data → Analysis → Evidence → Investigator → Decision**

The AI performs the computational work.

The investigator performs the contextual work.

This distinction allows Prysm to use machine intelligence without giving the machine unrestricted authority over the outcome of an investigation.

The system can say:

**“This account exhibits unusual transaction behavior.”**

The investigator can then ask:

**“Why?”**

**“Compared with what?”**

**“What transactions caused this finding?”**

**“Is there a legitimate explanation?”**

**“Is there additional context that the system does not have?”**

Only after examining those questions should an investigative decision be made.

> **“The AI starts the investigation. It does not finish it.”**

---

# Prysm Does Not Decide Guilt

Prysm is not designed to determine that a person is guilty, fraudulent, or criminal.

Its analytical components identify patterns that may deserve further examination.

This distinction is intentionally maintained throughout the system.

An anomaly is an anomaly.

A relationship is a relationship.

A risk signal is a risk signal.

None of these automatically becomes a verdict.

The investigator is responsible for determining whether the available evidence supports further action.

This prevents the platform from turning a machine-generated observation into an automatic judgment about a person or organization.

> **“A machine-generated signal is not a human verdict.”**

---

# From Detection to Investigation

Prysm's AI Engine can make large-scale financial analysis practical.

Instead of an investigator manually searching through thousands of transactions, the system can identify patterns that deserve attention.

For example, Prysm may surface:

* unusual transaction velocity,
* behavioral deviations,
* foreign-income anomalies,
* structuring-like activity,
* unusual transaction sequences,
* connected entities,
* network-level patterns,
* or other analytical findings.

The purpose of these findings is not to tell the investigator:

**“This is fraud.”**

The purpose is to tell them:

**“This is worth looking at.”**

The investigator can then move from automated detection to human investigation.

This is where the value of human oversight becomes visible.

> **“Detection narrows the search. Investigation establishes the context.”**

---

# Humans Provide the Context AI Cannot See

Financial behavior exists inside a world that is larger than the available dataset.

A model may see an unusually large payment.

An investigator may know that the company just completed a major contract.

A model may see multiple connected accounts.

An investigator may know that the accounts belong to legitimate business partners.

A model may identify a sudden behavioral change.

An investigator may know that the customer's business has recently expanded.

The system can identify the pattern.

The investigator can understand the circumstances surrounding it.

This is why Prysm does not attempt to remove the human from the process.

Human oversight provides the contextual layer that analytical systems cannot reliably guarantee.

> **“The model sees the pattern. The investigator sees the circumstances.”**

---

# Evidence Gives the Human Something to Question

Human oversight is meaningful only when the investigator can actually examine what the AI is doing.

Simply placing a human at the end of an automated pipeline does not create meaningful oversight.

Prysm instead emphasizes evidence-oriented investigation.

When an analytical finding is presented, the investigator should be able to understand what information contributed to that finding and examine the relevant context.

This allows the investigator to challenge the result rather than simply accept it.

The important question becomes:

**“Why did Prysm flag this?”**

rather than:

**“What did Prysm decide?”**

That difference changes the role of AI from authority to assistant.

> **“Human oversight means having enough evidence to question the machine.”**

---

# Investigators Can Disagree With Prysm

A responsible AI system must allow its users to say:

**“I don't agree.”**

Prysm's findings should therefore be treated as analytical outputs that can be investigated, challenged, contextualized, and ultimately accepted or rejected by the responsible human.

An investigator may discover that:

* the behavior has a legitimate explanation,
* the available data is incomplete,
* the relationship has a different meaning,
* the anomaly is expected for that particular business,
* or the model's interpretation does not adequately represent the situation.

The existence of an AI finding does not remove the investigator's ability to disagree with it.

In fact, disagreement is part of the intended workflow.

> **“Trustworthy AI does not demand agreement. It makes disagreement possible.”**

---

# Human Oversight Is Not a Rubber Stamp

Prysm does not define human oversight as simply asking an investigator to approve whatever the AI produces.

A human who cannot question the output is not truly overseeing the system.

Meaningful oversight requires the investigator to have access to enough information to evaluate the finding.

That includes understanding:

**What was detected?**

**What evidence supports it?**

**What context was analyzed?**

**What limitations exist?**

**What relationships were considered?**

**What information may be missing?**

**What alternative explanation could exist?**

The investigator should be able to move from the AI's conclusion back toward the evidence that produced the signal.

> **“Human oversight is not approval. It is informed judgment.”**

---

# AI Recommendations Remain Recommendations

Prysm's intelligence can prioritize what deserves attention.

It can help investigators identify potentially important activity within large datasets.

It can organize complex information.

It can expose relationships.

It can explain analytical findings.

But these outputs remain **recommendations and investigative signals**.

They do not become commands.

The system does not have personal authority over the subject of an investigation.

The investigator decides whether a finding is meaningful, whether additional evidence is required, and what action should follow.

This creates a clear boundary between computational intelligence and institutional decision-making.

> **“AI recommends. Humans decide.”**

---

# Human Oversight Across Prysm's Intelligence Layers

Human oversight is not limited to one model.

Prysm combines several forms of intelligence, including behavioral analysis, anomaly detection, transaction analysis, graph intelligence, GNN-based structural analysis, and RAG-assisted explanation.

Each layer contributes a different perspective.

An anomaly detector may identify unusual behavior.

A graph model may reveal a structural relationship.

Transaction analysis may expose a sequence or velocity pattern.

RAG may help explain the available evidence.

None of these individual components should independently become the final decision-maker.

Instead, their outputs contribute to a broader investigative picture that the human can examine.

> **“Multiple models can expand the picture. Only the investigator decides what the picture means.”**

---

# Human Oversight of Graph Intelligence

Graph intelligence makes it possible for Prysm to see relationships that may be difficult to recognize from individual transactions.

But the existence of a connection does not explain its purpose.

A graph can reveal:

**Person A → Account B → Business C**

The investigator still needs to understand what that connection represents.

It could be:

* legitimate ownership,
* ordinary business activity,
* a shared organization,
* a financial partnership,
* or something requiring further investigation.

The graph provides structure.

The investigator provides interpretation.

This is especially important because network visualization can make relationships appear more significant than they actually are if they are viewed without context.

Prysm therefore treats graph intelligence as a tool for understanding networks rather than an automatic mechanism for assigning blame.

> **“The graph shows who is connected. The investigator determines why it matters.”**

---

# Human Oversight of RAG and AI Explanations

Prysm's RAG layer can make complex analytical results easier to understand by retrieving relevant context and generating explanations.

But the explanation itself remains an AI-generated interpretation.

It should therefore never outrank the underlying evidence.

If an explanation says something that cannot be supported by the available evidence, the investigator should be able to recognize that discrepancy.

The hierarchy remains:

**Evidence first.**

**Analysis second.**

**Explanation third.**

The language model helps communicate intelligence.

It does not become the authority that determines whether the intelligence is true.

> **“An explanation can clarify evidence. It cannot replace it.”**

---

# Humans Can Provide Missing Context

No financial intelligence system has access to every fact about an investigation.

There may be information outside the dataset.

There may be business circumstances unknown to the model.

There may be legitimate explanations that cannot be inferred from transaction history alone.

Human investigators can introduce that missing context into the investigative process.

This means Prysm is not designed around the assumption that:

**“If the AI cannot see it, it does not exist.”**

Instead, the system recognizes that its analytical view is based on the information available to it.

The investigator remains capable of expanding that understanding.

> **“The absence of information is not proof of the absence of an explanation.”**

---

# Humans Remain Accountable

AI should never become an excuse for removing responsibility from decision-makers.

A statement such as:

**“The model flagged it.”**

does not explain what should happen next.

The responsible investigator must still evaluate the finding.

The organization deploying Prysm must still establish appropriate procedures.

The system itself must still communicate its limitations.

Prysm therefore keeps a clear separation between **AI assistance** and **human accountability**.

The machine performs analysis.

The human owns the investigative decision.

> **“Never hide a human decision behind an algorithm.”**

---

# Oversight Through Auditability

Human oversight also depends on being able to reconstruct what happened.

Prysm's architecture includes auditing around sensitive workflows so that investigative actions can be attributable and traceable.

This creates a history around the use of intelligence.

It allows organizations to ask:

**Who accessed the investigation?**

**What operation was performed?**

**When did it happen?**

**What system was involved?**

**What decision or action was recorded?**

This is important because responsible human oversight is not only about what an investigator does today.

It is also about being able to understand and review that process later.

> **“If a decision matters, its history matters.”**

---

# Oversight Through Transparency

Prysm's analytical architecture is designed to preserve information about findings, evidence, model information, limitations, provenance, and component availability.

This gives investigators more than a final result.

It gives them context around the result.

If a component was unavailable, that matters.

If evidence is limited, that matters.

If an analysis is derived from a specific historical window, that matters.

If a finding comes from a particular analytical component, that matters.

Transparency gives the human investigator the information required to determine how much weight a particular finding deserves.

> **“The investigator should know not only what the AI found, but how much trust to place in the finding.”**

---

# Temporal Human Oversight

Human investigation also requires understanding **when** information was available.

Prysm's analytical architecture uses investigation boundaries and historical context so that future information does not improperly influence an earlier analysis.

This means an investigator examining historical activity can understand the behavior within an appropriate time boundary.

The system should not create hindsight-based suspicion simply because later events make earlier activity look different.

Human oversight therefore includes the ability to understand the investigation in its proper temporal context.

> **“Don't let hindsight become evidence.”**

---

# When Prysm Is Uncertain

There are situations where Prysm may not have enough information to produce a strong analytical conclusion.

That is not a failure that should be hidden.

It is a condition the investigator needs to know about.

If the available evidence is limited, the investigator can decide whether additional information is necessary.

If an analytical component is unavailable, that limitation can influence how much weight should be placed on the result.

If the available context does not support a strong conclusion, the investigator can choose not to escalate the finding.

This creates a healthier relationship between AI confidence and human judgment.

> **“When the machine is uncertain, the human gets the final say.”**

---

# The Investigator Is the Final Context Layer

Prysm can bring together information from different analytical perspectives.

But the investigator remains the final context layer.

The investigator can connect the machine's findings with:

* organizational knowledge,
* business context,
* investigative procedures,
* additional evidence,
* external information available through legitimate processes,
* and human reasoning.

This makes the system collaborative rather than autonomous.

Prysm does not attempt to simulate human authority.

It attempts to **augment human capability.**

> **“Prysm does not replace the investigator. It gives the investigator a wider lens.”**

---

# A Deliberate Boundary

The boundary within Prysm can be summarized simply:

### The AI can:

**Detect**

**Analyze**

**Compare**

**Connect**

**Prioritize**

**Explain**

### The human can:

**Question**

**Verify**

**Contextualize**

**Reject**

**Escalate**

**Decide**

That boundary is intentional.

It allows Prysm to take advantage of AI's ability to process complexity while preserving the human responsibility required for consequential financial investigations.

---

# The Prysm Human Oversight Principle

Prysm is not designed to create a world where investigators simply receive decisions from machines.

It is designed to create a world where investigators can examine more information, discover patterns faster, understand complex relationships more clearly, and make decisions with stronger evidence.

The AI handles computational complexity.

The data provides the foundation.

The analytical models provide signals.

The RAG layer helps explain them.

And the investigator remains responsible for deciding what those signals actually mean.

That is the boundary Prysm is built to protect.

> ## **“AI can find the signal. AI can explain the signal. But humans decide what the signal means.”**






# Human Oversight

## AI can find what deserves attention. Humans decide what deserves action.

Prysm is designed around a simple boundary:

**The AI can assist an investigation, but it does not become the investigator.**

Financial intelligence often involves incomplete information, unusual circumstances, complex relationships, and decisions that cannot responsibly be reduced to a model output.

Prysm's AI Engine can process large amounts of financial activity, identify behavioral anomalies, analyze transaction patterns, examine relationships, and surface information that may otherwise be difficult to discover.

But those capabilities are deliberately positioned as **investigative assistance**.

The final interpretation remains with the human investigator.

Prysm therefore does not treat an AI finding as the end of an investigation.

It treats it as the beginning of a better-informed one.

> **“AI finds the signal. Humans determine the meaning.”**

---

# The Human Remains in the Loop

Prysm's workflow is not designed as:

**Data → AI → Automatic Decision**

Instead, the intended flow is:

**Data → Analysis → Evidence → Investigator → Decision**

The AI performs the computational work.

The investigator performs the contextual work.

This distinction allows Prysm to use machine intelligence without giving the machine unrestricted authority over the outcome of an investigation.

The system can say:

**“This account exhibits unusual transaction behavior.”**

The investigator can then ask:

**“Why?”**

**“Compared with what?”**

**“What transactions caused this finding?”**

**“Is there a legitimate explanation?”**

**“Is there additional context that the system does not have?”**

Only after examining those questions should an investigative decision be made.

> **“The AI starts the investigation. It does not finish it.”**

---

# Prysm Does Not Decide Guilt

Prysm is not designed to determine that a person is guilty, fraudulent, or criminal.

Its analytical components identify patterns that may deserve further examination.

This distinction is intentionally maintained throughout the system.

An anomaly is an anomaly.

A relationship is a relationship.

A risk signal is a risk signal.

None of these automatically becomes a verdict.

The investigator is responsible for determining whether the available evidence supports further action.

This prevents the platform from turning a machine-generated observation into an automatic judgment about a person or organization.

> **“A machine-generated signal is not a human verdict.”**

---

# From Detection to Investigation

Prysm's AI Engine can make large-scale financial analysis practical.

Instead of an investigator manually searching through thousands of transactions, the system can identify patterns that deserve attention.

For example, Prysm may surface:

* unusual transaction velocity,
* behavioral deviations,
* foreign-income anomalies,
* structuring-like activity,
* unusual transaction sequences,
* connected entities,
* network-level patterns,
* or other analytical findings.

The purpose of these findings is not to tell the investigator:

**“This is fraud.”**

The purpose is to tell them:

**“This is worth looking at.”**

The investigator can then move from automated detection to human investigation.

This is where the value of human oversight becomes visible.

> **“Detection narrows the search. Investigation establishes the context.”**

---

# Humans Provide the Context AI Cannot See

Financial behavior exists inside a world that is larger than the available dataset.

A model may see an unusually large payment.

An investigator may know that the company just completed a major contract.

A model may see multiple connected accounts.

An investigator may know that the accounts belong to legitimate business partners.

A model may identify a sudden behavioral change.

An investigator may know that the customer's business has recently expanded.

The system can identify the pattern.

The investigator can understand the circumstances surrounding it.

This is why Prysm does not attempt to remove the human from the process.

Human oversight provides the contextual layer that analytical systems cannot reliably guarantee.

> **“The model sees the pattern. The investigator sees the circumstances.”**

---

# Evidence Gives the Human Something to Question

Human oversight is meaningful only when the investigator can actually examine what the AI is doing.

Simply placing a human at the end of an automated pipeline does not create meaningful oversight.

Prysm instead emphasizes evidence-oriented investigation.

When an analytical finding is presented, the investigator should be able to understand what information contributed to that finding and examine the relevant context.

This allows the investigator to challenge the result rather than simply accept it.

The important question becomes:

**“Why did Prysm flag this?”**

rather than:

**“What did Prysm decide?”**

That difference changes the role of AI from authority to assistant.

> **“Human oversight means having enough evidence to question the machine.”**

---

# Investigators Can Disagree With Prysm

A responsible AI system must allow its users to say:

**“I don't agree.”**

Prysm's findings should therefore be treated as analytical outputs that can be investigated, challenged, contextualized, and ultimately accepted or rejected by the responsible human.

An investigator may discover that:

* the behavior has a legitimate explanation,
* the available data is incomplete,
* the relationship has a different meaning,
* the anomaly is expected for that particular business,
* or the model's interpretation does not adequately represent the situation.

The existence of an AI finding does not remove the investigator's ability to disagree with it.

In fact, disagreement is part of the intended workflow.

> **“Trustworthy AI does not demand agreement. It makes disagreement possible.”**

---

# Human Oversight Is Not a Rubber Stamp

Prysm does not define human oversight as simply asking an investigator to approve whatever the AI produces.

A human who cannot question the output is not truly overseeing the system.

Meaningful oversight requires the investigator to have access to enough information to evaluate the finding.

That includes understanding:

**What was detected?**

**What evidence supports it?**

**What context was analyzed?**

**What limitations exist?**

**What relationships were considered?**

**What information may be missing?**

**What alternative explanation could exist?**

The investigator should be able to move from the AI's conclusion back toward the evidence that produced the signal.

> **“Human oversight is not approval. It is informed judgment.”**

---

# AI Recommendations Remain Recommendations

Prysm's intelligence can prioritize what deserves attention.

It can help investigators identify potentially important activity within large datasets.

It can organize complex information.

It can expose relationships.

It can explain analytical findings.

But these outputs remain **recommendations and investigative signals**.

They do not become commands.

The system does not have personal authority over the subject of an investigation.

The investigator decides whether a finding is meaningful, whether additional evidence is required, and what action should follow.

This creates a clear boundary between computational intelligence and institutional decision-making.

> **“AI recommends. Humans decide.”**

---

# Human Oversight Across Prysm's Intelligence Layers

Human oversight is not limited to one model.

Prysm combines several forms of intelligence, including behavioral analysis, anomaly detection, transaction analysis, graph intelligence, GNN-based structural analysis, and RAG-assisted explanation.

Each layer contributes a different perspective.

An anomaly detector may identify unusual behavior.

A graph model may reveal a structural relationship.

Transaction analysis may expose a sequence or velocity pattern.

RAG may help explain the available evidence.

None of these individual components should independently become the final decision-maker.

Instead, their outputs contribute to a broader investigative picture that the human can examine.

> **“Multiple models can expand the picture. Only the investigator decides what the picture means.”**

---

# Human Oversight of Graph Intelligence

Graph intelligence makes it possible for Prysm to see relationships that may be difficult to recognize from individual transactions.

But the existence of a connection does not explain its purpose.

A graph can reveal:

**Person A → Account B → Business C**

The investigator still needs to understand what that connection represents.

It could be:

* legitimate ownership,
* ordinary business activity,
* a shared organization,
* a financial partnership,
* or something requiring further investigation.

The graph provides structure.

The investigator provides interpretation.

This is especially important because network visualization can make relationships appear more significant than they actually are if they are viewed without context.

Prysm therefore treats graph intelligence as a tool for understanding networks rather than an automatic mechanism for assigning blame.

> **“The graph shows who is connected. The investigator determines why it matters.”**

---

# Human Oversight of RAG and AI Explanations

Prysm's RAG layer can make complex analytical results easier to understand by retrieving relevant context and generating explanations.

But the explanation itself remains an AI-generated interpretation.

It should therefore never outrank the underlying evidence.

If an explanation says something that cannot be supported by the available evidence, the investigator should be able to recognize that discrepancy.

The hierarchy remains:

**Evidence first.**

**Analysis second.**

**Explanation third.**

The language model helps communicate intelligence.

It does not become the authority that determines whether the intelligence is true.

> **“An explanation can clarify evidence. It cannot replace it.”**

---

# Humans Can Provide Missing Context

No financial intelligence system has access to every fact about an investigation.

There may be information outside the dataset.

There may be business circumstances unknown to the model.

There may be legitimate explanations that cannot be inferred from transaction history alone.

Human investigators can introduce that missing context into the investigative process.

This means Prysm is not designed around the assumption that:

**“If the AI cannot see it, it does not exist.”**

Instead, the system recognizes that its analytical view is based on the information available to it.

The investigator remains capable of expanding that understanding.

> **“The absence of information is not proof of the absence of an explanation.”**

---

# Humans Remain Accountable

AI should never become an excuse for removing responsibility from decision-makers.

A statement such as:

**“The model flagged it.”**

does not explain what should happen next.

The responsible investigator must still evaluate the finding.

The organization deploying Prysm must still establish appropriate procedures.

The system itself must still communicate its limitations.

Prysm therefore keeps a clear separation between **AI assistance** and **human accountability**.

The machine performs analysis.

The human owns the investigative decision.

> **“Never hide a human decision behind an algorithm.”**

---

# Oversight Through Auditability

Human oversight also depends on being able to reconstruct what happened.

Prysm's architecture includes auditing around sensitive workflows so that investigative actions can be attributable and traceable.

This creates a history around the use of intelligence.

It allows organizations to ask:

**Who accessed the investigation?**

**What operation was performed?**

**When did it happen?**

**What system was involved?**

**What decision or action was recorded?**

This is important because responsible human oversight is not only about what an investigator does today.

It is also about being able to understand and review that process later.

> **“If a decision matters, its history matters.”**

---

# Oversight Through Transparency

Prysm's analytical architecture is designed to preserve information about findings, evidence, model information, limitations, provenance, and component availability.

This gives investigators more than a final result.

It gives them context around the result.

If a component was unavailable, that matters.

If evidence is limited, that matters.

If an analysis is derived from a specific historical window, that matters.

If a finding comes from a particular analytical component, that matters.

Transparency gives the human investigator the information required to determine how much weight a particular finding deserves.

> **“The investigator should know not only what the AI found, but how much trust to place in the finding.”**

---

# Temporal Human Oversight

Human investigation also requires understanding **when** information was available.

Prysm's analytical architecture uses investigation boundaries and historical context so that future information does not improperly influence an earlier analysis.

This means an investigator examining historical activity can understand the behavior within an appropriate time boundary.

The system should not create hindsight-based suspicion simply because later events make earlier activity look different.

Human oversight therefore includes the ability to understand the investigation in its proper temporal context.

> **“Don't let hindsight become evidence.”**

---

# When Prysm Is Uncertain

There are situations where Prysm may not have enough information to produce a strong analytical conclusion.

That is not a failure that should be hidden.

It is a condition the investigator needs to know about.

If the available evidence is limited, the investigator can decide whether additional information is necessary.

If an analytical component is unavailable, that limitation can influence how much weight should be placed on the result.

If the available context does not support a strong conclusion, the investigator can choose not to escalate the finding.

This creates a healthier relationship between AI confidence and human judgment.

> **“When the machine is uncertain, the human gets the final say.”**

---

# The Investigator Is the Final Context Layer

Prysm can bring together information from different analytical perspectives.

But the investigator remains the final context layer.

The investigator can connect the machine's findings with:

* organizational knowledge,
* business context,
* investigative procedures,
* additional evidence,
* external information available through legitimate processes,
* and human reasoning.

This makes the system collaborative rather than autonomous.

Prysm does not attempt to simulate human authority.

It attempts to **augment human capability.**

> **“Prysm does not replace the investigator. It gives the investigator a wider lens.”**

---

# A Deliberate Boundary

The boundary within Prysm can be summarized simply:

### The AI can:

**Detect**

**Analyze**

**Compare**

**Connect**

**Prioritize**

**Explain**

### The human can:

**Question**

**Verify**

**Contextualize**

**Reject**

**Escalate**

**Decide**

That boundary is intentional.

It allows Prysm to take advantage of AI's ability to process complexity while preserving the human responsibility required for consequential financial investigations.

---

# The Prysm Human Oversight Principle

Prysm is not designed to create a world where investigators simply receive decisions from machines.

It is designed to create a world where investigators can examine more information, discover patterns faster, understand complex relationships more clearly, and make decisions with stronger evidence.

The AI handles computational complexity.

The data provides the foundation.

The analytical models provide signals.

The RAG layer helps explain them.

And the investigator remains responsible for deciding what those signals actually mean.

That is the boundary Prysm is built to protect.

> ## **“AI can find the signal. AI can explain the signal. But humans decide what the signal means.”**




# Security & Trust

## Intelligence is only valuable when it can be trusted.

Prysm is designed for financial intelligence, where the information being processed is sensitive and the consequences of mishandling it can be significant.

For that reason, security is not treated as a feature added around the AI.

**Security is part of the architecture through which the AI operates.**

Prysm separates the different responsibilities of the platform so that financial data, analytical processing, relationship intelligence, retrieval, language generation, and user interaction do not all operate with the same level of access.

The objective is simple:

**Protect the data. Control the access. Isolate the intelligence. Preserve the evidence.**

> **“Intelligence without security is just exposure.”**

---

# Security Begins Before the AI

Prysm does not allow the browser to directly become the gateway to every internal intelligence service.

The frontend communicates through the backend, which acts as a controlled boundary between the user-facing application and internal services.

This gives Prysm a central place to handle important responsibilities such as:

* authentication,
* authorization,
* request validation,
* trusted investigation context,
* service orchestration,
* persistence,
* and auditing.

The AI Engine and RAG services therefore operate behind the application's trusted backend boundary rather than being treated as public endpoints.

This architectural separation reduces the number of places where sensitive intelligence can be directly exposed.

> **“The AI should not be directly exposed just because it can be reached.”**

---

# Authentication Is Only the Beginning

Knowing who a user is does not automatically mean they should be able to access everything.

Prysm separates **authentication** from **authorization**.

Authentication answers:

**“Who are you?”**

Authorization asks:

**“What are you allowed to access?”**

This distinction becomes particularly important in financial investigations.

A user may be authenticated but still have no permission to access a particular investigation.

A user may have access to investigations but not to every type of sensitive information.

A system component may need access to analytical data without needing access to the entire operational database.

Prysm's architecture therefore treats access as a controlled decision rather than assuming that identity alone provides unlimited access.

> **“Knowing who you are does not mean knowing everything you are allowed to see.”**

---

# Authorization Before Intelligence

Prysm places authorization around sensitive investigation workflows rather than treating AI access as inherently trusted.

Before private investigation context is provided to intelligence services, the system should establish that the requesting user is permitted to access that context.

This is particularly important for RAG.

A language model should not receive private investigation information simply because someone can ask a question.

The question must first belong to an authorized investigative context.

Only then can the relevant information be constructed for the intelligence layer.

> **“Permission comes before context. Context comes before intelligence.”**

---

# The Backend as a Trust Boundary

The Prysm backend serves as more than a collection of API endpoints.

It acts as an orchestration and trust boundary between the user and the internal intelligence architecture.

The frontend should not need to know how the AI Engine performs its analysis.

The AI Engine should not need to determine whether a browser user is authorized.

The RAG service should not independently decide whether a user is allowed to access a private investigation.

Each responsibility belongs to the appropriate layer.

This separation reduces the chance that one component becomes responsible for security decisions that should be made elsewhere.

> **“Every layer should enforce the boundary it is responsible for.”**

---

# Protecting the Source of Truth

Prysm separates operational data from analytical intelligence.

The operational database remains the source of truth for the underlying financial information.

Analytical services consume that information to generate derived intelligence.

This distinction provides an important security and integrity boundary.

If an AI model generates an incorrect interpretation, that interpretation does not become the underlying financial record.

The analytical layer can be wrong without rewriting the source of truth.

This makes it possible to improve, replace, retrain, or evaluate analytical components without treating their outputs as permanent replacements for the original information.

> **“The intelligence layer can evolve. The source of truth remains protected.”**

---

# Controlled Data Exposure

Prysm does not need to expose the entire financial system to every operation.

Different tasks require different information.

An investigation may require a defined set of transactions.

A graph analysis may require a specific relationship neighborhood.

A behavioral analysis may require a historical window.

A RAG response may require only the context relevant to a particular investigation.

By controlling the scope of information passed between components, Prysm reduces unnecessary exposure.

This is not only a privacy principle.

It is also a security principle.

Every additional piece of data exposed to a component creates another piece of information that must be protected.

> **“Reduce the data surface. Reduce the risk surface.”**

---

# Protecting the AI Layer

AI services should not automatically be treated as trusted simply because they are internal.

The AI Engine processes sensitive financial intelligence.

The RAG system can work with investigation-specific context.

Language models can transform that context into human-readable explanations.

Each of these capabilities creates a potential exposure point.

Prysm therefore separates these services and places them behind controlled application boundaries.

The goal is to prevent the AI layer from becoming an unrestricted doorway into the financial system.

> **“Powerful intelligence requires equally deliberate boundaries.”**

---

# Secure RAG

RAG creates a particularly important security responsibility.

The system must not confuse:

**“The model can answer this question.”**

with:

**“The user is allowed to know the answer.”**

Prysm therefore treats authorization as a prerequisite for private investigative context.

An authorized investigator can receive context associated with an investigation they are permitted to access.

An unauthorized request should not gain access simply by asking the language model a different way.

The RAG system is therefore not intended to become a backdoor into private financial information.

> **“RAG should retrieve what the user is authorized to know — not everything the system knows.”**

---

# Public and Private Intelligence

Prysm distinguishes between general interaction and authorized investigation workflows.

Public or general interactions should not automatically inherit private investigation context.

Authorized investigation conversations can operate within a specific investigative scope.

This separation prevents a general AI conversation from accidentally becoming a channel into private financial intelligence.

The principle is straightforward:

**Public questions remain public.**

**Private investigations remain protected.**

> **“A public question should never become a private data leak.”**

---

# Data Does Not Travel Without Purpose

Within Prysm, information moves between components because a particular operation requires it.

The database provides information to analytical systems.

Analytical systems produce findings.

Relevant context can be provided to the explanation layer.

The backend orchestrates these interactions.

This creates a purpose-driven flow of information rather than indiscriminate movement of the entire dataset.

Every transfer should have a reason.

Every recipient should have a role.

Every access boundary should have a purpose.

> **“Data should travel because it has a purpose, not because it has a path.”**

---

# Secrets Stay Out of the Interface

Sensitive credentials, API keys, database credentials, and service configuration should not be treated as frontend information.

The browser is an untrusted environment relative to internal service credentials.

Prysm therefore keeps sensitive service configuration within the backend/server-side environment rather than exposing those secrets to client-side code.

This prevents the frontend from becoming a source of credential leakage.

> **“What the browser does not need to know should never be placed in the browser.”**

---

# Validation at the Boundary

Security is not only about authentication.

Requests entering the system also need to be treated as untrusted input.

Prysm's backend boundary provides a place where requests can be validated before they reach internal services.

This is important because an attacker should not be able to manipulate an API request into changing the intended scope of an investigation or accessing information that was never meant to be returned.

The system should validate what is being requested before deciding what information can be provided.

> **“Never trust the request simply because it reached the server.”**

---

# Auditability Creates Accountability

Security becomes much stronger when sensitive actions leave a trace.

Prysm's architecture includes audit events around sensitive workflows such as investigation analysis, authorized chat, and ingestion.

This provides a record of important interactions with the platform.

The purpose is not to monitor people unnecessarily.

The purpose is to make sensitive operations accountable.

When something important happens, the system should be capable of answering:

**Who performed it?**

**What happened?**

**Which resource was involved?**

**When did it happen?**

**What decision or action was recorded?**

> **“If access matters, access should be traceable.”**

---

# Security Through Separation

Prysm deliberately separates different types of responsibility:

**PostgreSQL**
Operational financial data and application state.

**AI Engine**
Financial and behavioral analysis.

**Graph / GNN intelligence**
Relationship and structural analysis.

**RAG**
Retrieval and evidence-grounded explanation.

**Backend**
Authentication, authorization, orchestration, persistence, and trust boundaries.

**Frontend**
Human interaction and visualization.

This separation is more than software organization.

It limits how much authority any individual component needs.

A visualization layer does not need database ownership.

An LLM does not need unrestricted database access.

A graph model does not need to decide authorization.

An analytical model does not need to manage user identity.

> **“A secure system gives each component the power it needs — and no more.”**

---

# Security and Data Integrity Work Together

Security is often described as protecting information from unauthorized access.

For Prysm, it also means protecting the **integrity of the information and the processes around it**.

If unauthorized users can modify investigative information, the system cannot be trusted.

If analytical outputs can silently overwrite financial records, the system cannot be trusted.

If AI-generated explanations can be mistaken for source data, the system cannot be trusted.

If sensitive actions cannot be traced, the system cannot be fully trusted.

Trust therefore comes from several properties working together:

**Confidentiality.**

**Integrity.**

**Controlled access.**

**Traceability.**

**Separation of responsibilities.**

**Transparency.**

---

# Trust Does Not Mean Blind Belief

Prysm does not ask investigators to trust an AI simply because it is called artificial intelligence.

Trust should come from the system's behavior.

An investigator should be able to understand:

* where information came from,
* what analytical component produced a finding,
* what evidence supports it,
* what context was considered,
* what limitations exist,
* and what actions occurred during the investigation.

This creates **verifiable trust** rather than blind trust.

The objective is not:

**“Trust Prysm because Prysm is AI.”**

It is:

**“Trust the process because the process can be examined.”**

> **“Trust should be earned by transparency, not requested by authority.”**

---

# Security Without Destroying Usability

Security should protect the investigation without making legitimate investigation impossible.

Prysm therefore aims for controlled access rather than indiscriminate restriction.

An authorized investigator should be able to access the information required to perform their work.

At the same time, unrelated users and services should not automatically receive that same access.

The objective is not to create barriers for the sake of barriers.

It is to make access proportional to responsibility.

> **“The right person should have the right information for the right investigation.”**

---

# Trust Across the Investigation Lifecycle

Trust should exist throughout the entire Prysm workflow.

### Before analysis

The user must be authenticated and authorized.

### During analysis

The system works with controlled investigative context.

### During intelligence generation

Analytical components operate within their defined responsibilities.

### During explanation

RAG and language generation remain grounded in authorized context.

### During investigation

Humans can examine and challenge findings.

### After the investigation

Important actions remain auditable and traceable.

Security is therefore not one checkpoint.

It is a continuous boundary surrounding the entire investigative lifecycle.

> **“Security is not a door. It is the architecture around the entire journey.”**

---

# Trust Through Clear Boundaries

One of the strongest security principles within Prysm is knowing what each component **should not** do.

The frontend should not directly control internal intelligence services.

The AI Engine should not become the source of truth.

The LLM should not invent financial evidence.

RAG should not bypass authorization.

A model should not determine user permissions.

A derived analytical finding should not silently rewrite operational data.

These boundaries reduce the amount of trust that must be placed in any single component.

> **“Trust the system by limiting what any one part of it is allowed to do.”**

---

# When a Component Fails

A trustworthy system must also account for failure.

AI services can become unavailable.

Models can produce incomplete results.

External generation services can fail.

Data sources can become temporarily inaccessible.

Prysm's architecture recognizes component availability as part of the intelligence context rather than assuming that every component is always operational.

When an analytical capability is unavailable, the system should not pretend that it ran.

When an external language model is unavailable, the platform can use its locally grounded fallback behavior rather than treating failure as permission to fabricate an answer.

> **“A secure system does not hide failure. It contains it.”**

---

# Security Is Part of the Intelligence

Prysm's security architecture ultimately supports the same objective as its AI architecture:

**better financial understanding without uncontrolled exposure.**

The platform can analyze complex financial behavior while keeping access controlled.

It can examine relationships while preserving authorization boundaries.

It can use AI explanations while keeping the language model separate from the source of truth.

It can provide investigators with powerful intelligence while maintaining a traceable path through the system.

This is what allows security and intelligence to coexist.

> **“The goal is not to choose between intelligence and security. The goal is to architect them together.”**

---

# Our Security & Trust Principle

Prysm does not claim that a system becomes trustworthy simply because it has authentication, authorization, or encryption.

Trust is created through the combination of many deliberate boundaries.

The data has a source of truth.

The user has an identity.

The identity has permissions.

The investigation has a scope.

The AI has a defined role.

The RAG system has controlled context.

The backend has responsibility for orchestration and access.

Sensitive actions can be audited.

And human investigators remain able to examine what the system produces.

Together, these boundaries create a system where intelligence can operate without being given unlimited authority.

> ## **“Protect the data. Control the access. Preserve the evidence. Earn the trust.”**


