# StockSense AI

A stock analysis platform I built to make sense of the Indian and US markets in one place — technical indicators, a screener, portfolio tracking, and AI-generated summaries, without needing five different tabs open.

**Live app:** [stocksense-ai-jgbzps3lsbrsdybsjyupss.streamlit.app](https://stocksense-ai-jgbzps3lsbrsdybsjyupss.streamlit.app/)

## Why I built this

I wanted a tool that didn't just dump numbers on a screen but actually explained what they meant — especially for someone newer to investing. That's where the Beginner mode and the "explain like I'm new" toggle came from. At the same time, I wanted enough depth (RSI, MACD, Bollinger Bands, multi-factor screening) that it's actually useful for more serious analysis too, not just a toy.

It covers both NSE/BSE stocks (India) and major US equities, and you can switch between them with one toggle.

## What it does

- **Home** — live index tracking (Nifty 50, Sensex, Bank Nifty, S&P 500, Nasdaq)
- **Beginner mode** — a guided 5-step flow based on risk profile, sector, horizon, and budget, plus an SIP/lumpsum calculator
- **Pro screener** — filter by P/E, Debt/Equity, ROE, promoter holding, with a full market scan or a faster top-50 scan
- **Trending** — daily rotating list of liquid large-cap movers, plus a sector heatmap
- **Stock detail** — fundamentals, technical charts, insider/promoter ownership breakdown, analyst consensus, sector peer comparison, and a Groq-powered AI summary
- **Compare** — put 2–3 stocks side by side across 12 metrics with a radar chart
- **Portfolio** — paste your holdings and get P&L, sector concentration, and a risk rating
- **Watchlist** — save stocks across your session

## Tech stack

Python, Streamlit, yFinance for market data, Plotly for charts, and Groq (Llama 3.3) for the AI-generated stock summaries.

## Project structure

```
StockSense-AI/
├── app.py                # entry point, routing, session state
├── data_service.py       # data fetching, technical indicators, screener logic
├── ui_components.py      # design system, navbar, ticker bar, chart factories
├── views/                # one file per page (home, pro, compare, portfolio, etc.)
├── tests/                # pytest suite
├── tickers_india.json    # NSE/BSE ticker list
├── tickers_us.json       # US ticker list
└── requirements.txt
```

## Running it locally

```bash
git clone https://github.com/Vishu6636/StockSense-AI.git
cd StockSense-AI
pip install -r requirements.txt
streamlit run app.py
```

If you want the AI summaries and fallback data sources to work, add your own keys in `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_key_here"
ALPHA_VANTAGE_KEY = "your_key_here"
GNEWS_KEY = "your_key_here"
```

Everything else — prices, fundamentals, technical indicators, the screener, the SIP calculator — works fine without any keys, since it's all pulled through yFinance.

## Tests

There's a small pytest suite covering the technical indicator math and the recommendation scoring logic:

```bash
pytest tests/
```

## Disclaimer

This is a personal/educational project. It's not registered with SEBI or the SEC, and nothing here is financial advice — I built it to learn and to have something useful for myself, do your own research before acting on anything it shows you.

## License

MIT — see [LICENSE](LICENSE).
