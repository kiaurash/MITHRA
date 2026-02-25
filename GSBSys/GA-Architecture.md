# GSBsys Genetic Algorithm Architecture

## Complete GA Component Specification

### 1. Chromosome Encoding

GSBsys uses a **hybrid discrete-continuous encoding** representing a complete trading system:

```
Chromosome = {
  // Discrete genes
  Indicator_IDs: [3, 17, 22]           // 2-5 selected from pool of 37
  SecondaryFilter: "GeneticAlgorithm"  // or fixed rule

  // Continuous genes
  Indicator_Params: {
    Indicator_3: {period: 1561, param2: 0.75},
    Indicator_17: {period: 892, param2: 1.2},
    Indicator_22: {period: 2103, param2: 0.33}
  }

  Weights: [1.2, -0.5, 1.8]            // Range: -1 to 2
  EntryLevel: 450                       // Threshold for signal
  StopLoss: 800                         // In currency units
  ProfitTarget: 1200                    // In currency units
}
```

**Encoding Properties:**
- **Search Space Size:** Combinatorially massive
  - Indicator selection: C(37, k) where k = 2-5
  - Each indicator has 2-3 continuous parameters
  - Weights are continuous
  - Entry/exit levels are continuous
- **Estimated degrees of freedom:** 15-30 per chromosome
- **Total search space:** ~10^20 combinations (20M samples represent tiny fraction)

**Not Documented:**
- Exact bit/float representation
- Parameter bounds for each indicator
- Constraint handling (e.g., StopLoss < ProfitTarget enforcement)

---

### 2. Population Initialization

**Method:** Random seed-based initialization

```
FOR restart = 1 TO 10:
  Set random_seed = new_value()
  FOR individual = 1 TO 200:
    chromosome[individual] = random_initialization(seed)
```

**Parameters:**
- Initial population size: **200**
- Restarts: **10** (each with new random seed)
- Total individuals created: 200 × 10 = **2,000** (across all restarts)

**Reproducibility:**
- Users can manually set random seed for identical results
- Default: blank (true randomization)

**Not Documented:**
- Initialization distribution (uniform? Gaussian? Latin hypercube?)
- Whether indicator selection is uniform random from all 37
- Whether parameters are initialized within indicator-specific bounds

---

### 3. Fitness Function

**Primary Metric:**
```
Fitness = NetProfit × AverageTrade
```

**Multi-Component Filter (Hard Constraints):**

Systems are **immediately disqualified** if they fail any threshold:

| Metric | Training/Test | Validation | Purpose |
|--------|--------------|------------|---------|
| Pearson Correlation | ≥ 0.95 | - | Equity curve consistency between in-sample and OOS |
| Profit Factor | ≥ 1.2 | ≥ 1.8 | Gross profit / gross loss ratio |
| Net Profit | Positive | Positive | After all costs |

**Fitness Evaluation Process:**

```
1. Run backtest on training data (40%)
2. Run backtest on test data (60%)
3. Calculate:
   - NetProfit_train, NetProfit_test
   - AverageTrade_train, AverageTrade_test
   - ProfitFactor_train, ProfitFactor_test
   - Pearson(equity_curve_train, equity_curve_test)

4. Apply filters:
   IF Pearson < 0.95 THEN reject
   IF ProfitFactor_train < 1.2 THEN reject
   IF ProfitFactor_test < 1.2 THEN reject

5. Calculate fitness:
   Fitness = NetProfit_test × AverageTrade_test
```

**Significance of Net Profit × Average Trade:**

This formulation penalizes high-frequency systems:
- System A: $100k profit, 10,000 trades, AvgTrade = $10 → Fitness = $1M
- System B: $80k profit, 1,000 trades, AvgTrade = $80 → Fitness = $6.4M

System B wins despite lower absolute profit because it's more **trade-efficient** (less transaction cost exposure, lower overtrading risk).

