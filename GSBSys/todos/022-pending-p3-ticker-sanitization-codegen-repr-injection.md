---
status: pending
priority: p3
issue_id: "022"
tags: [code-review, security, quality]
dependencies: ["002"]
---

# Ticker symbol used in `repr()` / f-string in generated code — code injection via malicious ticker

## Problem Statement

`src/export/codegen.py` generates Python source code that embeds the ticker symbol as a string literal. The ticker is inserted via f-string or `repr()` without sanitization. A malicious ticker string containing quote characters or Python escape sequences could produce syntactically invalid or injected generated code. Example: a ticker of `"SPY'; import os; os.system('rm -rf /')\n#"` would embed that string directly into the generated Python script. While yfinance would reject such a ticker, the code generation path itself has no defense.

## Findings

- **`src/export/codegen.py`** — ticker embedded in generated code template
- **Security reviewer finding:** "ticker in repr() could inject into generated code; sanitize to `[A-Z0-9.-]+`"
- **Risk level:** Low (yfinance rejects invalid tickers first; only triggered if codegen is called directly)

## Proposed Solutions

### Option A — Sanitize ticker before embedding in generated code (Recommended)
```python
import re
def _sanitize_ticker(ticker: str) -> str:
    if not re.match(r'^[A-Z0-9.\-\^=]{1,10}$', ticker):
        raise ValueError(f"Invalid ticker symbol: {ticker!r}")
    return ticker
```
Call before inserting into template.

- **Effort:** Tiny
- **Risk:** None — strictens input; valid tickers all pass the regex

### Option B — Use `shlex.quote()` equivalent for Python string literals
Escape the ticker before embedding.

- **Effort:** Tiny
- **Risk:** None

### Option C — Accept risk for a local developer tool
Ticker is validated by yfinance before codegen is called.

- **Effort:** None
- **Risk:** Low in current context

## Recommended Action

Option A — a one-function regex guard. Apply when fixing issue 002 (codegen template overhaul).

## Acceptance Criteria

- [ ] Ticker validated against `[A-Z0-9.\-\^=]{1,10}` before embedding in generated code
- [ ] `ValueError` raised for invalid tickers (not embedded)
- [ ] Test: malformed ticker raises ValueError in codegen (not inserts into code)
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by security review agent
