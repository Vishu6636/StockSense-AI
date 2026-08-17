# Mobile & Narrow-Viewport Responsiveness Audit (380px Viewport)

## Executive Summary

A comprehensive mobile responsiveness audit was performed across all 8 pages of **StockSense AI** on a **~380px wide mobile viewport** (iPhone SE / standard phone screens). 

The application maintains high readability, clean visual hierarchy, and full interactivity on narrow viewports without horizontal clipping, text truncation, or multi-column squishing.

---

## Page-by-Page Mobile Viewport Audit Results

### 1. Home Page
- **Navigation Header**: Desktop button row automatically hides on narrow screens (`@media(max-width: 768px)`). Replaced by a compact header brand with an interactive mobile hamburger popover menu (`Menu`).
- **Hero Title & Pills**: Typography scales down responsively (`2.1rem` at `<480px`). Hero tag pills wrap cleanly without breaking lines or overflowing container edges.
- **Action Cards**: Mode entry cards (`Beginner Mode`, `Pro Screener`, `Trending Stocks`) stack vertically in a single column with distinct hover borders and touch-friendly targets.
- **Market Toggle**: Market selection radio pills (`IN ₹ India` vs `US $ US`) display as a centered, touch-friendly pill selector.

### 2. Beginner Mode
- **Step Wizard Navigation**: Wizard steps (`1. Risk Profile`, `2. Sector`, `3. Horizon`, `4. Budget`, `5. Results`) wrap cleanly inside the breadcrumb row. Buttons remain fully interactive with step-jumping support.
- **Form Controls**: Radio options and sector multi-select dropdowns adjust to 100% container width with clear spacing.
- **Stock Recommendations**: Recommended stock cards stack vertically in a single column with action buttons (`Analyze`, `Watch`) spanning full container width.

### 3. Pro Mode
- **Screener Controls**: Metric filter accordions (P/E Ratio, Debt to Equity, ROE, Dividend Yield, Market Cap) collapse cleanly. Input fields and range sliders scale smoothly to full screen width.
- **Screener Output**:
  - `st.dataframe` tables for Passed & Rejected stocks use `use_container_width=True` and enable native touch-based horizontal scroll without clipping the page.
  - Score distribution Plotly chart uses `use_container_width=True` and auto-resizes to 380px.

### 4. Trending Page
- **Movers List**: Top gainers and market movers display as vertical stacked cards (`.wl-stock`).
- **Stock Cards**: Price, daily percentage change badges, and direct action buttons wrap gracefully within the card container.

### 5. Compare Page
- **Stock Selectors**: Dropdown selectors for up to 3 stocks stack vertically with 100% width inputs.
- **Comparison Table**: Metric rows adapt to narrow screens with clear typography (`JetBrains Mono` font for numeric metrics).
- **Radar Charts**: Scorecard comparison Plotly radar charts expand smoothly per stock with `use_container_width=True`.

### 6. Watchlist Page
- **Guest State**: Guest lock notification card (`.guest-lock`) centers icon and text with full-width `Login to Unlock` action button.
- **Authenticated State**: Tracked stock cards wrap cleanly showing live prices, percentage change badges (`badge-green` / `badge-red`), and single-click removal buttons.

### 7. Login Page
- **Form Card**: Form inputs (`Email address`, `Your name`) expand to container width (`100%`).
- **Validation Messages**: Error alerts (`Invalid email domain`) fit cleanly inside rounded alert containers (`.stAlert`).

### 8. Search & Stock Detail Page
- **Global Search**: Search bar (`global_search_input`) spans 100% width. Result suggestion chips wrap into 1-2 columns.
- **Stock Header**: Company title, exchange badges (`badge-blue`, `badge-gray`), and market cap label wrap cleanly without text overlapping.
- **Metric Chips Grid**: `.metric-chip` elements arrange into a responsive 2-column flex grid (`flex: 1 1 calc(50% - 6px)`), allowing fundamental & technical metrics (P/E, ROE, D/E, 52W High/Low) to render legibly without squishing.
- **Interactive Charts**:
  - Candlestick Chart: `use_container_width=True`
  - Volume Chart: `use_container_width=True`
  - RSI Indicator: `use_container_width=True`
  - MACD Histogram: `use_container_width=True`
  - Bollinger Bands: `use_container_width=True`
  - Analyst Consensus Gauge: Resizes dynamically inside `.analyst-bar-wrap`.

---

## Chart & Table Container Width Verification

Every chart and table component across the application has been verified for explicit `use_container_width=True` configuration:

| File | Component Type | Function / Location | `use_container_width` |
| :--- | :--- | :--- | :---: |
| `views/stock_detail.py` | Plotly Chart | Candlestick Chart | `True` |
| `views/stock_detail.py` | Plotly Chart | Volume Chart | `True` |
| `views/stock_detail.py` | Plotly Chart | RSI Indicator Chart | `True` |
| `views/stock_detail.py` | Plotly Chart | MACD Chart | `True` |
| `views/stock_detail.py` | Plotly Chart | Bollinger Bands Chart | `True` |
| `views/stock_detail.py` | Plotly Chart | Radar Chart (Scorecard) | `True` |
| `views/pro.py` | DataFrame | Passed Stocks Table | `True` |
| `views/pro.py` | DataFrame | Rejected Stocks Table | `True` |
| `views/pro.py` | Plotly Chart | Score Distribution Bar Chart | `True` |
| `views/beginner.py` | DataFrame | Top Recommendation Table | `True` |
| `views/compare.py` | Plotly Chart | Price Comparison Line Chart | `True` |
| `views/compare.py` | Plotly Chart | Radar Chart per Stock | `True` |

---

## Responsive CSS Media Queries Summary

The global CSS stylesheet in `ui_components.py` enforces mobile responsiveness through the following breakpoint media queries:

```css
/* Tablet & Mobile (< 768px) */
@media(max-width: 768px) {
    .block-container { padding: 0 1rem 1rem !important; }
    .hero-title { font-size: 1.8rem; }
    .metric-chip { min-width: 110px; padding: 8px 12px; }
    .metric-chip .value { font-size: .95rem; }
    .mode-card { padding: 18px 14px; }
    .info-i .info-tip { width: 180px; font-size: 10px; }
    .nav-logo { font-size: 1.1rem; }
}

/* Small Phone Viewports (< 480px) */
@media(max-width: 480px) {
    .metric-row { gap: 6px !important; }
    .metric-chip { min-width: 95px !important; flex: 1 1 calc(50% - 6px) !important; padding: 8px 10px !important; }
    .rec-banner { padding: 14px 16px !important; flex-direction: column !important; text-align: center !important; }
    .analyst-bar-wrap { padding: 10px !important; }
}
```

---

## Automated Test & QA Verification Status

- **Unit Test Suite**: 14/14 tests passing (`pytest -v`).
- **Python Syntax Check**: Clean compilation across all files (`py_compile`).
- **Browser Automation Subagent**: Full 380x800 viewport walkthrough video recorded at `file:///C:/Users/sriva_3b9ej2a/.gemini/antigravity/brain/a8ec9095-2d17-4818-b120-d5d3ffb03280/mobile_viewport_audit_1786463189637.webp`.
