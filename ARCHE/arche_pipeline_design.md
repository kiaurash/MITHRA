# ARCHE RLT Generation Pipeline - Complete Design

Based on the ARCHE paper (arXiv:2511.12485v1), here's the complete pipeline for extracting Reasoning Logic Trees from scientific papers.

## Pipeline Overview

```
Scientific Paper (PDF/Text)
    ↓
[1. Viewpoint Extraction]
    ↓
Structured Viewpoints with Coordinates
    ↓
[2. RLT Generation - Stage 1]
    ↓
Initial DOT Graph
    ↓
[3. Structural Validation]
    ↓
[4. RLT Repair - Stage 2] (if needed)
    ↓
Final Validated RLT
    ↓
[5. Evaluation] (optional)
```

---

## Stage 1: Viewpoint Extraction

### Input
- Paper introduction section (sentences)
- Cited references (abstracts via Semantic Scholar API)

### Process
1. Parse introduction into individual sentences
2. Extract fine-grained viewpoints from each sentence using GPT-4o
3. For each citation, extract viewpoints from abstract
4. Assign coordinates to each viewpoint:
   - `(x,0,0)`: x-th sentence from introduction
   - `(x,y,0)`: y-th viewpoint within x-th sentence
   - `(x,y,z)`: z-th viewpoint from y-th reference cited in x-th sentence
   - `(0,0,0)`: Implicit knowledge/intermediate reasoning

### Output
Structured viewpoint list with source coordinates

### Example

**Sentence 1:** "Seawater is a natural carbon sink of net ~0.4 giga-ton CO₂ per year..."

**Extracted Viewpoints:**
- `(1,1,0)`: Seawater is a natural carbon sink of net approximately 0.4 giga-ton CO₂ per year
- `(1,2,0)`: Seawater potentially supports trillion-ton-scale CO₂ capture via engineering solutions

**Reference [3] viewpoints:**
- `(1,1,1)`: Electrochemical CO₂ capture technologies are gaining attention
- `(1,1,2)`: These methods can address decentralized emissions from ocean and atmosphere

---

## Stage 2: RLT Generation (Primary)

### Input
- Complete introduction section
- Extracted viewpoints with coordinates
- Cited reference viewpoints

### Prompt Structure

See `ARCHE_PRIMARY_PROMPT.txt` for full prompt. Key instructions:

**Goal:** Build a single-rooted reasoning tree representing the logical path to the paper's core research idea

**Node Format:**
```
node_id [label="(x,y,z) transcription"];
```

**Edge Types (exactly 6):**
- `deduction-rule`
- `deduction-case`
- `abduction-phenomenon`
- `abduction-knowledge`
- `induction-case`
- `induction-common`

**Critical Constraint - Edge Pairing:**
Every conclusion node MUST have exactly TWO incoming edges of a paired type:
- Deduction: `deduction-rule` + `deduction-case` → conclusion
- Induction: `induction-common` + `induction-case` → conclusion
- Abduction: `abduction-knowledge` + `abduction-phenomenon` → conclusion

**Reasoning Type Definitions:**

1. **Deduction (General → Specific)**
   - Rule node: "If [condition], then [consequence]"
   - Case node: "Currently [specific situation]"
   - Conclusion: "Therefore [consequence applies]"

2. **Induction (Specific → General)**
   - Case nodes: Multiple specific observations
   - Common node: Abstracted pattern across cases
   - Conclusion: Generalized rule

3. **Abduction (Hypothesis Formation)**
   - Phenomenon node: Observation needing explanation
   - Knowledge node: Existing mechanism/theory
   - Conclusion: Best explanatory hypothesis

**Structure Requirements:**
- Single root node (no outgoing edges)
- No isolated/disconnected nodes
- All nodes converge to final research idea
- Multi-hop reasoning requires intermediate `(0,0,0)` nodes
- Aim for 70%+ coverage of original sentences

**Output Format:** DOT graph syntax in code block

---

## Stage 3: Structural Validation

Automated validator checks:

### Structural Integrity
- ✓ Single root node exists
- ✓ No isolated nodes
- ✓ No cycles (DAG structure)

