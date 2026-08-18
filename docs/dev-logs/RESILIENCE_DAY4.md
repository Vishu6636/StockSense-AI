# Day 4 — Error Handling & System Resilience Report

**Date**: August 10, 2026  
**Status**: Completed  
**Target Repository**: StockSense AI Platform  

---

## Executive Summary

The Day 4 resilience pass focused on auditing and hardening all data-fetching routines across `data_service.py` and every user view in `views/`. Every potential failure state was audited and handled to guarantee that the application gracefully degrades with clear, friendly user notifications (`st.info` / `st.warning`) and never renders a red Streamlit error box or python stack trace.

---

## Failure Condition Scenarios & Applied Fixes

### 1. No Internet Connection (yfinance / API Timeout)
- **Simulated Condition**: Network timeout, socket disconnect, or API service unavailability during data fetching (`yf.Ticker`, `yf.download`, `get_stock_data`, `get_market_news`).
- **Behavior Before Fix**: High potential for unhandled `ConnectionError`, `RequestException`, or empty array indexing errors.
- **Fix Applied**:
  - `data_service.py`: Wrapped API calls in try-except blocks returning safe fallbacks (`None`, `{}`, or `[]`).
  - `views/trending.py`: Updated fallback from `st.error` to `st.warning("⚠️ Could not fetch trending stock data. Please check your internet connection or try again later.")`.
  - `views/home.py`: Added fallback notice `st.info("📰 Market news temporarily unavailable. Please check your internet connection or try again later.")`.
  - `views/search.py`: Gracefully intercepts network failures with `st.warning("⚠️ Data unavailable for this stock. Please try another.")`.

---

### 2. Ticker That Doesn't Exist or Was Delisted
- **Simulated Condition**: User searches for an invalid, misspelled, or delisted symbol (e.g. `INVALID123` or `DELISTED.NS`).
- **Behavior Before Fix**: `views/stock_detail.py` displayed a red `st.error` alert box.
- **Fix Applied**:
  - `views/stock_detail.py`: Replaced `st.error` with a friendly `st.warning("⚠️ Stock data unavailable for **{ticker}**. The ticker may be delisted or invalid.")` accompanied by an `st.info("💡 Try selecting a stock from the dropdown list or search by company name.")` guidance tip.

---

### 3. Empty Search Results
- **Simulated Condition**: User submits the search form without selecting or entering a ticker symbol.
- **Behavior Before Fix**: Rendered a red `st.error` notification.
- **Fix Applied**:
  - `views/search.py`: Replaced `st.error` with `st.warning("⚠️ Please select a stock from the dropdown list or enter a ticker symbol.")`.
  - `views/beginner.py`: Replaced `st.error` with `st.warning("⚠️ No stocks matched your exact criteria. Try broadening your budget or risk preferences.")` and an `st.info` suggestion tip.
  - `views/pro.py`: Updated empty screener results to display `st.warning("⚠️ No stocks matched your exact criteria. Try relaxing your P/E, ROE, or Debt filters.")` and `st.info` advice.

---

### 4. Stock with Missing Fundamental Data (e.g. No P/E, No ROE)
- **Simulated Condition**: Fetching metrics for newly listed stocks, ETFs, or REITs missing traditional fundamental data fields (`trailingPE`, `returnOnEquity`, `debtToEquity`, `revenueGrowth`, `earningsGrowth`).
- **Behavior Before Fix**: Potential `TypeError`, `ValueError`, or `ZeroDivisionError` during formatting or radar chart mathematical bounds calculation.
- **Fix Applied**:
  - `views/stock_detail.py`: Built safe metric parsing helpers (`safe_ratio`, `safe_pct`, `pc`) that convert `None`, `NaN`, string error values, or missing properties to standard `"N/A"` or `"—"` strings without throwing exceptions.
  - `ui_components.py`: `radar_chart` functions with bounded default fallbacks (`or 0`, `or 50`, `min/max` bounds checking) so missing metrics render as zero-values on polar charts rather than raising runtime errors.

---

### 5. Switching Market Mode (India <-> US) Mid-Session
- **Simulated Condition**: User toggles the top market switch from `🇮🇳 ₹ India` to `🇺🇸 $ US` or vice-versa while data is loading or halfway through stock screening/comparison.
- **Behavior Before Fix**: State mismatch where old Indian tickers (`RELIANCE.NS`) were passed to US market price formatters or screener DataFrames persisted across sessions.
- **Fix Applied**:
  - `ui_components.py`: Added active state purging (`pro_df`, `compare_tickers`, `search_ticker`) when `market_mode` changes. When switched, transient search and comparison data is cleared before `st.rerun()`, ensuring clean re-initialization under the new currency and market universe.

---

### 6. Hitting Compare with Fewer Than 2 Tickers Selected
- **Simulated Condition**: User clicks `🆚 Compare Now` with 0 or 1 stock selected, or when data for selected stocks cannot be fetched.
- **Behavior Before Fix**: Displayed red `st.error("Please select at least 2 stocks.")` and `st.error("Need at least 2 valid stocks.")`.
- **Fix Applied**:
  - `views/compare.py`: Replaced both `st.error` calls with friendly yellow notifications:
    - `st.warning("⚠️ Please select at least 2 different stocks to compare.")`
    - `st.warning("⚠️ Could not fetch complete data for at least 2 valid stocks. Please check your internet connection or selections.")`.

---

### 7. User on Watchlist Page with an Empty Watchlist
- **Simulated Condition**: Logged-in user visits the watchlist page (`views/watchlist.py`) with zero saved stocks in `st.session_state.watchlist`.
- **Behavior Before Fix**: Rendered custom HTML empty card, but lacked a formal Streamlit notification widget.
- **Fix Applied**:
  - `views/watchlist.py`: Added explicit Streamlit notification `st.info("ℹ️ Your watchlist is currently empty. Add stocks by clicking the ⭐ Watch button on any stock page.")` alongside the existing interactive CTA button (`🔍 Find Stocks to Watch`).

---

## Verification Summary

| Scenario | Tested View | Warning/Info Alert Shown | Red Error Box Present? | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. No Internet** | `trending.py`, `home.py` | `st.warning` / `st.info` | ❌ No | ✅ Passed |
| **2. Invalid / Delisted Ticker** | `stock_detail.py` | `st.warning` + `st.info` | ❌ No | ✅ Passed |
| **3. Empty Search / Screener** | `search.py`, `beginner.py`, `pro.py` | `st.warning` + `st.info` | ❌ No | ✅ Passed |
| **4. Missing Fundamentals** | `stock_detail.py`, `ui_components.py` | Renders `"N/A"` / `"—"` | ❌ No | ✅ Passed |
| **5. Mid-Session Market Switch** | `ui_components.py` | Clean re-initialization | ❌ No | ✅ Passed |
| **6. Compare < 2 Stocks** | `compare.py` | `st.warning` | ❌ No | ✅ Passed |
| **7. Empty Watchlist** | `watchlist.py` | `st.info` | ❌ No | ✅ Passed |
