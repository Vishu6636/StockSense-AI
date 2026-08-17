# StockSense AI — Comprehensive Codebase Audit Report (Day 1)

**Date**: August 10, 2026  
**Status**: Completed  
**Target Architecture**: Streamlit Web Application (India & US Stock Analysis Platform)

---

## 1. Executive Summary

This audit represents a complete, line-by-line inspection of the **StockSense AI** codebase. The application is structured as a multi-page Streamlit application with dedicated modular views (`views/`), a centralized styling and component library (`ui_components.py`), a data processing & market API layer (`data_service.py`), and a standalone ticker generation script (`create_tickers.py`).

While the application features strong visual styling and high functional density, the audit identified several critical architectural risks:
1. **Silent Bug Swallowing**: 18 instances of bare `except: pass` or `except Exception: pass` mask underlying API failures, type mismatches, and data structure shifts.
2. **Unbound Variables**: A severe variable scope bug in `views/stock_detail.py` where `rsi_val` is used outside a `try...except` block, leading to app crashes when technical parsing fails.
3. **Data Integrity Overwrites**: A duplicate key in `COMPETITIVE_ADVANTAGES` silently overwrites Coal India's competitive moat classification.
4. **Cloud Deployment Barriers**: Cross-origin JavaScript manipulating `parent.document` and hardcoded relative paths that break when launched from non-root working directories.

---

## 2. Complete Codebase Architecture & File Map

| File Path | Imports From Project | Functions / Classes Defined | Description & Purpose |
| :--- | :--- | :--- | :--- |
| **`app.py`** | `ui_components`, `views.home`, `views.search`, `views.compare`, `views.watchlist`, `views.trending`, `views.beginner`, `views.pro`, `views.login` | `init_session()`, `main()` | Application entry point, session state default initialization, query parameter deep-linking handler, view router, and watermark footer. |
| **`create_tickers.py`** | *None* | `get_nifty500()`, `get_sp500()` | Standalone utility script that scrapes Nifty 500 (NSE India) and S&P 500 (US) ticker lists and outputs `tickers_india.json` and `tickers_us.json`. |
| **`data_service.py`** | *None* | `load_ticker_list()`, `_precompute_search_index()`, `search_tickers()`, `_to_av_ticker()`, `_nsepython_quote()`, `_alpha_vantage_history()`, `_gnews_fetch()`, `get_stock_data_safe()`, `get_market_indices()`, `get_index_data()`, `get_stock_info_cached()`, `get_stock_data()`, `screen_stocks_with_progress()`, `compute_technicals()`, `generate_recommendation()`, `get_analyst_consensus()`, `extract_news_items()`, `get_market_news()`, `get_ai_summary()` | Core data pipeline. Manages ticker caching, yfinance live queries, multi-source fallbacks (NSEPython, Alpha Vantage, GNews), parallel multi-threaded stock screening, technical indicator calculations (RSI, MACD, Bollinger, MAs), BUY/HOLD/SELL scoring engine, and Groq LLM AI summary generator. |
| **`ui_components.py`** | `data_service` | `inject_css()`, `render_loading()`, `render_ticker_bar()`, `render_navbar()`, `render_back_button()`, `render_breadcrumb()`, `safe_pct()`, `safe_ratio()`, `metric_chip()`, `render_metric_row()`, `render_badge()`, `render_stock_header()`, `render_sebi_disclaimer()`, `apply_theme()`, `candlestick_chart()`, `volume_chart()`, `rsi_chart()`, `macd_chart()`, `bollinger_chart()`, `radar_chart()` | Central design system and visual UI library. Injects custom dark-mode CSS styling, marquee ticker bar, navigation header with mobile popover, breadcrumbs, metric chips, and Plotly interactive chart renderers. |
| **`views/__init__.py`** | *None* | *None* | Empty package initialization marker file. |
| **`views/beginner.py`** | `data_service`, `ui_components`, `views.stock_detail` | `page_beginner()` | 5-step guided wizard for beginner investors (Risk -> Sector -> Horizon -> Budget -> Stock Screener & Top Picks). |
| **`views/compare.py`** | `data_service`, `ui_components` | `page_compare()` | Side-by-side comparative analysis for up to 3 stocks, featuring normalized 3-month performance charts, metrics grid, radar scorecards, and AI verdict. |
| **`views/home.py`** | `data_service`, `ui_components` | `page_home()` | Landing page hero view, feature shortcuts, mode selection cards, and live market news feed. |
| **`views/login.py`** | `ui_components` | `is_valid_email()`, `page_login()` | User authentication page with email validation, cookie persistence integration, and Guest Mode toggle. |
| **`views/pro.py`** | `data_service`, `ui_components`, `views.stock_detail` | `page_pro()` | Advanced stock screening engine with customizable sliders for P/E, D/E, ROE, promoter %, NPM, EPS, FCF, Moat filter, and budget with tabbed results. |
| **`views/search.py`** | `data_service`, `views.stock_detail` | `page_search()` | Ticker search page with autocomplete dropdown and manual ticker symbol input. |
| **`views/stock_detail.py`**| `data_service`, `ui_components` | `safe_pct()`, `render_fundamentals()`, `render_technicals()`, `render_analyst_consensus()`, `render_news()`, `render_super_investors()`, `render_recommendation()`, `render_simulator()`, `render_ai_tab()`, `render_stock_detail()` | Master stock analysis view rendering 7 detailed analytical tabs (Fundamentals, Technicals, AI Summary, Scorecard, Analysts, Super Investors, Simulator). |
| **`views/trending.py`** | `data_service` | `page_trending()` | Live market trending view fetching top gainers and losers in batch via yfinance. |
| **`views/watchlist.py`**| *None* | `page_watchlist()` | User portfolio watchlist tracker with live price polling, gain/loss sorting, and item management. |