### Edge Type Compliance
- ✓ All edges use one of 6 valid types
- ✓ Correct edge pairing (each conclusion has exactly 2 paired edges)

### Node Format
- ✓ Coordinates follow `(x,y,z)` format
- ✓ Valid coordinate values

**Pass:** Proceed to final output
**Fail:** Trigger Stage 4 repair

---

## Stage 4: RLT Repair (Structural Correction)

### Triggered When
- Validation detects structural errors
- Statistics show 52.9%-82.9% of papers require repair (model-dependent)

### Repair Prompt

Includes:
1. Original DOT graph with issues
2. List of detected problems
3. Complete format requirements (repeated)
4. Specific fixes required
5. Original paper content for reference

**Key Instruction:**
"Fix ALL structural problems while preserving content and maintaining quality-coverage balance"

**Specific Fixes:**
- Ensure exactly one root node
- Connect all isolated nodes to main chain
- Enforce proper edge pairing
- Fix node label formatting
- Preserve all reasoning transcriptions

### Output
Corrected DOT graph

---

## Stage 5: Evaluation (Optional)

### Metric 1: Entity Coverage (EC)

**Measures:** How comprehensively the RLT captures core concepts

**Process:**
1. Extract gold-standard core entities from paper's research idea (using o3)
2. Parse generated graph, identify main connected component
3. Extract entities from original source content of each node (via coordinates)
4. Calculate percentage of gold entities found in graph

```
EC = (Covered Core Entities / Total Core Entities) × 100%
```

### Metric 2: Reasoning Edge Accuracy (REA)

**Measures:** Logical validity of inference steps

**Process:**
1. **Structural filtering:** Identify format errors (invalid edge pairing)
2. **Semantic validation:** For each structurally valid step:
   - Send to 3 LLM judges (o3, Claude-Sonnet-4, Gemini-2.5-Pro)
   - Each judges if conclusion follows from premises
   - Majority vote determines correctness (ties → correct)
3. Calculate accuracy

```
REA = (Correct Steps / Total Attempted Steps) × 100%
```

**Human calibration:** 3-model voting achieves 88%+ agreement with human judgment

---

## Implementation Requirements

### Dependencies
- Python 3.8+
- LLM API access (OpenAI, Anthropic, Google)
- Libraries: `networkx`, `pydot`, `requests`, `pandas`
- Semantic Scholar API (for reference abstracts)

### LLM Models Used
- **Viewpoint extraction:** GPT-4o
- **RLT generation:** Any frontier model (Claude Opus/Sonnet-4, GPT-4o, Gemini-2.5-Pro, DeepSeek-R1, etc.)
- **Evaluation:** o3, Claude-Sonnet-4, Gemini-2.5-Pro (voting panel)

---

## Example Workflow

```python
# 1. Extract viewpoints
paper_intro = load_introduction(paper_pdf)
sentences = parse_sentences(paper_intro)
viewpoints = []

for idx, sentence in enumerate(sentences):
    # Extract viewpoints from sentence
    sent_viewpoints = gpt4o.extract_viewpoints(sentence)
    for v_idx, viewpoint in enumerate(sent_viewpoints):
        viewpoints.append({
            'coord': (idx+1, v_idx+1, 0),
            'text': viewpoint
        })

    # Extract viewpoints from cited references
    citations = extract_citations(sentence)
    for ref_idx, citation in enumerate(citations):
        abstract = semantic_scholar.get_abstract(citation)
        ref_viewpoints = gpt4o.extract_viewpoints(abstract)
        for z_idx, ref_vp in enumerate(ref_viewpoints):
            viewpoints.append({
                'coord': (idx+1, ref_idx+1, z_idx+1),
                'text': ref_vp
            })

# 2. Generate RLT (Stage 1)
prompt = build_arche_prompt(paper_intro, viewpoints)
rlt_dot = llm.generate(prompt)

# 3. Validate structure
issues = validate_rlt(rlt_dot)

# 4. Repair if needed (Stage 2)
if issues:
    repair_prompt = build_repair_prompt(rlt_dot, issues, paper_intro, viewpoints)
    rlt_dot = llm.generate(repair_prompt)

# 5. Parse final RLT
graph = parse_dot(rlt_dot)

# 6. Evaluate (optional)
ec_score = calculate_entity_coverage(graph, paper_intro)
rea_score = calculate_reasoning_accuracy(graph, llm_panel)

print(f"EC: {ec_score}%, REA: {rea_score}%")
```

