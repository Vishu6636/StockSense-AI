# Day 5 — Automated Test Suite & Core Logic Verification Report

**Date**: August 10, 2026  
**Status**: Passed (14 / 14 tests passed)  
**Target Repository**: StockSense AI Platform  

---

## Executive Summary

A comprehensive automated `pytest` test suite was built for the core pure-logic functions in `data_service.py` (`compute_technicals()`, `generate_recommendation()`, `get_analyst_consensus()`, and `search_tickers()`).

During unit test execution, the test suite uncovered a real logic bug in `data_service.py` regarding Debt-to-Equity (D/E) percentage normalization and neutral score thresholds. Both issues were resolved and verified against the test suite.

---

## 1. Discovered & Fixed Real Codebase Bugs

### Bug 1: Debt-to-Equity Percentage Normalization Failure
- **Location**: `data_service.py` (lines 352 & 444)
- **Symptom**: `generate_recommendation()` and `screen_stocks_with_progress()` failed to normalize D/E percentage values between 5% and 100% (e.g., `80%` D/E ratio = `0.8`). Because the normalization check was set to `if de > 100: de = de / 100`, a company with a normal `80%` D/E retained `de = 80`, triggering the `if de > 2:` high-debt penalty (-2 points).
- **Fix Applied**: Updated the D/E normalization check in both functions:
  ```python
  if 5 < de < 999: de = de / 100  # Normalizes 80% -> 0.8
  ```

### Bug 2: Neutral Recommendation Score Threshold
- **Location**: `data_service.py` (lines 476–478)
- **Symptom**: Neutral companies with a score of `0` (no positive bonuses, but no negative penalties) were classified as `SELL` (🔴) instead of `HOLD` (🟡) because `HOLD` required `score >= 1`.
- **Fix Applied**:
  ```python
  if score >= 5: return "BUY", "buy", "🟢", reasons
  elif score >= 0: return "HOLD", "hold", "🟡", reasons
  else: return "SELL", "sell", "🔴", reasons
  ```

---

## 2. Test Suite Overview (`tests/test_data_service.py`)

The test suite covers 14 distinct test cases organized into 4 test classes:

1. **`TestComputeTechnicals`**:
   - `test_empty_or_short_dataframe_returns_empty_dict`: Validates graceful `{}` return for `None`, empty DataFrame, and DataFrames with < 30 rows.
   - `test_mathematical_correctness_on_synthetic_data`: Validates RSI calculation, MACD histogram invariant (`macd_hist == macd - signal`), Bollinger Band boundaries (`bb_upper == ma20 + 2*std20`), and moving averages on synthetic price series.

2. **`TestGenerateRecommendation`**:
   - `test_clear_buy_case`: Validates healthy company metrics produce `BUY` (🟢, score >= 5).
   - `test_clear_sell_case`: Validates high P/E, low ROE, high debt produce `SELL` (🔴, score < 0).
   - `test_hold_case`: Validates moderate metrics produce `HOLD` (🟡, score 0 to 4).
   - `test_empty_or_malformed_info`: Confirms handling of `{}` info dict without raising exceptions.

3. **`TestGetAnalystConsensus`**:
   - `test_malformed_or_empty_inputs_return_none`: Asserts `None` for `None`, `pd.DataFrame()`, strings, numbers, lists.
   - `test_dataframe_without_period_column_returns_none`: Asserts `None` for missing `"period"` column.
   - `test_zero_total_consensus_returns_none`: Asserts `None` when analyst counts total 0.
   - `test_valid_analyst_recommendations`: Confirms dict structure and totals for valid analyst data.

4. **`TestSearchTickers`**:
   - `test_partial_match`: Tests `"rel"` matching `"RELIANCE.NS"` and `"aap"` matching `"AAPL"`.
   - `test_case_insensitivity`: Tests `"tcs"`, `"TCS"`, `"Tcs"` resolving identically.
   - `test_search_by_name`: Tests company name search (e.g. `"tata"` -> `"TCS.NS"`).
   - `test_no_match_returns_empty_list`: Asserts `[]` for unknown tickers.

---

## 3. Pytest Execution Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.5.0 -- C:\Users\sriva_3b9ej2a\miniconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\sriva_3b9ej2a\OneDrive\Documents\projects\Stock Analysis & Ranking System
plugins: anyio-4.13.0, logfire-4.32.0, cov-7.1.0
collected 14 items

tests/test_data_service.py::TestComputeTechnicals::test_empty_or_short_dataframe_returns_empty_dict PASSED [  7%]
tests/test_data_service.py::TestComputeTechnicals::test_mathematical_correctness_on_synthetic_data PASSED [ 14%]
tests/test_data_service.py::TestGenerateRecommendation::test_clear_buy_case PASSED [ 21%]
tests/test_data_service.py::TestGenerateRecommendation::test_clear_sell_case PASSED [ 28%]
tests/test_data_service.py::TestGenerateRecommendation::test_hold_case PASSED [ 35%]
tests/test_data_service.py::TestGenerateRecommendation::test_empty_or_malformed_info PASSED [ 42%]
tests/test_data_service.py::TestGetAnalystConsensus::test_malformed_or_empty_inputs_return_none PASSED [ 50%]
tests/test_data_service.py::TestGetAnalystConsensus::test_dataframe_without_period_column_returns_none PASSED [ 57%]
tests/test_data_service.py::TestGetAnalystConsensus::test_zero_total_consensus_returns_none PASSED [ 64%]
tests/test_data_service.py::TestGetAnalystConsensus::test_valid_analyst_recommendations PASSED [ 71%]
tests/test_data_service.py::TestSearchTickers::test_partial_match PASSED [ 78%]
tests/test_data_service.py::TestSearchTickers::test_case_insensitivity PASSED [ 85%]
tests/test_data_service.py::TestSearchTickers::test_search_by_name PASSED [ 92%]
tests/test_data_service.py::TestSearchTickers::test_no_match_returns_empty_list PASSED [100%]

============================= 14 passed in 3.00s ==============================
```