**Not Documented:**
- How tied fitness scores are broken
- Whether validation PF ≥ 1.8 is enforced during evolution or post-selection
- Penalty functions for constraint violations

---

### 4. Selection Method

**Status:** NOT DOCUMENTED

Based on standard GA practice and the "Max. Crossover Attempts" parameter, likely methods:
- Tournament selection (most common for elitist GAs)
- Roulette wheel selection
- Rank-based selection

**Inference from Crossover Timeout:**
The existence of "Max. Crossover Attempts" suggests selection can produce low-diversity parent pairs that struggle to generate viable offspring, implying a **fitness-proportional or tournament selection** that occasionally picks similar parents.

**Not Documented:**
- Selection pressure (tournament size if tournament selection)
- Elitism (how many top individuals carry over unchanged)
- Whether selection is with or without replacement

---

### 5. Crossover Operator

**Crossover Rate:** **95%**

This is exceptionally high — 95 out of 100 offspring are generated via crossover vs. only 5 by mutation.

**Crossover Control Parameter:**
- **Max. Crossover Attempts:** If crossover stalls for N attempts, GA auto-breaks and continues

This suggests crossover can fail (e.g., producing invalid offspring) and needs a timeout mechanism.

**Likely Crossover Type (Not Confirmed):**

Given the hybrid discrete-continuous encoding:

**For discrete genes (indicator IDs):**
- Likely uniform crossover or single-point
- Example: Parent1 = [3, 17, 22], Parent2 = [5, 9, 17] → Offspring = [3, 9, 22]

**For continuous genes (parameters, weights):**
- Likely blend crossover (BLX-α) or simulated binary crossover (SBX)
- Example: Parent1_weight = 1.2, Parent2_weight = -0.5 → Offspring_weight = 0.35 (blend)

**Not Documented:**
- Exact crossover mechanism (single-point, two-point, uniform, blend)
- Whether discrete and continuous genes use different operators
- Alpha parameter for blend crossover
- Crossover point selection strategy

---

### 6. Mutation Operator

**Mutation Rate:** **5%**

Only 5 out of 100 offspring are generated by mutation (vs. 95 by crossover).

**Mutation Strength:** **25%**

This controls the **magnitude** of parameter perturbations. Interpretation:

```
IF mutate(gene):
  gene_new = gene_old + random(-0.25, +0.25) × gene_range
```

Example:
- StopLoss range: [0, 2000]
- Current StopLoss: 800
- Mutation: 800 + random(-0.25, 0.25) × 2000 = 800 ± 500 = [300, 1300]

**Mutation Strategy (Inferred):**

Given the low 5% rate, mutation serves as **local refinement** rather than exploration. The 10 restarts provide diversity; mutation provides fine-tuning.

**Not Documented:**
- Whether mutation is Gaussian or uniform
- Whether mutation strength is adaptive (decreases over generations)
- Whether discrete genes (indicator IDs) mutate differently than continuous genes
- Mutation probability per gene vs. per individual

---

### 7. Termination Criteria

**Primary Termination:**
```
Generations × Population = 1000 × 200 = 200,000 fitness evaluations
```

**Early-Stop Reset-and-Restart:**

```
IF progress_stalled(N% of total tests):
  Reset random_seed
  Reinitialize population
  Restart optimization

Loop up to 10 restarts total
```

**Parameters:**
- Early-Stop threshold: "stopped before N% of total tests"
- Max restarts: **10**

**Total Computation:**
```
Best case: 200,000 evaluations (1 successful run)
Typical case: 200,000 × 3-5 restarts = 600k-1M evaluations
Worst case: 200,000 × 10 = 2M evaluations
```

**User Control:**
- Manual stop button available
- Can override automatic termination

**Not Documented:**
- How "progress stalled" is defined (no improvement for K generations? Fitness plateau?)
- Whether restarts share any information (warm start) or are completely independent
- What happens to best-so-far solution across restarts (kept or discarded?)

---

### 8. Walk-Forward GA (Separate Stage)

GSBsys has a **second GA stage** for walk-forward optimization:

