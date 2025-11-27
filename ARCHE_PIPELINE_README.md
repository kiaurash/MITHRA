# ARCHE RLT Extraction Pipeline

Implementation and documentation of the ARCHE (Latent Reasoning Chain Extraction) methodology for extracting structured reasoning trees from scientific papers.

## What This Is

This branch contains a complete implementation of the ARCHE pipeline from the paper "ARCHE: A Novel Task to Evaluate LLMs on Latent Reasoning Chain Extraction" (arXiv:2511.12485).

## Key Files

All ARCHE work is located in `your_workspace/`:

- **arche_pipeline_design.md** - Complete pipeline architecture (5 stages, implementation details)
- **arche_prompts.md** - Full ARCHE prompts extracted from paper appendix (verbatim)
- **validate_rlt.py** - Python tool for RLT structural validation
- **arche_paper_analysis.md** - Working document with viewpoint extraction
- **arche_paper_rlt*.dot** - Multiple RLT iterations (initial + corrections)
- **arche_rlt_demo.md** - Demo results and lessons learned

## What We Accomplished

✅ Extracted complete ARCHE methodology from research paper
✅ Obtained full prompts from LaTeX source (Appendix D)
✅ Built structural validator following ARCHE spec
✅ Manually extracted RLT from ARCHE paper itself (meta-demo)
✅ Validated with automated checker (found edge pairing violations)
✅ Demonstrated 2-stage repair process

## Pipeline Overview

```
Scientific Paper
    ↓
[1. Viewpoint Extraction] ← GPT-4o, Semantic Scholar API
    ↓
[2. RLT Generation Stage 1] ← Primary prompt with reasoning paradigms
    ↓
[3. Structural Validation] ← Automated checker (networkx)
    ↓
[4. RLT Repair Stage 2] ← Repair prompt (if issues found)
    ↓
[5. Evaluation] ← EC (coverage) + REA (accuracy) metrics
    ↓
Reasoning Logic Tree (DOT format)
```

## Key Concepts

### Reasoning Paradigms (Peirce)
- **Deduction**: General rule + specific case → conclusion
- **Induction**: Multiple cases → generalized pattern
- **Abduction**: Phenomenon + knowledge → hypothesis

### RLT Structure
- **Nodes**: Viewpoints with (x,y,z) coordinates for source traceability
- **Edges**: 6 types (deduction-rule/case, induction-common/case, abduction-phenomenon/knowledge)
- **Constraint**: Each conclusion requires exactly 2 paired edges
- **Format**: Single-rooted DAG (directed acyclic graph)

### Coordinate System
- `(x,0,0)`: Sentence x from paper
- `(x,y,0)`: Viewpoint y within sentence x
- `(x,y,z)`: Viewpoint z from reference y cited in sentence x
- `(0,0,0)`: Implicit knowledge/intermediate reasoning

## Next Steps: RLT → FOL → Symbolic Reasoning

See detailed recommendations below for building the complete pipeline.

---

## Suggested Next Steps

Based on our work, here's the recommended path forward for building an RLT→FOL→Symbolic Reasoning system:

### Phase 1: Automated RLT Extraction (2-3 weeks)

**Goal**: Build Python pipeline that automatically extracts RLTs from papers

**Components**:
1. **PDF/Text Preprocessor**
   - Extract introduction sections
   - Parse citations
   - Sentence segmentation

2. **Viewpoint Extractor**
   - LLM-based (GPT-4o or Claude)
   - Semantic Scholar API integration
   - Coordinate assignment

3. **RLT Generator**
   - Implement 2-stage process (generation + repair)
   - Use exact ARCHE prompts
   - DOT graph output

4. **Validator**
   - Enhance existing `validate_rlt.py`
   - Add visualization (networkx → graphviz)
   - Repair loop automation

**Deliverable**: `arche_extractor.py` that takes paper → outputs RLT

### Phase 2: RLT → FOL Translation (2-3 weeks)

**Goal**: Convert RLT structures to First-Order Logic formulas

**Key Challenges**:
1. **Node → Proposition Translation**
   - NL viewpoint text → FOL predicates
   - Entity extraction & typing
   - Relation identification

2. **Edge → Inference Rule Translation**
   - **Deduction**: Direct modus ponens
     ```
     deduction-rule: ∀x (P(x) → Q(x))
     deduction-case: P(a)
     → Q(a)
     ```

   - **Induction**: Universal generalization (requires special handling)
     ```
     induction-cases: P(a), P(b), P(c)
     induction-common: pattern
     → ∀x (P(x)) [with confidence/probability]
     ```

   - **Abduction**: Hypothetical reasoning (non-monotonic)
     ```
     abduction-phenomenon: Q(a)
     abduction-knowledge: ∀x (P(x) → Q(x))
     → P(a) [best explanation, defeasible]
     ```

