# 📈 StockSense AI v4.0
### Smart Stock Intelligence & Multi-Market Analysis Platform · Built for Real Investors

---

## 🌟 Overview

**StockSense AI** is a production-grade, data-driven stock intelligence and portfolio analytics web application designed to help retail and professional investors make informed decisions. It delivers real-time market data, technical indicators, multi-factor stock screening, portfolio health analytics, and AI-generated insights across both **Indian (NSE/BSE - 500+ stocks)** and **US (300+ stocks)** equity markets.

Built with **Python**, **Streamlit**, **yFinance**, **Plotly**, and **Groq (Llama 3.3)**, StockSense AI features a dark glassmorphic design system tailored for fast, intuitive financial analysis.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Vishu6636/StockSense-AI.git
cd StockSense-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit app
streamlit run app.py
```

App will automatically launch at: `http://localhost:8501`

---

## 🔐 API Keys Setup (Optional for AI & Fallbacks)

Create a `.streamlit/secrets.toml` file in the project root to configure optional API keys:

```toml
# Required for AI-powered stock summaries (Groq Llama 3.3)
GROQ_API_KEY = "gsk_your_groq_api_key_here"

# Fallback market data provider
ALPHA_VANTAGE_KEY = "your_alpha_vantage_key_here"

# Fallback financial news provider
GNEWS_KEY = "your_gnews_key_here"
```

> **Note**: Core functionality (price data, fundamental metrics, technical indicators, screeners, SIP calculator, portfolio analyzer) works out-of-the-box using `yfinance` without needing API keys.

---

## ✨ Key Features & Navigation

StockSense AI features a modular 9-page view routing system:

### 1. 🏠 Home Page (`views/home.py`)
- **Live Ticker Bar**: Real-time market tracking for Nifty 50, Sensex, Bank Nifty, S&P 500, Nasdaq, and Dow Jones.
- **Dual-Market Toggle**: One-click instant switching between **IN ₹ India** and **US $ US** equity universes.
- **Market Overview Cards**: Top market indices with 1-day percentage change and direction indicators.

### 2. 🌱 Beginner Mode (`views/beginner.py`)
- **Guided 5-Step Investment Wizard**: Filters stocks based on Risk Profile (Low/Medium/High), Sector Preferences, Investment Horizon, and Budget.
- **Top Picks**: Surfaces top 3 recommended stocks with share allocation recommendations.
- **💡 SIP & Wealth Growth Calculator**: Interactive tool simulating long-term Systematic Investment Plans (SIP) or Lumpsum wealth accumulation with inflation-adjusted Plotly area charts.

### 3. 🚀 Pro Screener (`views/pro.py`)
- **Multi-Factor Filter Engine**: Customizable sliders for P/E Ratio, Debt/Equity, ROE %, and Promoter Holding %.
- **Quick Scan (Top 50)** vs. **Full Market Scan**: Fast performance options.
- **Score Breakdown Bar Chart**: Visual scoring breakdown for passed stocks (0–100 scale).

### 4. 🔥 Daily Trending & Sector Heatmap (`views/trending.py`)
- **Highlighted Daily Movers**: Rotating selection of top liquid large-cap stocks ranked by 1-day % change.
- **🔥 Real-Time Sector Performance Heatmap**: Aggregated sector card dashboard (IT, Banking, Pharma, Energy, Tech, etc.) showing top gainers and sector averages.

### 5. 🔍 Stock Search & Single-Stock Intelligence (`views/stock_detail.py`)
- **Company Essentials**: Fundamentals grid (P/E, P/B, ROE, Debt/Equity, Dividend Yield, EPS, Sales & Profit Growth, 52-Week High/Low).
- **💡 Explain Like I'm New (ELI5) Toggle**: Educational toggle explaining financial metrics in simple terms.
- **👔 Insider & Promoter Ownership Tracker**: Promoter vs. Institutional vs. Public ownership breakdown with insider confidence scoring.
- **📉 Interactive Technical Analysis**: Candlestick OHLCV chart, Volume, RSI (14), MACD, and Bollinger Bands using Plotly.
- **🤖 Groq Llama 3.3 AI Analysis**: Deep AI stock breakdown with bullish/bearish catalysts and valuation assessment.
- **🎯 Analyst Consensus Meter**: Visual sentiment needle parsing analyst ratings.
- **🔍 Auto-Suggested Sector Peers**: Head-to-head quick comparison cards for top sector competitors.
- **What-If Investment Simulator**: Compound growth calculator for custom investment horizons.

### 6. 🆚 Head-to-Head Comparison (`views/compare.py`)
- **Side-by-Side Analysis**: Compare 2–3 stocks simultaneously.
- **Normalized 3-Month Price Performance Chart**: Multi-line growth chart starting from baseline 100.
- **12-Metric Comparison Table**: Deep comparison across fundamental & technical metrics.
- **Radar Scorecard**: Multi-axis spider chart comparing fundamental balance.