---

## Key Insights for Implementation

### Critical Success Factors

1. **Coordinate System:** The `(x,y,z)` system is crucial for grounding and traceability
2. **Edge Pairing:** Strict enforcement prevents invalid reasoning patterns
3. **Two-Stage Process:** Repair loop significantly improves structural quality
4. **Grounded Evaluation:** Always extract from original source text, not paraphrased labels
5. **Multi-hop Decomposition:** Complex reasoning requires intermediate nodes

### Common Failure Modes

- **Multiple roots:** Models struggle to converge all reasoning to single idea
- **Isolated nodes:** ~60-80% of first attempts have disconnected reasoning
- **Edge pairing violations:** Models forget to provide both paired edges
- **Coverage vs. precision tradeoff:** High coverage often sacrifices reasoning validity

### Model Performance

**Best performers (REA):**
- Gemini-2.5-Pro-Thinking: 41.4%
- DeepSeek-R1: 39.9%

**Best for coverage (EC):**
- Claude-Opus-4-Thinking: 69.7%
- Gemini-2.5-Pro-Thinking: 64.4%

**Lowest Stage 2 trigger (best structural quality):**
- DeepSeek-R1: 52.9%
- Grok 4: 55.7%
- Claude-Sonnet-4: 58.6%

---

## Application to FOL Extraction

### How ARCHE Enables FOL Conversion

1. **Structured Decomposition:** RLT breaks complex arguments into elementary steps
2. **Reasoning Type Labels:** Each edge identifies inference mode (deduction/induction/abduction)
3. **Logical Dependencies:** DAG structure maps premise-conclusion relationships
4. **Source Grounding:** Coordinates enable tracing to original text

### RLT → FOL Pipeline

```
RLT (DOT Graph)
    ↓
[Extract Nodes & Edges]
    ↓
For each node:
  - Extract proposition from viewpoint text
  - Convert to FOL predicate/formula
    ↓
For each edge pair:
  - If deduction: Generate inference rule
  - If induction: Generate universal quantifier
  - If abduction: Generate hypothesis formula
    ↓
First-Order Logic Knowledge Base
    ↓
[Symbolic Reasoner] (Prover9, Vampire, etc.)
```

### Example Translation

**RLT Node:**
```dot
rule [label="(0,0,0) If MOFs have high porosity, then they are suitable for CO₂ capture"];
case [label="(3,1,0) MOFs have high porosity"];
conclusion [label="(0,0,0) MOFs are suitable for CO₂ capture"];

rule -> conclusion [label="deduction-rule"];
case -> conclusion [label="deduction-case"];
```

**FOL Translation:**
```prolog
% Deduction rule (universal quantifier)
∀x (HighPorosity(x) ∧ MOF(x) → SuitableForCO2Capture(x))

% Deduction case (fact)
MOF(mof_1) ∧ HighPorosity(mof_1)

% Conclusion (derived)
SuitableForCO2Capture(mof_1)  % follows by modus ponens
```

---

## Next Steps for Building Your Own Pipeline

1. **Start Simple:** Implement viewpoint extraction first
2. **Use Existing Prompts:** Adapt the exact prompts from appendix
3. **Build Validator:** Structural checks are straightforward (networkx)
4. **Test Iteratively:** Start with 1-2 papers, debug edge pairing
5. **Add Repair Loop:** Significantly improves results
6. **Evaluate:** Implement EC/REA metrics for quality control

---

## References

- **Paper:** ARCHE: A Novel Task to Evaluate LLMs on Latent Reasoning Chain Extraction
- **ArXiv:** https://arxiv.org/abs/2511.12485
- **Repository:** https://github.com/Linsonng/ARCHEBenchmark
- **Dataset:** 70 Nature Communications papers with ~38K viewpoints
