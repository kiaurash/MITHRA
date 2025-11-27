# ARCHE Paper RLT Extraction - Working Document

## Introduction Text (Clean)

**Sentence 1:** LLMs are increasingly applied in scientific domains, from assisting literature reviews and hypothesis generation to aiding in experimental design.

**Sentence 2:** Although these advances suggest the potential of LLMs to accelerate scientific discovery, it is poorly understood how well these models understand and emulate human reasoning.

**Sentence 3:** In particular, their ability to follow and generate structured paradigm-based reasoning is uncertain, raising concerns about the trustworthiness of LLM-driven scientific workflows.

**Sentence 4:** Building on Charles S. Peirce's taxonomy, which holds that all valid reasoning is deductive, inductive, abductive, or some combination thereof, we argue that the ability to understand and appropriately apply these elementary paradigms of reasoning is essential for LLMs to perform trustworthy scientific reasoning.

**Sentence 5:** Human scientists often employ a mixed inferential strategy to navigate vast bodies of evidence and competing claims in order to generate novel insights.

**Sentence 6:** Such discoveries are not isolated leaps, but chains of reasoning steps that traverse multiple paradigms.

**Sentence 7:** This process involves latent reasoning chains composed of implicit, unspoken steps that connect existing knowledge to new insights.

**Sentence 8:** However, existing benchmarks fail to evaluate whether LLMs can (i) recognize the three reasoning paradigms from complex argument, (ii) incorporate them into coherent reasoning chains, and (iii) ground each step in verifiable textual evidence.

**Sentence 9:** To address limitations (i) and (ii), we propose a novel task, Latent Reasoning Chain Extraction (ARCHE), designed to recognize the underlying reasoning behind scientific claims.

**Sentence 10:** ARCHE leverages an LLM to extract fine-grained reasoning steps from a paper's introduction paragraph and classify each step as deductive, inductive, or abductive reasoning.

**Sentence 11:** These steps are then assembled into a structured Reasoning Logic Tree (RLT), where nodes correspond to individual premise or conclusion sentences, and labeled edges link each set of premise nodes to the corresponding conclusion node, indicating the associated inference type.

**Sentence 12:** By (i) recognizing distinct reasoning paradigms and (ii) assembling them into an RLT, ARCHE delivers a faithful, structured representation of complex scientific arguments.

**Sentence 13:** To (iii) ground the reasoning steps in real tasks, we introduce ARCHE Bench, a benchmark derived from 70 peer-reviewed Nature Communication articles.

**Sentence 14:** For each paper, we provide its introduction along with the relevant background viewpoints.

**Sentence 15:** We also propose two complementary metrics that capture different aspects of RLT: (a) EC, which measures proportion of key scientific entities of each paper that appear in the predicted RLT, reflecting how comprehensively the model captures the core contents; and (b) REA, which assesses the accuracy of each individual inference step in the reasoning chain, using an LLM-based judge to verify whether the conclusion logically follows from its premises given the labeled inference type.

**Sentence 16:** While EC ensures that no critical pieces of the core idea are omitted, REA directly evaluates logical validity at the step level.

**Sentence 17:** We perform zero-shot evaluations on 10 state-of-the-art LLMs, revealing that even the best models struggle to exceed an accuracy of 50%, indicating their limited ability to recognize and properly formalize latent reasoning chains via standard paradigms.

**Sentence 18:** Furthermore, we observe a trade-off between EC and REA: models that achieve higher EC often do so at the cost of lower REA, and vice versa.

---

## Citations Referenced

[Note: In a full implementation, we would fetch abstracts via Semantic Scholar API. For this demo, I'll use known context about these papers.]

- wang2406autosurvey, zhu2025deepreview (literature reviews)
- gottweis2025towards, xiong2024improving (hypothesis generation)
- huang2024crispr, li2025can (experimental design)
- bai2025intern (scientific discovery)
- peirce1868some (Peirce's taxonomy)
- Yang2024Logical, hu2025survey (existing benchmarks)

---

## Viewpoint Extraction (Next Step)

Now extracting fine-grained viewpoints from each sentence...