### 7. 💼 Portfolio Import & Health Risk Analyzer (`views/portfolio.py`)
- **CSV Import Tool**: Paste custom stock holdings (`Ticker, Shares, Buy Price`).
- **Interactive Sample Portfolios**: Pre-populated test portfolios for both Indian and US markets.
- **Automated Health Dashboard**: Calculates Total Invested, Current Value, Net P&L (₹/$ and %), Weighted Portfolio P/E, and Health/Risk Rating.
- **Sector Concentration Donut & Stock Allocation Bar Charts**.

### 8. ⭐ Watchlist (`views/watchlist.py`)
- Save and track stocks across session state.

### 9. 🔐 Login & Session Persistence (`views/login.py`)
- Seamless local session authentication and cookie-based persistence (`streamlit-cookies-controller`).

---

## 🏗️ System Architecture & Code Structure

```
StockSense-AI/
├── app.py                      # Main entry point, router, session state & theme injection
├── data_service.py             # Data fetching, yfinance layer, technical calculations, screeners, AI engine
├── ui_components.py            # Design system, CSS tokens, navbar, ticker bar, Plotly chart factories, ELI5 cards
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development & testing dependencies
├── real_bull.gif               # Loading animation asset
├── LICENSE                     # MIT Open Source License
├── README.md                   # System documentation
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   ├── config.toml             # Dark theme palette & Streamlit server options
│   └── secrets.toml            # API keys (Groq, Alpha Vantage, GNews)
├── views/                      # Modular view page components
│   ├── home.py                 # Landing page & market cards
│   ├── beginner.py             # 5-Step wizard + SIP calculator
│   ├── pro.py                  # Advanced multi-factor screener
│   ├── trending.py             # Daily movers & sector heatmap
│   ├── search.py               # Ticker search router
│   ├── stock_detail.py         # Full single-stock detail view
│   ├── compare.py              # 3-Stock comparison view
│   ├── portfolio.py            # Portfolio CSV analyzer
│   ├── watchlist.py            # Saved watchlist manager
│   └── login.py                # Login & session state manager
├── tests/                      # Automated unit test suite (pytest)
│   ├── test_data_service.py    # Core data & technical indicator tests
│   └── test_new_features.py    # Phase 4 feature tests (SIP, Heatmap, ELI5, Insider, Peers, Portfolio)
├── tickers_india.json          # 500+ Indian ticker mappings (NSE/BSE)
└── tickers_us.json             # 300+ US ticker mappings (NASDAQ/NYSE)
```

---

## 🧪 Testing & Verification

StockSense AI includes a complete `pytest` test suite covering technical indicator logic, recommendation engine scoring, multi-factor screening, portfolio analytics, and wealth math.

To run the test suite:

```bash
pytest tests/
```

**Test Coverage Output**:
```text
============================= 20 passed in 10.19s =============================
```

---

## 🛡️ System Design & Technical Highlights

1. **Multi-Tier API Fallback Strategy**:
   - Primary: `yfinance` batch download & cached ticker info.
   - Secondary: `Alpha Vantage` API fallback for price data.
   - Fallback scrapers: Resilient handling when external rate-limits occur.
2. **Performance Caching**: Extensive use of `@st.cache_data(ttl=300)` for financial data and `@st.cache_data(ttl=3600)` for static universe lists.
3. **Vanilla CSS Design System**: Custom glassmorphism cards, dark background palette (`#0E1117`), typography stack (`Inter` & `JetBrains Mono`), and custom metric badges.
4. **Resilient Error Boundaries**: Defensive fallbacks for missing financial data, delisted tickers, or offline API endpoints.

---

## 📋 Resume & Portfolio Highlights

- **Full-Stack Financial Engineering**: Designed and built a multi-market stock analytics application in Python using Streamlit, yFinance, Plotly, and Groq LLMs.
- **Quantitative Multi-Factor Screener**: Implemented rule-based scoring algorithms evaluating P/E ratios, ROE, Debt/Equity, EPS growth, and promoter holdings.
- **Interactive Data Visualization**: Created 10+ custom Plotly chart types (Candlestick OHLCV, MACD histogram, RSI bounds, Radar scorecards, Portfolio sector donuts, Wealth area projections).
- **AI Financial Summaries**: Integrated Groq Llama 3.3 API to generate structured stock analysis summaries based on real-time fundamental and technical inputs.
- **Enterprise Testing & Code Standards**: Maintained modular separation of concerns with 100% passing `pytest` test coverage.

---

## ⚠️ Disclaimer

**StockSense AI is for educational and informational purposes only.** It is **not** registered with SEBI (Securities and Exchange Board of India) or the SEC (U.S. Securities and Exchange Commission). Nothing on this platform constitutes financial, investment, or legal advice. Always conduct your own research or consult a certified financial advisor before making investment decisions.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
