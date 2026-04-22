# StockSense AI

A data-driven stock analysis platform designed to help investors make informed decisions using real-time market data, technical indicators, and multi-factor screening.

Supports both Indian (NSE/BSE) and US markets.

---

## Problem Statement

Retail investors often rely on scattered tools for stock analysis, making it difficult to combine technical indicators, fundamental metrics, and market insights in one place. This leads to inefficient decision-making and information overload.

StockSense AI solves this by providing a unified platform for structured, data-driven stock analysis.

---

## Key Features

* Real-time stock data (NSE & US markets)
* Technical analysis: RSI, MACD, Bollinger Bands, Moving Averages
* Fundamental analysis: P/E, ROE, Debt/Equity, EPS, Growth metrics
* Multi-factor stock screener with scoring system
* Beginner mode (guided 5-step investment flow)
* Pro mode (advanced filters & deep analysis)
* Stock comparison (side-by-side + charts)
* Interactive charts using Plotly (candlestick, volume, indicators)
* Rule-based analyst sentiment & recommendation system

---

## Data Coverage

Supports analysis for 500+ Indian stocks and 300+ US stocks.

Built with a scalable architecture designed to expand coverage to thousands of stocks with minimal changes.

---

## Tech Stack

* Python
* Streamlit
* yFinance
* Plotly
* Pandas / NumPy

---

## Setup and Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

App runs on: http://localhost:8501

---

## API Keys Setup

Create a file:

.streamlit/secrets.toml

Add:

* ALPHA_VANTAGE_KEY="your_key_here" & 
* GNEWS_KEY="your_key_here"

Required for fallback data and news features.

---

## Architecture

- **app.py**: Main application and routing
- **data_service.py**: Data fetching and API fallbacks
- **ui_components.py**: UI rendering components
- **views/**: Feature pages (Home, Search, Compare, etc.)
- **requirements.txt**: Dependencies

---

## System Design Highlights

* API fallback strategy: yFinance → Alpha Vantage → NSEPython
* Caching optimization using st.cache_data
* Modular architecture (UI, data, logic separation)
* Multi-factor rule-based recommendation engine

---

## Future Scope

* Integration with brokerage APIs (Zerodha, Alpaca) for buy/sell execution
* Portfolio tracking and P&L analytics
* AI-based personalized investment recommendations
* Real-time alerts and risk management system

---

## Disclaimer

This project is for educational purposes only.
Not financial advice. Not SEBI registered.
Always consult a certified financial advisor before investing.

---

## Author

Built as a production-style project focusing on scalability, performance, and user-centric design.
