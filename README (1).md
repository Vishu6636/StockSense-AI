# 📈 StockSense AI v2.0
### Smart Stock Analysis · Risk-Aware · Built for Real Users

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# App opens at: http://localhost:8501
```

---

## ✨ Features

### 🏠 Home
- Live **Sensex, Nifty 50, Bank Nifty** ticker bar (auto-refreshes)
- Mode selector: Beginner | Pro | Trending
- Quick access to Compare & Search

### 🌱 Beginner Mode (5-Step Wizard)
1. **Risk Profile** — Low / Medium / High
2. **Sector Preference** — Tech, Banking, Pharma, etc.
3. **Investment Horizon** — Short / Medium / Long term
4. **Budget Filter** — Only shows affordable stocks
5. **Results** — Top 3 picks + Top 10 table + Simulator

### 🚀 Pro Mode
- Custom P/E, Debt/Equity, ROE, Promoter sliders
- Budget filter
- Full screener with Passed/Rejected tabs
- Score bar chart
- One-click deep analysis for any stock

### 🔥 Trending
- Live prices for 12 top NIFTY stocks
- One-click detail view

### 🔍 Stock Search (Full Analysis)
- **Fundamentals**: P/E, P/B, ROE, D/E, EPS, Growth metrics
- **Technicals**: RSI, MACD, Bollinger Bands, Moving Averages
- **Candlestick Chart** with Volume
- **Analyst Consensus** — Bullish/Bearish meter
- **Super Investors** — Who's holding (MFs, FIIs, HNIs)
- **Recommendation** — Buy / Hold / Sell with reasons
- **Simulator** — What-if investment calculator
- **News** (Pro mode)

### 🆚 Compare 3 Stocks
- Normalized price chart (3-month)
- Side-by-side 12-metric table
- Radar scorecard for each
- AI conclusion — best pick with reasoning

### 🔐 Login System
- Email login (stored locally in session)
- Google OAuth ready (wire up Firebase Auth credentials)
- "Start without login" option

---

## 🏗️ Architecture

```
app.py              ← Single-file app (modular functions)
requirements.txt    ← Dependencies
.streamlit/
  config.toml       ← Theme & server config
README.md           ← This file
```

### Code Structure (easy to extend)
```python
# DATA LAYER
get_index_data()        # Sensex, Nifty, BankNifty
get_stock_data()        # Full yfinance fetch
screen_stocks()         # NIFTY50 screener
compute_technicals()    # RSI, MACD, BB
generate_recommendation() # Buy/Hold/Sell logic
get_analyst_consensus() # Parse analyst ratings

# CHART BUILDERS
candlestick_chart()     # OHLCV candles
volume_chart()          # Volume bars
rsi_chart()             # RSI with zones
macd_chart()            # MACD + signal + histogram
bollinger_chart()       # BB + MA20
radar_chart()           # Fundamental scorecard

# UI COMPONENTS
render_ticker_bar()     # Live index bar
render_navbar()         # Top nav
render_back_button()    # Back navigation
render_stock_header()   # Price + change banner
render_fundamentals()   # Metric chips grid
render_technicals()     # Tech charts in tabs
render_analyst_consensus() # Analyst meter
render_news()           # News cards
render_super_investors() # Investor cards
render_recommendation() # Buy/Hold/Sell banner
render_simulator()      # What-if calculator

# PAGES (easy to add new ones)
page_login()
page_home()
page_beginner()
page_pro()
page_trending()
page_search()
page_compare()
```

---

## 🔧 Adding New Features

### Add a new page:
1. Define `page_myfeature()` function
2. Add a button in `page_home()` pointing to `st.session_state.page = "myfeature"`
3. Add `elif page == "myfeature": page_myfeature()` in `main()`

### Add a new metric:
- In `render_fundamentals()`, add a `metric_chip()` to the `chips` list

### Add a new stock to universe:
- Add to `NIFTY50_STOCKS` dict: `"Company Name": "TICKER.NS"`

### Firebase Google Auth (production):
1. Create Firebase project → Enable Google Auth
2. Install: `pip install firebase-admin`
3. Replace the `page_login()` Google button with Firebase Auth flow
4. Store user data in Firestore

---

## 💰 Monetization Strategy

| Tier | Price | Features |
|------|-------|---------|
| Free | ₹0 | Beginner mode, Trending, Basic search |
| Pro | ₹199/mo | Pro screener, Full technicals, Compare, News |
| Premium | ₹499/mo | Portfolio tracker, Alerts, Priority support |

**Platforms**: Gumroad (one-time ₹999 for source code), Lemonsqueezy, own website

---

## 📋 Resume Bullets

- Built **StockSense AI**, a full-stack stock analysis platform using Python, Streamlit & yfinance with live NSE/BSE data for 50+ stocks
- Implemented **multi-factor stock screener** with P/E, ROE, Debt/Equity, Promoter filters + budget-aware recommendations
- Engineered **technical analysis engine** computing RSI, MACD, Bollinger Bands with interactive Plotly visualizations
- Designed **dual-mode UX** (Beginner wizard + Pro screener) serving both novice and experienced investors
- Integrated **analyst consensus meter**, what-if investment simulator, and 3-stock comparison tool
- Applied **production-grade practices**: modular architecture, caching, error handling, SEBI disclaimers

---

## ⚠️ Disclaimer
StockSense AI is for educational purposes only. Not registered with SEBI. 
Not financial advice. Always consult a SEBI-registered advisor before investing.

---

## 📊 Interview Questions This Project Covers

1. **How did you handle live data latency?** → `@st.cache_data(ttl=300)` with graceful fallback
2. **How does your screener work?** → Multi-factor scoring: PE (25pts) + ROE (25pts) + D/E (20pts) + Promoter (15pts) + Growth (15pts)
3. **Explain RSI calculation** → 14-day Wilder smoothing of gains/losses; <30 oversold, >70 overbought
4. **How would you scale this?** → Replace yfinance with paid API, add PostgreSQL, deploy on AWS/GCP
5. **What's your recommendation logic?** → Weighted scoring across 8 fundamental + 2 technical factors