3. **Special Considerations**:
   - Induction doesn't map cleanly to FOL (needs probabilistic extension)
   - Abduction requires non-monotonic logic or answer set programming
   - Intermediate nodes create chained inference rules

**Approach Options**:

**Option A: Pure FOL (Conservative)**
- Only translate deductive steps
- Mark inductive/abductive steps as "assumptions"
- Pro: Clean, provable
- Con: Loses reasoning type information

**Option B: Extended Logic (Recommended)**
- Use Prolog or Answer Set Programming (Clingo)
- Support non-monotonic reasoning
- Probabilistic annotations for induction
- Pro: Preserves full reasoning structure
- Con: More complex infrastructure

**Option C: Hybrid (Pragmatic)**
- Deduction → FOL inference rules
- Induction → Annotated facts with confidence
- Abduction → Hypothetical facts (tagged)
- Pro: Practical, works with standard reasoners
- Con: Some semantic loss

**Deliverable**: `rlt_to_fol.py` that converts DOT → FOL/Prolog

### Phase 3: Symbolic Reasoning Integration (1-2 weeks)

**Goal**: Use extracted FOL in automated reasoners

**Toolchain Options**:

1. **Prover9/Mace4** (Theorem proving)
   - Input: FOL clauses
   - Output: Proofs, counterexamples
   - Use case: Verify logical consistency

2. **Vampire** (ATP - Automated Theorem Proving)
   - Fast, competition-grade
   - Handles quantifiers well
   - Good for complex proofs

3. **Prolog (SWI-Prolog)** (Logic programming)
   - Query-based reasoning
   - Natural for scientific Q&A
   - Easy integration with Python

4. **Clingo** (Answer Set Programming)
   - Best for abduction
   - Non-monotonic reasoning
   - Handles defaults, preferences

**Integration Architecture**:
```
Paper → [ARCHE] → RLT → [Translator] → FOL → [Reasoner] → Inferences
                                               ↓
                                          [Query Engine]
                                               ↓
                                          Answers/Proofs
```

**Deliverable**: End-to-end demo notebook

### Phase 4: Applications & Validation (Ongoing)

**Use Cases**:
1. **Scientific Q&A**: Query reasoning chains
2. **Consistency Checking**: Detect logical conflicts
3. **Hypothesis Generation**: Use abductive reasoning
4. **Argument Mining**: Extract claim-evidence structures
5. **Knowledge Graph Construction**: Build from reasoning chains

**Validation**:
- Test on ARCHE Bench (70 papers)
- Compare inferences to human expert annotations
- Measure coverage (what % of RLT translates to FOL)
- Evaluate reasoning quality (valid inferences)

---

## Recommended Tech Stack

```python
# Core dependencies
- Python 3.10+
- networkx (graph manipulation)
- pydot/graphviz (DOT parsing/visualization)
- anthropic/openai (LLM APIs)
- requests (Semantic Scholar API)

# FOL Translation
- nltk/spacy (NLP for entity extraction)
- sympy.logic (FOL representation - optional)
- pyswip (Prolog interface)
- clingo (ASP solver)

# Reasoning
- SWI-Prolog (logic programming)
- Vampire (via CLI)
- Z3 (SMT solver - for typed FOL)
```

---

## Quick Start (When Resuming)

```bash
# Switch to this branch
git checkout arche-rlt-pipeline

# Review documentation
cd your_workspace
cat arche_pipeline_design.md  # Full methodology
cat arche_prompts.md           # Exact prompts to use

# Test validator
python validate_rlt.py arche_paper_rlt_final.dot

# Start Phase 1 implementation
# Create: src/arche_extractor/
#   - preprocessor.py
#   - viewpoint_extractor.py
#   - rlt_generator.py
#   - validator.py
#   - main.py
```

---

## Related Work to Explore

1. **PrisM** (Module extraction) - Could preprocess ontologies before RLT extraction
2. **NL→FOL tools** - Flan-T5-XXL fine-tuned (70% accuracy)
3. **Symbolic AI + LLMs** - Papers on neuro-symbolic integration
4. **Scientific argument mining** - Datasets and benchmarks

---

## Contact & Collaboration

This work was done as part of the Bootcamp25 program exploring AI-powered scientific reasoning systems.

For questions or collaboration: See your_workspace/arche_rlt_demo.md for lessons learned.