---

## 3. Audit Section 1: Dead Code (Defined but Never Called)

| Function Name | Defined In | Line Number | Analysis |
| :--- | :--- | :--- | :--- |
| `get_stock_data_safe` | `data_service.py` | 131 | Intended as a safe downloader wrapper around `yf.download` with fallbacks. However, `get_stock_data()` performs its own inline download logic, making `get_stock_data_safe` completely unreferenced across the codebase. |
| `safe_pct` | `ui_components.py` | 465 | Designed as a utility function to format percentage values safely. It is never called by any component or view because `views/stock_detail.py` (Line 10) re-defined its own duplicate function of the exact same name. |
| `safe_ratio` | `ui_components.py` | 482 | Designed to format ratios safely. Never invoked anywhere; `views/stock_detail.py` (Line 64) defines an inner helper `safe_ratio(v)` instead. |

---

## 4. Audit Section 2: Unused Imports

| File | Unused Import | Line Number | Risk / Description |
| :--- | :--- | :--- | :--- |
| `data_service.py` | `import time` | Line 6 | Leftover import; `time` module is never referenced in `data_service.py`. |
| `data_service.py` | `import datetime` | Line 7 | Leftover import; date handling uses native yfinance pandas Timestamps. |
| `ui_components.py` | `import plotly.express as px` | Line 5 | Unused import; all charts in `ui_components.py` use `plotly.graph_objects as go`. |
| `views/home.py` | `from data_service import load_ticker_list` | Line 3 | Unused import; `home.py` does not access the local ticker JSON lists. |
| `views/stock_detail.py` | `from ui_components import apply_theme` | Line 6 | Unused import; `apply_theme` is called internally by chart functions in `ui_components.py`. |
| `views/trending.py` | `from data_service import load_ticker_list` | Line 3 | Unused import; `trending.py` uses a hardcoded static list of 11 benchmark tickers. |

---

## 5. Audit Section 3: Variable Scope & Session State Initialisation Risks

### A. Unbound Local Variable / Crash Risk in `views/stock_detail.py`
* **File & Line**: `views/stock_detail.py:102-134`
* **Details**: Inside `render_technicals(ta, hist)`:
  ```python
  try:
      rsi_val = float(ta["rsi"].iloc[-1])
      ...
  except Exception: pass

  # Later under Tab 2 (Line 132):
  if rsi_val < 30: ...
  ```
  If `ta` has missing values or `ta["rsi"]` raises an exception during calculation, code jumps to `except Exception: pass`. `rsi_val` is **never defined**. When the user switches to the "RSI" tab, line 132 crashes the app with `UnboundLocalError: local variable 'rsi_val' referenced before assignment`.

### B. Loss of State on Rerun in `views/compare.py`
* **File & Line**: `views/compare.py:18-94`
* **Details**: The entire comparative analysis and results rendering logic is wrapped inside `if st.button("🆚 Compare Now"):`. In Streamlit, button click triggers evaluate to `True` for **one rerun cycle only**. If a user clicks an expander or interacts with any widget inside the comparison view, Streamlit reruns the script, `st.button()` evaluates to `False`, and the entire comparison view instantly disappears.

### C. State Initialisation Guard in `app.py`
* **File & Line**: `app.py:30-43`
* **Details**: `st.session_state` keys (`page`, `market_mode`, `watchlist`, etc.) are properly initialized in `init_session()`. However, `_deep_link_handled` is initialized dynamically at line 66 rather than inside `defaults`, which presents a minor inconsistency in state management.

---

## 6. Audit Section 4: Duplicate Dictionary Keys Across Codebase

| File | Line Numbers | Dictionary Name | Key | Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `data_service.py` | Line 165 & Line 175 | `COMPETITIVE_ADVANTAGES` | `"COALINDIA.NS"` | Line 165 defines `"COALINDIA.NS": "Monopoly"`. Line 175 defines `"COALINDIA.NS": "Cost Advantage"`. Python silently overwrites `"Monopoly"` with `"Cost Advantage"`, corrupting Coal India's moat classification in the screener. |

