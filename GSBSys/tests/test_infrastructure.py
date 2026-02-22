"""Phase 1a smoke tests: verify infrastructure wiring.

These tests run with NUMBA_DISABLE_JIT=1 (set in conftest.py) and require
only the packages installed in Phase 1a. No data, indicators, or GA logic.
"""

from pathlib import Path

import pytest

# ── seed.py ───────────────────────────────────────────────────────────────────


def test_set_global_seed_is_callable():
    from src.utils.seed import set_global_seed

    set_global_seed(42)  # must not raise


def test_make_restart_seeds_length():
    from src.utils.seed import make_restart_seeds

    seeds = make_restart_seeds(42, n=10)
    assert len(seeds) == 10


def test_make_restart_seeds_deterministic():
    from src.utils.seed import make_restart_seeds

    assert make_restart_seeds(42) == make_restart_seeds(42)


def test_make_restart_seeds_unique():
    from src.utils.seed import make_restart_seeds

    seeds = make_restart_seeds(42, n=10)
    assert len(set(seeds)) == 10, "All restart seeds must be distinct"


def test_make_restart_seeds_different_bases():
    from src.utils.seed import make_restart_seeds

    assert make_restart_seeds(1) != make_restart_seeds(2)


# ── config.py ─────────────────────────────────────────────────────────────────


def test_gaconfig_defaults():
    from src.config import GAConfig

    cfg = GAConfig()
    assert cfg.population_size == 200
    assert cfg.n_restarts == 10
    assert cfg.n_indicators == 3
    assert cfg.train_ratio == 0.40
    assert cfg.cxpb == 0.95
    assert cfg.mutpb == 0.05


def test_gaconfig_frozen():
    from src.config import GAConfig

    cfg = GAConfig()
    with pytest.raises(Exception):  # ValidationError or TypeError
        cfg.population_size = 999  # type: ignore[misc]


def test_gaconfig_from_yaml(tmp_path):
    from src.config import GAConfig

    yaml_path = tmp_path / "test.yaml"
    yaml_path.write_text(
        "population_size: 50\nn_restarts: 3\n"
    )
    cfg = GAConfig.from_yaml(yaml_path)
    assert cfg.population_size == 50
    assert cfg.n_restarts == 3
    # Unspecified fields use defaults
    assert cfg.cxpb == 0.95


def test_gaconfig_from_yaml_spy_mvp():
    """Verify the shipped spy_mvp.yaml parses without errors."""
    from src.config import GAConfig

    cfg = GAConfig.from_yaml(Path("config/spy_mvp.yaml"))
    assert cfg.data.ticker == "SPY"
    assert cfg.n_indicators == 3
    assert cfg.warmup_bars == 252


def test_gaconfig_from_yaml_missing_file():
    from src.config import GAConfig

    with pytest.raises(FileNotFoundError):
        GAConfig.from_yaml("nonexistent.yaml")


# ── conftest DEAP fixture ─────────────────────────────────────────────────────


def test_deap_creator_registered():
    """conftest autouse fixture must have registered creator types."""
    from deap import creator

    assert hasattr(creator, "FitnessMax"), "FitnessMax not registered"
    assert hasattr(creator, "Individual"), "Individual not registered"


def test_deap_individual_creation():
    """Verify an Individual can be instantiated and has a fitness."""
    from deap import creator

    ind = creator.Individual([0, 14, 1.0, 0, 14, 1.0, 0, 14, 1.0, 25.0, 0.06, 0.12, 1.0])
    assert len(ind) == 13
    assert hasattr(ind, "fitness")
