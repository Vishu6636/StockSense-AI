# Day 7 Manual QA Fixes & Diagnostic Report

**Project:** StockSense AI  
**Date:** August 11, 2026  
**Status:** Completed & Verified  

---

## 🛠️ Direct Fixes Applied (Items 1 – 4)

### 1. Single Entry-Point Search Bar (Removed Duplicate Input)
* **File Modified:** [`views/search.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/search.py)
* **Issue:** Navigating to the Stock Analysis / Search page rendered a redundant local `selectbox` and `text_input` in addition to the global top navigation search bar.
* **Resolution:** Removed the local search form components from `views/search.py`. The global top navigation search bar is now the sole search entry point. Navigating to Stock Analysis with a selected ticker renders stock details directly, while an empty search displays an informative guide prompting the user to use the top search bar.

---

### 2. Fundamental Metrics Fix: ROE & Dividend Yield
* **Files Modified:** 
  * [`views/stock_detail.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/stock_detail.py)
  * [`data_service.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/data_service.py)
* **Issue:** Under the Fundamentals tab, ROE and Dividend Yield showed blank/missing values (`—`) for many stocks (e.g., RELIANCE.NS, TCS.NS, INFY.NS, AAPL).
* **Root Causes & Resolutions:**
  1. **Dividend Yield Multiplier Mismatch:** `yfinance` returns `info['dividendYield']` as an already-percentage float (e.g. `2.68` for 2.68%). The code multiplied this value by `100` (`268%`), which exceeded `safe_pct`'s `max_val=20` threshold, causing it to return `"—"`. Fixed by checking raw values and only converting decimal ratios (like `trailingAnnualDividendYield`) when applicable.
  2. **Missing Indian ROE Fallback:** `yfinance` returns `None` for `info['returnOnEquity']` on many major Indian tickers (e.g., RELIANCE.NS, ITC.NS, ASIANPAINT.NS). Added robust fallback calculation `(trailingEps / bookValue) * 100`, which correctly produces accurate ROEs (e.g. RELIANCE.NS: 8.2%, ITC.NS: 27.1%).
  3. **Display Limit Cap:** Expanded `safe_pct` ceiling from 80%/200% to 2000% so high-ROE stocks (e.g. Apple at 148.8%) are rendered properly instead of being truncated to `"—"`.

---

### 3. Removal of "Super Investors" from Pro Mode Results
* **File Modified:** [`views/pro.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/pro.py)
* **Issue:** Running the Pro Mode stock screener rendered a "Super Investors" tab alongside Passed, Rejected, and Score Chart. Super investor holdings belong contextually on individual stock analysis pages, not in screener result batches.
* **Resolution:** Removed the `👑 Super Investors` tab and its associated rendering call `render_super_investors()` from `views/pro.py`. Screener output now strictly presents `✅ Passed`, `❌ Rejected`, and `📊 Score Chart`.

---

### 4. Pro Mode State Reset on Navigation (Watchlist Preserved)
* **Files Modified:** 
  * [`views/pro.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/pro.py)
  * [`app.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/app.py)
* **Issue:** Navigating away from Pro Mode and returning retained stale filter selections and prior screener results.
* **Resolution:** Implemented `reset_pro_state()` in `views/pro.py` alongside active view tracking in `app.py`. When a user navigates to Pro Mode from any other section, all `pro_*` filter parameters and prior `pro_df` results are reset to clean defaults. Crucially, the user's `watchlist` session state (`st.session_state.watchlist`) is explicitly excluded and preserved intact.

---

## 🔍 Diagnostic Investigations (Items 5 – 7)

### 5. Diagnosis: "Super Investors" Data Sources
* **Observation:** The "Super Investors" section rendered the same 3 institutional names for most stocks analyzed.
* **Root Cause:** In `data_service.py`, `SUPER_INVESTORS` is a static Python dictionary containing hardcoded investor records for only 8 specific stocks (`RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, `INFY.NS`, `ICICIBANK.NS`, `SBIN.NS`, `AAPL`, `MSFT`). Any stock outside this hardcoded set falls back to `DEFAULT_INVESTORS` (a static list of 3 generic dummy placeholders).
* **Data Source Feasibility:**
  * **US Equities:** Real-time per-stock institutional and mutual fund holder data is accessible via `yfinance` (`yf.Ticker(symbol).institutional_holders` & `.mutualfund_holders`), returning top holders (BlackRock, Vanguard, Berkshire Hathaway, etc.) with exact share counts and dates.
  * **Indian Equities (.NS / .BO):** `yfinance` returns empty DataFrames for institutional/mutual fund holder endpoints on Indian symbols. Fetching live shareholding patterns for Indian stocks would require external APIs (such as NSE India live market endpoints or Trendlyne/Alpha Vantage premium).

---

### 6. Diagnosis: "Recent News" Date Filtering & Aging
* **Observation:** News articles displayed in the "Recent News" card sometimes dated back 6–12 months or longer.
* **Root Cause:** 
  1. `extract_news_items()` in `data_service.py` extracts the first 6 entries returned by `yf.Ticker(symbol).news` or GNews without parsing date strings/timestamps.
  2. No date-sorting or age-filtering logic exists. `yfinance` often caches older earnings call transcripts or evergreen editorial summaries ahead of recent news.
  3. ISO-8601 strings and UNIX timestamps are passed directly to `render_news()` without normalization.
* **Required Fix:**
  * Parse all article timestamps into standard `datetime` objects.
  * Sort the news list in descending order by publication date.
  * Apply a recency filter (e.g., exclude articles older than 30 or 60 days).

---

### 7. Diagnosis: "Trending Stocks" Static List
* **Observation:** The "Trending Stocks" page always displays the same fixed set of companies.
* **Root Cause:** In `views/trending.py`, the `trending` variable is initialized with a hardcoded list of 11 Indian stocks (`RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, etc.) and 11 US stocks (`AAPL`, `MSFT`, `GOOGL`, etc.). The page downloads 2-day price history for these specific 11 stocks and ranks them by 1-day percentage change. It does not scan the broader market for actual gainers/losers or volume leaders.
* **Required Data Sources for Dynamic Trending:**
  * **US Market:** Alpha Vantage `TOP_GAINERS_LOSERS` API endpoint (free tier, returns live top gainers, top losers, and most active US stocks) or Yahoo Finance Screener (`yf.EquityQuery`).
  * **Indian Market:** NSE India API (`/api/live-analysis-variations?index=gainers`) or scanning the pre-configured 500 Indian stock universe (`tickers_india.json`) via batch quote fetching to identify market-wide top 10 gainers/losers dynamically.

---

## ✅ Verification Summary

| Item | Description | Status | Verification Result |
| :--- | :--- | :--- | :--- |
| **Fix 1** | Remove duplicate search input | **Passed** | Global navbar is single entry point; detail page clean. |
| **Fix 2** | Fix ROE & Dividend Yield metrics | **Passed** | ROE (8.2% Reliance, 148.8% AAPL) & Div Yield (0.5% Reliance, 2.7% TCS) display accurately. |
| **Fix 3** | Clean Pro Mode results view | **Passed** | "Super Investors" tab removed from screener results. |
| **Fix 4** | Reset Pro Mode state on nav | **Passed** | Filters & results reset on fresh navigation; Watchlist state persists. |
| **Diag 5** | Super Investors data diagnosis | **Reported** | Root cause & source availability documented. |
| **Diag 6** | News recency filter diagnosis | **Reported** | Absence of timestamp parsing & date sorting documented. |
| **Diag 7** | Trending stocks list diagnosis | **Reported** | Hardcoded 11-stock array & dynamic replacement sources identified. |
