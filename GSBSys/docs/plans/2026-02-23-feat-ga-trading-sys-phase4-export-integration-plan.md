---
title: "GA-Trading-Sys Phase 4: Export & Integration"
type: feat
date: 2026-02-23
prd: Design/GA-Trading-Sys-MVP-PRD.md
prd_version: "2.0"
prior_plan: docs/plans/2026-02-23-feat-ga-trading-sys-phase3-robustness-plan.md
phase: 4
timeline: "6 weeks (Weeks 27–32)"
---

# feat: GA-Trading-Sys Phase 4 — Export & Integration

## Overview

Phase 4 completes the MVP by wrapping Phases 1-3 in user-facing tooling:
a validated Pydantic config schema, executable Python code generation,
text/CSV performance reports, equity-curve visualisations, and a
Click-based CLI (`ga-trading-sys init|optimize|validate|backtest`).

**Phase 3 status:** Complete — 302 tests passing, 3-module robustness operational.

**What Phase 4 adds:**
1. **Config schema** — Pydantic v2 YAML validation (FR-8.1)
2. **Code generation** — self-contained executable Python strategy (FR-7.1)
3. **Performance reports** — text + CSV (FR-7.3)
4. **Visualizer** — equity-curve plots via Matplotlib (FR-7.2)
5. **CLI** — `init`, `optimize`, `validate`, `backtest` (FR-8.2)

---

## Components

### `src/config.py` — Configuration Schema

```python
class DataConfig(BaseModel):
    ticker: str = "SPY"
    start_date: str = "2010-01-01"
    end_date: str = "2024-12-31"

class GAConfig(BaseModel):
    population_size: int = Field(default=200, ge=10, le=2000)
    n_generations:   int = Field(default=1000, ge=1, le=10000)
    n_restarts:      int = Field(default=10, ge=1, le=50)
    seed:            int = 42
    use_lhs:         bool = True

class BacktestConfig(BaseModel):
    warmup_bars:          int   = 252
    normalization_window: int   = 252
    train_fraction:       float = Field(default=0.40, ge=0.1, le=0.9)
    stop_loss_pct:        Optional[float] = None
    take_profit_pct:      Optional[float] = None
    position_size_mult:   Optional[float] = None

class OutputConfig(BaseModel):
    dir:          str  = "results"
    save_code:    bool = True
    save_plots:   bool = True
    save_reports: bool = True

class OptimizationConfig(BaseModel):
    data:     DataConfig     = DataConfig()
    ga:       GAConfig       = GAConfig()
    backtest: BacktestConfig = BacktestConfig()
    output:   OutputConfig   = OutputConfig()

def load_config(path: str) -> OptimizationConfig
def save_config(config: OptimizationConfig, path: str) -> None
def default_config_yaml() -> str   # template YAML string
```

### `src/export/codegen.py` — Strategy Code Generation

```python
def generate_backtest_code(individual: list) -> str
    # Returns self-contained Python source that imports from src.*
    # and reproduces the backtest

def export_strategy_yaml(individual: list, path: str) -> None
    # Save individual as YAML dict with gene names as keys

def load_strategy_yaml(path: str) -> list
    # Load individual from YAML, returns 13-gene list
```

### `src/export/reporter.py` — Performance Reports

```python
@dataclass(frozen=True)
class PerformanceReport:
    profit_factor:    float
    total_pnl:        float
    n_trades:         int
    avg_trade_pnl:    float
    sharpe_ratio:     float
    max_drawdown_pct: float
    win_rate_pct:     float
    expectancy:       float

def build_report(result: BacktestResult) -> PerformanceReport
def format_text(report: PerformanceReport) -> str   # human-readable table
def save_csv(report: PerformanceReport, path: str) -> None
def load_csv(path: str) -> PerformanceReport
```

### `src/export/visualizer.py` — Equity Curve Plots

```python
def plot_equity_curves(
    train_equity: np.ndarray,
    test_equity:  np.ndarray,
    title: str = "Equity Curves",
    save_path: Optional[str] = None,
    show: bool = False,
) -> None

def plot_regime_performance(
    regime_result: RegimeTestResult,
    save_path: Optional[str] = None,
    show: bool = False,
) -> None
```

### `src/cli/commands.py` — Click CLI

```bash
ga-trading-sys init     --output config.yaml
ga-trading-sys optimize --config config.yaml --output results/
ga-trading-sys validate --results results/ [--individual individual.yaml]
ga-trading-sys backtest --individual results/individual.yaml
```

---

## File Structure

```
src/
├── config.py
├── export/
│   ├── __init__.py
│   ├── codegen.py
│   ├── reporter.py
│   └── visualizer.py
└── cli/
    ├── __init__.py
    └── commands.py

tests/
├── test_config.py
├── test_codegen.py
├── test_reporter.py
├── test_visualizer.py
└── test_cli.py

experiments/
└── 05_phase4_export.py

docs/
└── user_guide.md
```

---

## Implementation Checklist

### Phase 4a: Config
- [ ] `src/config.py` — Pydantic v2 schema + load/save helpers
- [ ] `tests/test_config.py`

### Phase 4b: Code Generation
- [ ] `src/export/__init__.py`
- [ ] `src/export/codegen.py` — `generate_backtest_code()`, `export_strategy_yaml()`, `load_strategy_yaml()`
- [ ] `tests/test_codegen.py`

### Phase 4c: Performance Reports
- [ ] `src/export/reporter.py` — `PerformanceReport`, `build_report()`, `format_text()`, `save_csv()`, `load_csv()`
- [ ] `tests/test_reporter.py`

### Phase 4d: Visualizer
- [ ] `src/export/visualizer.py` — `plot_equity_curves()`, `plot_regime_performance()`
- [ ] `tests/test_visualizer.py`

### Phase 4e: CLI
- [ ] `src/cli/__init__.py`
- [ ] `src/cli/commands.py` — Click group + 4 commands
- [ ] `tests/test_cli.py`

### Phase 4f: Integration + docs + commit
- [ ] `experiments/05_phase4_export.py` — end-to-end demo
- [ ] `docs/user_guide.md` — getting-started guide
- [ ] Run full suite + commit

---

## Acceptance Criteria

### MVP Tier
- [ ] Config validates YAML and rejects invalid fields
- [ ] Generated strategy.py runs without error and outputs PF
- [ ] Performance report saved as text + CSV
- [ ] Equity curve PNG saved to file
- [ ] `ga-trading-sys init` creates a valid config file

### Production Tier
- [ ] Generated code reproduces backtest result (PF within ±0.01%)
- [ ] CLI `optimize` end-to-end with synthetic data
- [ ] User guide covers: install, configure, optimize, validate

### Quality
- [ ] All new tests pass (full suite ≥ 302 + new)
- [ ] Matplotlib import gracefully skipped if unavailable
- [ ] Pydantic validation errors give human-readable messages
