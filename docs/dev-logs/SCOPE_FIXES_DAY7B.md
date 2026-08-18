# Scope Fixes Report — Day 7B

**Project:** StockSense AI  
**Date:** August 11, 2026  
**Status:** All Scope Fixes Implemented & Verified  

---

## 1. 📰 News Recency & Date Parsing Fix
* **Files Modified:** 
  * [`data_service.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/data_service.py)
  * [`views/stock_detail.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/stock_detail.py)
* **Changes Implemented:**
  1. **Robust Timestamp Parser (`_parse_news_datetime`):** Handles ISO-8601 strings (e.g. `2026-08-10T14:00:00Z`), strings with numeric timestamps, and raw UNIX epoch integers (e.g. `1754640000`), converting all into UTC-aware `datetime` objects.
  2. **Recency Sorting & 45-Day Cutoff:** All extracted articles are sorted in descending order (most recent first). A strict 45-day window (`now - 45 days`) is applied.
  3. **Honest Fallback Labeling:** If 3 or more articles fall within the 45-day window, only recent articles are displayed under `📰 Recent News`. If fewer than 3 articles meet the cutoff, the app falls back to displaying the available sorted articles while honest header labeling (`📰 News & Archives`) informs the user of older items.
  4. **Clean UI Formatting:** Datetimes are formatted uniformly as `DD MMM YYYY, HH:MM AM/PM` (e.g., `11 Aug 2026, 01:37 PM`).

---

## 2. 👑 Super Investors — US Live Data & Indian Removal
* **Files Modified:** 
  * [`data_service.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/data_service.py)
  * [`views/stock_detail.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/stock_detail.py)
* **Changes Implemented:**
  1. **US Real Institutional Holders (`get_us_institutional_holders`):** Replaced hardcoded dictionary lookups with live calls to `yf.Ticker(symbol).institutional_holders`. Formats institutional names (e.g. *BlackRock Inc.*, *Vanguard Capital Management*), percentage shares held (e.g. `7.97%`), and total dollar value (e.g. `$356.07B`).
  2. **24-Hour Caching:** Decorated with `@st.cache_data(ttl=86400)` to eliminate redundant API calls and respect Yahoo Finance rate limits.
  3. **Complete Removal for Indian Stocks:** For Indian stocks (`.NS` / `.BO` / India market mode), the `👑 Super Investors` tab is omitted entirely from the stock detail tab bar.
  4. **Static Dictionary Cleanup:** Deleted the obsolete hardcoded `SUPER_INVESTORS` and `DEFAULT_INVESTORS` dictionaries.
  5. **Empty State Handling:** US stocks with sparse institutional data gracefully render a clean card (`No institutional holder data available for this ticker.`) without errors or crashing.

---

## 3. 🔥 Trending Stocks — Expanded Curated Pool & Daily Rotation
* **File Modified:** [`views/trending.py`](file:///c:/Users/sriva_3b9ej2a/OneDrive/Documents/projects/Stock%20Analysis%20&%20Ranking%20System/views/trending.py)
* **Changes Implemented:**
  1. **Expanded Large-Cap Pools:** Expanded the curated pool from 11 tickers to 48 highly liquid, large-cap names for India (`CURATED_TRENDING_INDIA`) and 48 for the US (`CURATED_TRENDING_US`).
  2. **Deterministic Daily Rotation (`get_daily_trending_list`):** Uses `datetime.date.today().toordinal()` as a random seed. This deterministically selects a 12-stock subset each day—ensuring identical results across reruns on the same day while rotating to a fresh subset the next day.
  3. **Honest Labeling:** Renamed section title to `🔥 Daily Highlighted Movers ({market})` and added the explanatory caption: `💡 Daily rotating selection of 12 liquid large-cap stocks ranked by 1-day % change.`

---

## 🧪 Verification & Audit Results

### 1. Automated Unit Tests (`pytest`)
- Executed `pytest`: All **14 unit tests** in `tests/test_data_service.py` passed cleanly (`100%`).

### 2. Programmatic Script Verification
- **News Recency:** ISO and UNIX timestamps parsed correctly; sorted descending; 45-day cutoff and fallback titles confirmed.
- **US Super Investors:** AAPL returned live holders (*Blackrock Inc.* `7.97%` `$356.07B`, *Vanguard* `6.54%` `$292.04B`). `RELIANCE.NS` returned `[]`.
- **Daily Rotation:** Rotation test confirmed today's 12-stock selection differs deterministically from tomorrow's 12-stock selection.

### 3. Browser Visual QA Verification
- **AAPL Detail Page:** Confirmed `👑 Super Investors` tab renders real institutional holders with accurate share percentages and dollar values.
- **RELIANCE.NS Detail Page:** Confirmed `👑 Super Investors` tab is completely absent from the tabs header.
- **Trending Page:** Confirmed section title `🔥 Daily Highlighted Movers (🇮🇳 India)` and caption `💡 Daily rotating selection of 12 liquid large-cap stocks ranked by 1-day % change.` display correctly.

---

## 📸 Artifact Reference
* **Browser Session WebP Recording:** `scope_fixes_day7b_verification_1786456923469.webp`