**Parameters:**
- WF Generations: 100-150 (configurable)
- WF Population: 100-150 (configurable)
- WF Tests: WF_Generations × WF_Population

**Recommended Configurations:**
| Indicator Count | WF Gen × Pop | Total WF Tests |
|----------------|--------------|----------------|
| 3 indicators | 120 × 120 | 14,400 |
| 4-5 indicators | 150 × 150 | 22,500 |
| With adaptive MA | 150+ × 150+ | 22,500+ |

**Purpose:**

The WF-GA optimizes **when to re-optimize** the trading system during walk-forward testing:
- How often to retrain the system on new data
- What weight to give to recent vs. historical performance
- Whether to use additive or multiplicative parameter updates

**Evidence of Effectiveness:**
> "In all cases the WF parameters are better in EVERY metric in all 3 tests."

**Not Documented:**
- What the WF-GA chromosome encodes (walk-forward schedule parameters?)
- Fitness function for WF-GA (is it the same as main GA?)
- Whether WF-GA uses same crossover/mutation rates

---

## Computational Requirements

**Per-Individual Fitness Evaluation:**
- Fast (rule-based system, not RL training)
- Estimated: milliseconds to seconds
- Data: 30-minute bars typical (years of data)

**Total Compute:**
- Development GA: 200,000 evaluations per restart × 10 restarts = **2M evaluations max**
- Walk-forward GA: 22,500 evaluations
- **Total: ~2-3M fitness evaluations** per system development cycle

**Hardware Requirements:**
- Minimum RAM: **16 GB**
- Cloud workers recommended for large populations (prevents RAM exhaustion)

**Comparison to GA+RL:**
- GSBsys: milliseconds per evaluation → 2M evaluations feasible
- GA+RL: hours per evaluation (RL training) → 2,000-10,000 evaluations typical

This 100-1000x speed advantage enables GSBsys to explore orders of magnitude more combinations.

---

## Design Philosophy

**High Crossover, Low Mutation (95/5):**
- Crossover recombines successful indicator patterns
- Mutation provides fine-tuning
- Diversity comes from **10 independent restarts**, not mutation

**Conservative Train/Test Split (40/60):**
- Reserves majority of data for OOS validation
- Opposite of typical academic practice (60/40 or 70/30 training-favored)
- Reflects practitioner priority: robustness > maximum performance

**Multi-Component Fitness with Hard Floors:**
- Pearson ≥ 0.95 prevents divergent equity curves (Red Queen failure mode)
- Profit Factor ≥ 1.8 (validation) exceeds MaxAI's 1.07 live performance
- Net Profit × Avg Trade penalizes overtrading

**Restart-Based Diversity:**
- 10 independent random seeds
- Each restart explores different region of search space
- Prevents premature convergence without complex diversity preservation protocols

---

## Unknown Components

Despite extensive documentation analysis, the following remain undocumented:

1. **Selection method** (tournament? roulette? rank?)
2. **Exact crossover type** (single-point? BLX-α? SBX?)
3. **Mutation distribution** (Gaussian? Uniform?)
4. **Elitism strategy** (top N preserved?)
5. **Constraint handling** (penalty functions? repair mechanisms?)
6. **Chromosome bit/float representation**
7. **WF-GA chromosome structure and fitness**

These are likely proprietary implementation details deliberately omitted from user-facing documentation.

---

## Comparison to Standard GA

| Component | Standard GA | GSBsys |
|-----------|-------------|--------|
| Population | 50-100 typical | **200** (large) |
| Generations | 100-500 typical | **1000** (very large) |
| Crossover rate | 60-80% typical | **95%** (very high) |
| Mutation rate | 5-20% typical | **5%** (low) |
| Restarts | 1 typical | **10** (multi-start) |
| Total evals | 5k-50k typical | **2M max** (massive) |

GSBsys is a **large-scale, crossover-dominant, multi-start GA** optimized for exhaustive search of the trading system space.
