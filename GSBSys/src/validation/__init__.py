"""Phase 2 validation framework for GA-Trading-Sys.

Four-layer validation pipeline:
  1. pearson_filter   — train/test equity curve correlation gate
  2. multi_period_oos — 5-regime walk-forward testing
  3. noise_injection  — 8-variant data robustness testing
  4. family_grouping  — parameter CoV stability analysis
  5. report           — unified pass/fail summary
"""
