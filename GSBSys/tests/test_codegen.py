"""Tests for src/export/codegen.py."""

from __future__ import annotations

import pytest
import yaml

from src.export.codegen import (
    export_strategy_yaml,
    generate_backtest_code,
    load_strategy_yaml,
)
from src.ga.chromosome import GENE_NAMES, N_GENES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_individual() -> list:
    return [0, 14, 1.2, 5, 9, 0.8, 13, 20, 1.0, 0.3, 0.04, 0.08, 1.0]


# ---------------------------------------------------------------------------
# generate_backtest_code
# ---------------------------------------------------------------------------

class TestGenerateBacktestCode:
    def test_returns_string(self):
        code = generate_backtest_code(_make_individual())
        assert isinstance(code, str)
        assert len(code) > 0

    def test_contains_individual_repr(self):
        ind = _make_individual()
        code = generate_backtest_code(ind)
        assert "INDIVIDUAL" in code

    def test_contains_gene_names(self):
        code = generate_backtest_code(_make_individual())
        # At least first and last gene names should appear in comments
        assert "ind1_type" in code
        assert "position_size_mult" in code

    def test_contains_main_function(self):
        code = generate_backtest_code(_make_individual())
        assert "def main()" in code

    def test_contains_imports(self):
        code = generate_backtest_code(_make_individual())
        assert "import" in code

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError):
            generate_backtest_code([1, 2, 3])  # too short

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            generate_backtest_code([])

    def test_valid_python_syntax(self):
        """Generated code must compile without SyntaxError."""
        code = generate_backtest_code(_make_individual())
        compile(code, "<generated>", "exec")

    def test_gene_values_in_code(self):
        ind = _make_individual()
        code = generate_backtest_code(ind)
        # The repr of the list should be embedded
        for val in ind:
            assert str(val) in code or str(float(val)) in code

    def test_uses_load_market_data_not_DataLoader(self):
        """Generated script must call load_market_data(), not DataLoader class."""
        code = generate_backtest_code(_make_individual())
        assert "load_market_data" in code
        assert "DataLoader" not in code

    def test_warmup_bars_parameter_interpolated(self):
        """Custom warmup_bars value must appear in generated WARMUP_BARS constant."""
        code = generate_backtest_code(_make_individual(), warmup_bars=100)
        assert "WARMUP_BARS     = 100" in code

    def test_train_fraction_parameter_interpolated(self):
        """Custom train_fraction value must appear in generated TRAIN_FRACTION constant."""
        code = generate_backtest_code(_make_individual(), train_fraction=0.70)
        assert "TRAIN_FRACTION  = 0.7" in code

    def test_named_index_constants_in_generated_code(self):
        """Generated code must use IDX_* constants, not raw indices 10/11/12."""
        code = generate_backtest_code(_make_individual())
        assert "IDX_STOP_LOSS_PCT" in code
        assert "IDX_TAKE_PROFIT_PCT" in code
        assert "IDX_POSITION_SIZE_MULT" in code


# ---------------------------------------------------------------------------
# export_strategy_yaml / load_strategy_yaml
# ---------------------------------------------------------------------------

class TestStrategyYamlRoundtrip:
    def test_roundtrip(self, tmp_path):
        ind = _make_individual()
        path = tmp_path / "strategy.yaml"
        export_strategy_yaml(ind, str(path))
        loaded = load_strategy_yaml(str(path))
        assert len(loaded) == N_GENES
        for orig, loaded_val in zip(ind, loaded):
            assert orig == pytest.approx(loaded_val)

    def test_yaml_has_gene_names_as_keys(self, tmp_path):
        path = tmp_path / "strategy.yaml"
        export_strategy_yaml(_make_individual(), str(path))
        with open(path) as f:
            data = yaml.safe_load(f)
        for name in GENE_NAMES:
            assert name in data

    def test_load_returns_list_of_n_genes(self, tmp_path):
        path = tmp_path / "strategy.yaml"
        export_strategy_yaml(_make_individual(), str(path))
        loaded = load_strategy_yaml(str(path))
        assert isinstance(loaded, list)
        assert len(loaded) == N_GENES

    def test_export_wrong_length_raises(self, tmp_path):
        with pytest.raises(ValueError):
            export_strategy_yaml([1, 2], str(tmp_path / "bad.yaml"))

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_strategy_yaml("nonexistent_strategy.yaml")

    def test_export_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "strategy.yaml"
        export_strategy_yaml(_make_individual(), str(path))
        assert path.exists()

    def test_gene_order_preserved(self, tmp_path):
        """Loaded list must match GENE_NAMES order."""
        ind = list(range(N_GENES))  # unique values 0..12
        ind = [float(v) for v in ind]
        path = tmp_path / "order.yaml"
        export_strategy_yaml(ind, str(path))
        loaded = load_strategy_yaml(str(path))
        for i, name in enumerate(GENE_NAMES):
            assert loaded[i] == pytest.approx(ind[i]), f"Mismatch at gene {name}"
