#  StockSense AI

A data-driven stock analysis platform that helps investors make informed decisions using real-time market data, technical indicators, and multi-factor screening.

Supports both **Indian (NSE/BSE)** and **US markets**.

---

##  Key Features

* Real-time stock data (NSE & US markets)
* Technical analysis: RSI, MACD, Bollinger Bands, Moving Averages
* Fundamental analysis: P/E, ROE, Debt/Equity, EPS, Growth metrics
* Multi-factor stock screener with scoring system
* Beginner mode (guided 5-step investment flow)
* Pro mode (advanced filters & deep analysis)
* Stock comparison (side-by-side + charts)
* Interactive charts using Plotly (candlestick, volume, indicators)
* Analyst sentiment & recommendation logic (rule-based)

---
## 📊 Data Coverage

Currently supports analysis for **500+ stocks** across Indian markets and **300 stcoks** for US markets.

Designed with a scalable architecture to expand coverage to thousands of stocks in future versions.

---
##  Tech Stack

* Python
* Streamlit
* yFinance
* Plotly
* Pandas / NumPy

---

##  Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

App runs on: `http://localhost:8501`

---

## 🔐 API Keys Setup

Create a file:

```
.streamlit/secrets.toml
```

Add:

```
ALPHA_VANTAGE_KEY="your_key_here"
GNEWS_KEY="your_key_here"
```

> These are required for fallback data and news features.

---

## Architecture

```
app.py              → Main application & routing
data_service.py     → Data fetching & API fallbacks
ui_components.py    → UI rendering components
views/              → Feature pages (Home, Search, Compare, etc.)
requirements.txt    → Dependencies
```

---

##  System Design Highlights

* **API Fallback Strategy**: yFinance → Alpha Vantage → NSEPython
* **Caching Optimization**: `@st.cache_data` to reduce API calls & latency
* **Modular Structure**: Clear separation of UI, data, and logic
* **Rule-Based Recommendation Engine**: Multi-factor scoring (fundamental + technical)

---

##  Future Scope

* Integration with brokerage APIs (Zerodha, Alpaca) for **buy/sell execution**
* Portfolio tracking and P&L analytics
* AI-based personalized investment recommendations
* Real-time alerts and risk management system

---

##  Disclaimer

This project is for educational purposes only.
Not financial advice. Not SEBI registered.
Always consult a certified financial advisor before investing.

---

##  Author

Built as a real-world, production-style project focusing on scalability, data handling, and user-centric design.
