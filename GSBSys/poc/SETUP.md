# POC Setup and Execution Guide

## Quick Start

### 1. Navigate to POC Directory

```bash
cd c:/Users/kiaur/Documents/AI-ML/AI-Product-Development/Bootcamp25/GSBSys/poc
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **Linux/Mac**: `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important Note on TA-Lib:**

TA-Lib requires C library compilation. If pip install fails:

**Windows:**
1. Download precompiled wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install: `pip install TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`

**Linux:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**Alternative**: If TA-Lib installation fails, temporarily replace `talib` with `pandas-ta` in requirements.txt and modify indicators.py to use pandas_ta.

### 4. Run Individual Module Tests

Test each module independently to verify installation:

```bash
# Test data loading
python data_loader.py

# Test indicators
python indicators.py

# Test backtesting (requires VectorBT)
python backtest.py

# Test fitness function
python fitness.py

# Test GA engine
python ga_engine.py
```

### 5. Run Full POC

```bash
python main_poc.py
```

**Expected Runtime:**
- Performance benchmark: ~2-5 minutes (100 evaluations)
- Full GA evolution: ~30-60 minutes (1000 generations × 100 population)

## Expected Output

### Performance Benchmark
```
BENCHMARK: Fitness Function Performance
========================================================
Running 100 fitness evaluations...

Results:
  Total time: 3500.00ms
  Average per evaluation: 35.00ms
  Target: <50ms
  ✓ PASS: 35.00ms < 50ms
```

### Convergence Test
```
CONVERGENCE TEST: GA Evolution
========================================================
Gen 0: {'avg': 0.001, 'max': 0.015, 'min': 0.000}
Gen 100: {'avg': 0.045, 'max': 0.082, 'min': 0.001}
...
Gen 1000: {'avg': 0.078, 'max': 0.125, 'min': 0.012}

Best Individual Found:
  Parameters: [-62.3, 58.7, 0.042, 0.135, 0.087]
    RSI Buy Threshold: -62.30
    RSI Sell Threshold: 58.70
    Stop Loss: 4.20%
    Take Profit: 13.50%
    Position Size: 8.70%
  Fitness: 0.125436

Convergence Analysis:
  Initial max fitness: 0.015234
  Final max fitness: 0.125436
  Improvement: 0.110202
  ✓ PASS: Fitness improved over generations
```

### Final Verdict
```
POC VALIDATION SUMMARY
========================================================
1. VectorBT Speed: ✓ PASS
   Average: 35.00ms (Target: <50ms)

2. DEAP Integration: ✓ PASS
   GA ran successfully for 1000 generations

3. Fitness Function: ✓ PASS
   Fitness calculations completed without errors

4. Convergence: ✓ PASS
   Best fitness: 0.125436

========================================================
VERDICT: ✓ ALL TESTS PASSED

Recommendation: Proceed with full MVP implementation
========================================================
```

## Troubleshooting

### TA-Lib Installation Issues
- **Problem**: "error: Microsoft Visual C++ 14.0 or greater is required"
- **Solution**: Use precompiled wheel (Windows) or install from source (Linux)
- **Workaround**: Replace with pandas-ta library

### VectorBT Performance Issues
- **Problem**: Fitness evaluation >100ms
- **Solution**:
  1. Reduce data size (use 2015-2025 instead of 2010-2025)
  2. Enable Numba JIT compilation (already in backtest.py)
  3. Reduce population size to 50

### Memory Issues
- **Problem**: "MemoryError" during GA evolution
- **Solution**:
  1. Reduce population size from 100 to 50
  2. Reduce generations from 1000 to 500
  3. Close other applications

### Data Loading Failures
- **Problem**: yfinance returns empty DataFrame
- **Solution**:
  1. Check internet connection
  2. Verify SPY ticker exists
  3. Try alternate data range (2020-2025)
  4. Check yfinance version: `pip install --upgrade yfinance`

## Next Steps After POC

### If All Tests Pass (✓)
1. Review full implementation plan (Design/2026-02-21-feat-ga-trading-sys-implementation-plan.md)
2. Setup full project structure for Phase 1
3. Begin Week 1-12: Core GA Engine implementation

### If Performance Test Fails (✗)
1. Profile VectorBT usage to identify bottlenecks
2. Consider alternative: backtest.py with custom Numba-accelerated engine
3. Re-validate with optimized implementation

### If Convergence Test Fails (✗)
1. Analyze logbook for fitness trends
2. Adjust GA parameters (increase mutation rate, population size)
3. Modify fitness function if all individuals score 0
4. Re-run with adjusted parameters

## Git Branch

Current branch: `feat/ga-sys-poc`

After POC validation:
- If PASS: Merge to main and create new branch for Phase 1
- If FAIL: Document findings, iterate on POC, or pivot approach