---

## 7. Audit Section 5: Bare Except & Bug Swallowing Audit

The codebase contains **18 instances** where exceptions are swallowed without logging, reporting, or fallback state flags. This masks network failures, yfinance API schema changes, and type conversion errors.

| # | File Path | Line Number | Exception Syntax | Swallowed Impact / Risk |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `data_service.py` | 141–142 | `except Exception: pass` | Swallows primary `yfinance` download failures silently in `get_stock_data_safe`. |
| 2 | `data_service.py` | 218–219 | `except Exception: pass` | Swallows index data fetch errors in `get_index_data`, resulting in zeroed market top bar values without diagnostic output. |
| 3 | `data_service.py` | 247–248 | `except Exception: pass` | Swallows fundamental `t.info` exceptions silently in `get_stock_data`. |
| 4 | `data_service.py` | 261–262 | `except Exception: pass` | Swallows `t.fast_info` lookup exceptions in `get_stock_data`. |
| 5 | `data_service.py` | 278–279 | `except Exception: pass` | Swallows 1-year historical price data fetch failures in `get_stock_data`. |
| 6 | `data_service.py` | 284–285 | `except Exception: pass` | Swallows 3-month historical price data fetch failures in `get_stock_data`. |
| 7 | `data_service.py` | 291–292 | `except Exception: pass` | Swallows raw news list retrieval errors in `get_stock_data`. |
| 8 | `data_service.py` | 303–304 | `except Exception: pass` | Swallows recommendation DataFrame retrieval errors in `get_stock_data`. |
| 9 | `data_service.py` | 352–353 | `except Exception: continue` | Silently skips stock items in `screen_stocks_with_progress` parallel executor loop on thread failure. |
| 10 | `data_service.py` | 420–421 | `except Exception: continue` | Swallows evaluation & scoring errors per stock in `screen_stocks_with_progress`, dropping stocks silently. |
| 11 | `data_service.py` | 497 | `except: pass` | Swallows RSI/MACD array index calculation errors in `generate_recommendation`. |
| 12 | `data_service.py` | 514 | `except: pass` | Swallows analyst recommendation parsing errors in `get_analyst_consensus`. |
| 13 | `data_service.py` | 538–539 | `except Exception: continue` | Swallows news dictionary normalization errors in `extract_news_items`. |
| 14 | `data_service.py` | 551–552 | `except Exception: pass` | Swallows index news fetch failures in `get_market_news`. |
| 15 | `views/stock_detail.py` | 124 | `except Exception: pass` | Swallows technical metric chip parsing in `render_technicals`, triggering downstream `UnboundLocalError`. |
| 16 | `views/stock_detail.py` | 264–265 | `except: pass` | Swallows technical float formatting in `render_ai_tab`. |
| 17 | `views/trending.py` | 50–51 | `except Exception as e: pass` | Swallows single stock price extraction errors in `page_trending`. |
| 18 | `views/trending.py` | 53–54 | `except Exception as e: pass` | Swallows batch `yf.download` errors in `page_trending`. |

---

## 8. Audit Section 6: Deployment & Environment Portability Audit

### A. Relative CWD File Path Risks
* **Files Affected**: `data_service.py:17`, `ui_components.py:233`, `create_tickers.py:52,58`
* **Issue**: File lookups use relative paths like `"tickers_india.json"` and `"real_bull.gif"`. If the Streamlit application is executed from a subfolder or external working directory (e.g. `streamlit run views/home.py`), `os.path.exists()` fails and returns empty ticker lists or breaks GIF rendering.
* **Remediation Requirement**: Replace relative strings with path resolution relative to `__file__` (`os.path.join(os.path.dirname(__file__), ...)`).

### B. Cross-Origin DOM Manipulation Restrictions
* **Files Affected**: `views/home.py:20`, `ui_components.py:438-446`
* **Issue**:
  1. `views/home.py:20`: `<button onclick="parent.document.querySelector('[data-testid=\\'baseButton-primary\\']#btn_start').click()">`
  2. `ui_components.py:438-446`: JavaScript calling `window.parent.document.querySelector(...)` to hide Streamlit sidebar controls.
* **Risk**: When deployed to Streamlit Community Cloud, HuggingFace Spaces, or embedded in an `<iframe>`, browsers enforce strict **Same-Origin Policy**. Accessing `parent.document` throws an uncatchable `SecurityError` DOM exception and breaks navigation.

### C. Cloud Server IP Blocking (NSE India)
* **Files Affected**: `create_tickers.py:9`, `data_service.py:46-67` (`nsepython`)
* **Issue**: National Stock Exchange (NSE India) blocks request headers and IP addresses originating from major cloud datacenters (AWS, GCP, Azure).
  - `create_tickers.py` scraping fails when executed in cloud environments.
  - `data_service.py` contains a guarded import for `nsepython` specifically because it fails on Streamlit Cloud servers.

---
*End of Audit Report AUDIT_DAY1.md*
