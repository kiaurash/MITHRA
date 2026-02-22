"""Pytest configuration and shared fixtures for GA-Trading-Sys.

Critical setup:
1. NUMBA_DISABLE_JIT=1 — disables Numba JIT compilation during tests so unit
   tests run in pure Python (fast, debuggable). Set before any numba import.
2. DEAP creator session fixture — DEAP uses global module state. Registering
   FitnessMax/Individual multiple times in the same process raises RuntimeError.
   A single session-scoped autouse fixture with hasattr guards prevents this.
"""

import os

# Must be set before any numba import occurs anywhere in the test session.
os.environ.setdefault("NUMBA_DISABLE_JIT", "1")

import pytest
from deap import base, creator


@pytest.fixture(scope="session", autouse=True)
def deap_creator():
    """Register DEAP creator types once per test session.

    DEAP's ``creator`` module is a global registry. Re-registering an
    already-registered type raises ``RuntimeError``. The ``hasattr`` guard
    makes this fixture safe when tests are collected across multiple modules
    or when ``conftest.py`` is imported more than once.

    The cleanup at yield ensures isolation if pytest is invoked multiple
    times in the same Python process (e.g., via ``pytest-repeat``).
    """
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

    yield

    # Cleanup — makes repeated pytest invocations safe
    if hasattr(creator, "FitnessMax"):
        del creator.FitnessMax
    if hasattr(creator, "Individual"):
        del creator.Individual
