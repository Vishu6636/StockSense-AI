import json
import os
import streamlit as st
import yfinance as yf
import pandas as pd
import time
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── DYNAMIC ASSETS ──
@st.cache_data(ttl=86400)
def load_ticker_list(market: str):
    filename = "tickers_india.json" if market == "🇮🇳 India" else "tickers_us.json"
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=86400)
def _precompute_search_index(market: str):
    """Precompute lowercase fields once per market for fast search."""
    tickers = load_ticker_list(market)
    for t in tickers:
        t["_name_lower"] = t["name"].lower()
        t["_ticker_lower"] = t["ticker"].lower()
    return tickers

def search_tickers(query: str, market: str):
    tickers = _precompute_search_index(market)
    q = query.lower()
    return [t for t in tickers if q in t["_name_lower"] or q in t["_ticker_lower"]][:10]

# ── TICKER FORMAT HELPERS ──
def _to_av_ticker(ticker: str) -> str:
    """RELIANCE.NS → RELIANCE.BSE, RELIANCE.BO → RELIANCE.BSE, AAPL → AAPL"""
    if ticker.endswith(".NS"):
        return ticker.replace(".NS", ".BSE")
    if ticker.endswith(".BO"):
        return ticker.replace(".BO", ".BSE")
    return ticker

# ── FALLBACK 1: NSEPython (Indian market, no API key, no rate limit) ──
# NOTE: nsepython is NOT in requirements.txt because it breaks on Streamlit Cloud
# (NSE blocks cloud server IPs). It works fine locally if installed.
# The import is guarded so the app gracefully skips this fallback on cloud.
def _nsepython_quote(ticker: str) -> dict:
    """Live Indian stock quote. Returns {c, h, l, o, pc} or {}. No key needed."""
    if not ticker.endswith(".NS") and not ticker.endswith(".BO"):
        return {}
    try:
        from nsepython import nse_eq
        symbol = ticker.replace(".NS", "").replace(".BO", "")
        data = nse_eq(symbol)
        price_info = data.get("priceInfo", {})
        intra = price_info.get("intraDayHighLow", {})
        return {
            "c": price_info.get("lastPrice", 0),
            "pc": price_info.get("previousClose", 0),
            "h": intra.get("max", 0),
            "l": intra.get("min", 0),
            "o": price_info.get("open", 0),
        }
    except Exception:
        return {}


# ── FALLBACK 2: Alpha Vantage (price history, 25 calls/day free) ──
@st.cache_data(ttl=3600)
def _alpha_vantage_history(ticker: str) -> pd.DataFrame:
    """OHLCV history fallback. Indian stocks use BSE format. Returns DataFrame or empty."""
    api_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")
    if not api_key:
        return pd.DataFrame()
    av_ticker = _to_av_ticker(ticker)
    try:
        r = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": av_ticker,
                "outputsize": "full",
                "apikey": api_key
            },
            timeout=10
        )
        ts = r.json().get("Time Series (Daily Adjusted)")
        if not ts:
            return pd.DataFrame()
        df = pd.DataFrame.from_dict(ts, orient="index")
        df = df.rename(columns={
            "1. open": "Open", "2. high": "High",
            "3. low": "Low", "4. close": "Close",
            "6. volume": "Volume"
        })[["Open", "High", "Low", "Close", "Volume"]]
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# ── FALLBACK 3: GNews (news, 100 calls/day free, covers Indian sources) ──
@st.cache_data(ttl=1800)
def _gnews_fetch(query: str, country: str = "in") -> list:
    """News fallback. Covers ET, NDTV Business, Moneycontrol etc. Returns list or []."""
    api_key = st.secrets.get("GNEWS_KEY", "")
    if not api_key:
        return []
    try:
        r = requests.get(
            "https://gnews.io/api/v4/search",
            params={"q": query, "lang": "en", "country": country, "max": 6, "token": api_key},
            timeout=8
        )
        return [
            {
                "title": a.get("title", ""),
                "publisher": a.get("source", {}).get("name", ""),
                "link": a.get("url", "#"),
                "time": a.get("publishedAt", ""),
            }
            for a in r.json().get("articles", [])
        ]
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_stock_data_safe(ticker, period="1y"):
    # Primary: yfinance
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if not df.empty:
            return df
        if ticker.endswith(".NS"):
            df = yf.download(ticker.replace(".NS", ".BO"), period=period, progress=False, auto_adjust=True)
            if not df.empty:
                return df
    except Exception:
        pass
    # Fallback 1: NSEPython (Indian only, gets latest quote as single row)
    q = _nsepython_quote(ticker)
    if q.get("c", 0) > 0:
        # NSEPython gives live quote only, not history — return empty to let caller handle
        pass
    # Fallback 2: Alpha Vantage history
    df = _alpha_vantage_history(ticker)
    if not df.empty:
        return df
    return pd.DataFrame()

# ── INDICES FOR MARKET TOP BAR ──
INDICES_INDIA = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
INDICES_US = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DOW JONES": "^DJI"}

def get_market_indices():
    market = st.session_state.get("market_mode", "🇮🇳 India")
    return INDICES_INDIA if market == "🇮🇳 India" else INDICES_US


# ── FALLBACK/MOCK DATA FOR ADVANTAGES/INVESTORS ──
COMPETITIVE_ADVANTAGES = {
    "COALINDIA.NS":"Monopoly","IRCTC.NS":"Monopoly","HAL.NS":"Monopoly","CONCOR.NS":"Monopoly",
    "BEL.NS":"Oligopoly","MAZDOCK.NS":"Oligopoly","COCHINSHIP.NS":"Oligopoly",
    "BHARTIARTL.NS":"Duopoly","INDIGO.NS":"Duopoly",
    "ASIANPAINT.NS":"Brand Power","TITAN.NS":"Brand Power","NESTLEIND.NS":"Brand Power",
    "HINDUNILVR.NS":"Brand Power","BRITANNIA.NS":"Brand Power","COLPAL.NS":"Brand Power",
    "PIDILITIND.NS":"Brand Power","PAGEIND.NS":"Brand Power","DMART.NS":"Brand Power",
    "MARUTI.NS":"Brand Power","EICHERMOT.NS":"Brand Power","TRENT.NS":"Brand Power",
    "TCS.NS":"Switching Cost","INFY.NS":"Switching Cost","HCLTECH.NS":"Switching Cost",
    "HDFCBANK.NS":"Network Effect","ICICIBANK.NS":"Network Effect","SBIN.NS":"Network Effect",
    "ZOMATO.NS":"Network Effect","NAUKRI.NS":"Network Effect","POLICYBZR.NS":"Network Effect",
    "RELIANCE.NS":"Conglomerate Moat","ADANIENT.NS":"Conglomerate Moat",
    "NTPC.NS":"Cost Advantage","POWERGRID.NS":"Cost Advantage","COALINDIA.NS":"Cost Advantage",
    "ULTRACEMCO.NS":"Scale Advantage","LT.NS":"Scale Advantage","JSWSTEEL.NS":"Scale Advantage",
    "BAJFINANCE.NS":"Distribution Moat","BAJAJFINSV.NS":"Distribution Moat",
    "SUNPHARMA.NS":"R&D Moat","DRREDDY.NS":"R&D Moat","DIVISLAB.NS":"R&D Moat",
    # US Examples
    "AAPL":"Brand Power", "MSFT":"Switching Cost", "GOOGL":"Network Effect", "NVDA":"Monopoly"
}

SUPER_INVESTORS = {
    "RELIANCE.NS":[{"name":"LIC of India","type":"Insurance","holding":"6.74%","value":"₹94,200 Cr"},{"name":"SBI Mutual Fund","type":"Mutual Fund","holding":"2.11%","value":"₹29,500 Cr"}],
    "TCS.NS":[{"name":"Tata Sons","type":"Promoter Group","holding":"72.30%","value":"₹9,89,000 Cr"},{"name":"LIC of India","type":"Insurance","holding":"3.92%","value":"₹53,700 Cr"}],
    "HDFCBANK.NS":[{"name":"HDFC Ltd (merged)","type":"Promoter","holding":"26.00%","value":"₹3,12,000 Cr"},{"name":"Mirae Asset MF","type":"Mutual Fund","holding":"2.86%","value":"₹34,300 Cr"}],
    "INFY.NS":[{"name":"NR Narayana Murthy & Family","type":"Promoter","holding":"14.48%","value":"₹74,200 Cr"},{"name":"LIC of India","type":"Insurance","holding":"6.21%","value":"₹31,900 Cr"}],
    "ICICIBANK.NS":[{"name":"LIC of India","type":"Insurance","holding":"6.29%","value":"₹57,400 Cr"},{"name":"Govt of Singapore","type":"FII / Sovereign","holding":"4.01%","value":"₹36,600 Cr"}],
    "SBIN.NS":[{"name":"Govt of India","type":"Promoter","holding":"57.51%","value":"₹3,11,000 Cr"},{"name":"LIC of India","type":"Insurance","holding":"9.20%","value":"₹49,800 Cr"}],
    "AAPL":[{"name":"Vanguard Group","type":"Mutual Fund","holding":"8.3%","value":"$230B"}],
    "MSFT":[{"name":"BlackRock","type":"Mutual Fund","holding":"7.1%","value":"$205B"}]
}
DEFAULT_INVESTORS = [
    {"name":"LIC of India (or equivalent inst.)","type":"Institutional","holding":"~2–7%","value":"Varies"},
    {"name":"Mutual Funds","type":"Mutual Fund","holding":"~1–3%","value":"Large Cap"},
    {"name":"Govt of Singapore / Sovereign","type":"Sovereign Wealth","holding":"~0.5–2%","value":"FII"},
]

# ── DATA FUNCTIONS ──
@st.cache_data(ttl=900)
def get_index_data(market_indices: dict):
    results = {}
    for name, ticker in market_indices.items():
        fetched = False
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d", interval="1d")
            if len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                curr = float(hist["Close"].iloc[-1])
                chg = curr - prev
                results[name] = {"price": curr, "change": chg, "pct": (chg / prev) * 100}
                fetched = True
            elif len(hist) == 1:
                results[name] = {"price": float(hist["Close"].iloc[-1]), "change": 0, "pct": 0}
                fetched = True
        except Exception:
            pass
        if not fetched:
            # NSEPython fallback for Indian indices
            q = _nsepython_quote(ticker)
            if q.get("c", 0) > 0:
                curr, prev = q["c"], q.get("pc", q["c"])
                chg = curr - prev
                results[name] = {"price": curr, "change": chg, "pct": ((chg / prev) * 100) if prev else 0}
            else:
                results[name] = {"price": 0, "change": 0, "pct": 0}
    return results

@st.cache_data(ttl=1800)
def get_stock_info_cached(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info
    except Exception:
        return {}

@st.cache_data(ttl=1200)
def get_stock_data(ticker):
    try:
        t = yf.Ticker(ticker)
        
        info = {}
        try:
            info = t.info
        except Exception:
            pass
            
        if not info:
            try:
                fi = t.fast_info
                info = {
                    "currentPrice": getattr(fi, "last_price", 0),
                    "previousClose": getattr(fi, "previous_close", 0),
                    "marketCap": getattr(fi, "market_cap", 0),
                    "fiftyTwoWeekHigh": getattr(fi, "year_high", 0),
                    "fiftyTwoWeekLow": getattr(fi, "year_low", 0),
                    "longName": ticker
                }
            except Exception:
                pass
                
        if not info and (ticker.endswith(".NS") or ticker.endswith(".BO")):
            q = _nsepython_quote(ticker)
            if q.get("c"):
                info = {
                    "currentPrice": q.get("c"),
                    "previousClose": q.get("pc"),
                    "fiftyTwoWeekHigh": q.get("h"),
                    "fiftyTwoWeekLow": q.get("l"),
                    "longName": ticker
                }

        hist_1y = None
        try:
            hist_1y = t.history(period="1y")
        except Exception:
            pass
            
        hist_3m = None
        try:
            hist_3m = t.history(period="3mo")
        except Exception:
            pass

        # News: yfinance first, GNews fallback
        raw_news = []
        try:
            raw_news = t.news if hasattr(t, "news") and t.news else []
        except Exception:
            pass
        news = extract_news_items(raw_news)
        if not news:
            company_name = info.get("longName") or info.get("shortName") or ticker
            is_indian = ticker.endswith(".NS") or ticker.endswith(".BO")
            news = _gnews_fetch(company_name, country="in" if is_indian else "us")

        # Analyst recs
        recs = None
        try:
            recs = t.recommendations
        except Exception:
            pass

        # Price history fallback
        if hist_1y is None or (hasattr(hist_1y, "empty") and hist_1y.empty):
            hist_1y = _alpha_vantage_history(ticker)
        if hist_3m is None or (hasattr(hist_3m, "empty") and hist_3m.empty):
            av_full = _alpha_vantage_history(ticker)
            hist_3m = av_full.iloc[-63:] if not av_full.empty else pd.DataFrame()

        return {"info": info, "hist_1y": hist_1y, "hist_3m": hist_3m,
                "news": news, "recs": recs, "ticker": ticker}
    except Exception:
        return None

def screen_stocks_with_progress(stocks_dict, max_pe=25, max_de=1.0, min_roe=10,
                                  min_promoter=40, min_npm=0, min_eps=0,
                                  fcf_positive=False, adv_filter=None, budget=None):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    total = len(stocks_dict)
    est_time = max(2, total * 0.05)
    # Using dynamic currency and handling limit sizes
    market = st.session_state.get("market_mode", "🇮🇳 India")
    currency = "₹" if market == "🇮🇳 India" else "$"
    
    st.markdown(f"<div style='color:#9E9E9E;font-size:12px;margin-bottom:8px'>⏱️ Estimated time: ~{est_time:.0f}s for {total} stocks</div>", unsafe_allow_html=True)

    # Pre-fetch all stock info in parallel using ThreadPoolExecutor
    status_text.markdown(f"<div style='color:#9E9E9E;font-size:13px'>📊 Pre-fetching data for {total} stocks...</div>", unsafe_allow_html=True)
    info_cache = {}
    tickers_list = list(stocks_dict.items())

    def _fetch_info(item):
        name, ticker = item
        try:
            return name, ticker, get_stock_info_cached(ticker)
        except Exception:
            return name, ticker, {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_fetch_info, item): item for item in tickers_list}
        done_count = 0
        for future in as_completed(futures):
            done_count += 1
            progress_bar.progress(done_count / total)
            try:
                name, ticker, info = future.result()
                if info:
                    info_cache[(name, ticker)] = info
            except Exception:
                continue

    # Process results from cache (no repeated API calls)
    for name, ticker in tickers_list:
        info = info_cache.get((name, ticker))
        if not info:
            continue
        try:
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

            # FIX 7 — Budget filter: skip stocks above budget
            if budget and price and price > budget:
                continue

            pe = info.get("trailingPE") or info.get("forwardPE") or 999
            
            # handle some string values occasionally returned
            if isinstance(pe, str): pe = 999
            
            de = info.get("debtToEquity", 999) or 999
            if de > 100: de = de / 100
            
            roe = (info.get("returnOnEquity") or 0) * 100
            promoter = info.get("heldPercentInsiders", 0) * 100
            market_cap = info.get("marketCap", 0)
            sales_growth = (info.get("revenueGrowth") or 0) * 100
            profit_growth = (info.get("earningsGrowth") or 0) * 100
            div_yield = (info.get("dividendYield") or 0) * 100
            pb = info.get("priceToBook") or 0
            eps = info.get("trailingEps") or 0
            npm = (info.get("profitMargins") or 0) * 100
            fcf = info.get("freeCashflow") or 0
            adv = COMPETITIVE_ADVANTAGES.get(ticker, "None")

            if adv_filter and adv_filter != "Any" and adv != adv_filter:
                continue
            if fcf_positive and fcf <= 0:
                continue

            score = 0
            if 0 < pe < max_pe: score += 20
            if de < max_de: score += 15
            if roe >= min_roe: score += 20
            if promoter >= min_promoter: score += 10
            if sales_growth > 10: score += 10
            if profit_growth > 10: score += 10
            if div_yield > 1: score += 5
            if npm >= min_npm and min_npm > 0: score += 5
            if eps >= min_eps and min_eps > 0: score += 5

            shares_can_buy = int(budget / price) if budget and price > 0 else None
            
            mcap_val = round(market_cap/1e7,0) if market == "🇮🇳 India" else round(market_cap/1e9,2) # Cr for India, B for US
            fcf_val = round(fcf/1e7,0) if market == "🇮🇳 India" else round(fcf/1e9,2)

            results.append({
                "Name":name,"Ticker":ticker,"Price":price,"P/E":round(pe,1),
                "D/E":round(de,2),"ROE%":round(roe,1),"Promoter%":round(promoter,1),
                "Sales Growth%":round(sales_growth,1),"Profit Growth%":round(profit_growth,1),
                "Div Yield%":round(div_yield,2),"P/B":round(pb,2),"EPS":round(eps,2),
                "NPM%":round(npm,1),f"FCF ({'Cr' if market == '🇮🇳 India' else 'B'})":fcf_val if fcf else 0,
                "Advantage":adv,f"Market Cap ({'Cr' if market == '🇮🇳 India' else 'B'})":mcap_val if market_cap else 0,
                "Score":score,"Shares with Budget":shares_can_buy,
                "Status":"✅ Pass" if score >= 35 else "❌ Reject",
            })
        except Exception:
            continue
    progress_bar.empty()
    status_text.empty()
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values("Score", ascending=False).reset_index(drop=True)
    return df


def compute_technicals(hist):
    if hist is None or hist.empty or len(hist) < 30:
        return {}
    close = hist["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - signal
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    bb_upper = ma20 + 2*std20
    bb_lower = ma20 - 2*std20
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean() if len(close) >= 200 else pd.Series([None]*len(close))
    support = close.rolling(20).min()
    resistance = close.rolling(20).max()
    vol = hist["Volume"]
    vol_sma5 = vol.rolling(5).mean()
    vol_sma20 = vol.rolling(20).mean()
    return {"rsi":rsi,"macd":macd,"signal":signal,"macd_hist":macd_hist,
            "ma20":ma20,"ma50":ma50,"ma200":ma200,"bb_upper":bb_upper,"bb_lower":bb_lower,
            "support":support,"resistance":resistance,"vol_sma5":vol_sma5,"vol_sma20":vol_sma20}


def generate_recommendation(info, technicals):
    score = 0
    reasons = []
    pe = info.get("trailingPE") or info.get("forwardPE") or 0
    if isinstance(pe, str): pe = 0
    roe = (info.get("returnOnEquity") or 0) * 100
    de = (info.get("debtToEquity") or 0)
    if de > 100: de = de / 100
    sales_growth = (info.get("revenueGrowth") or 0) * 100
    profit_growth = (info.get("earningsGrowth") or 0) * 100
    promoter = (info.get("heldPercentInsiders") or 0) * 100
    div_yield = (info.get("dividendYield") or 0) * 100
    npm = (info.get("profitMargins") or 0) * 100

    if 0 < pe < 20: score += 2; reasons.append("✅ Low P/E — may be undervalued")
    elif pe > 40: score -= 2; reasons.append("⚠️ High P/E — heavy growth priced in")
    if roe > 15: score += 2; reasons.append("✅ Strong ROE — efficient capital use")
    elif roe < 5: score -= 1; reasons.append("⚠️ Low ROE — efficiency concern")
    if de < 0.5: score += 1; reasons.append("✅ Low debt — financially stable")
    elif de > 2: score -= 2; reasons.append("❌ High debt — repayment risk")
    if sales_growth > 15: score += 2; reasons.append("✅ Strong revenue growth")
    elif sales_growth < 0: score -= 2; reasons.append("❌ Revenue declining")
    if profit_growth > 20: score += 2; reasons.append("✅ High profit growth")
    elif profit_growth < 0: score -= 1; reasons.append("⚠️ Profit fell recently")
    if promoter > 50: score += 1; reasons.append("✅ High promoter confidence")
    if div_yield > 2: score += 1; reasons.append("✅ Good dividend yield")
    if npm > 15: score += 1; reasons.append("✅ Healthy profit margins")

    if technicals:
        try:
            rsi_val = float(technicals["rsi"].iloc[-1])
            if rsi_val < 35: score += 2; reasons.append(f"✅ RSI {rsi_val:.0f} — oversold (good entry)")
            elif rsi_val > 70: score -= 1; reasons.append(f"⚠️ RSI {rsi_val:.0f} — overbought")
            macd_val = float(technicals["macd"].iloc[-1])
            sig_val = float(technicals["signal"].iloc[-1])
            if macd_val > sig_val: score += 1; reasons.append("✅ MACD bullish crossover")
            else: reasons.append("⚠️ MACD below signal")
        except: pass

    if score >= 5: return "BUY","buy","🟢",reasons
    elif score >= 1: return "HOLD","hold","🟡",reasons
    else: return "SELL","sell","🔴",reasons


def get_analyst_consensus(recs):
    if recs is None or (hasattr(recs,'empty') and recs.empty): return None
    try:
        if hasattr(recs,'columns') and "period" in recs.columns:
            latest = recs[recs["period"]=="0m"]
            if latest.empty: latest = recs.iloc[-1:]
            row = latest.iloc[-1]
            total = int(row.get("strongBuy",0)+row.get("buy",0)+row.get("hold",0)+row.get("sell",0)+row.get("strongSell",0))
            if total == 0: return None
            return {"strongBuy":int(row.get("strongBuy",0)),"buy":int(row.get("buy",0)),"hold":int(row.get("hold",0)),"sell":int(row.get("sell",0)),"strongSell":int(row.get("strongSell",0)),"total":total}
    except: pass
    return None


def extract_news_items(raw_news):
    items = []
    if not raw_news: return items
    for item in raw_news[:6]:
        try:
            if isinstance(item, dict) and "content" in item:
                c = item["content"]
                items.append({
                    "title": c.get("title", "No title"),
                    "publisher": c.get("provider", {}).get("displayName", "") if isinstance(c.get("provider"), dict) else "",
                    "link": c.get("canonicalUrl", {}).get("url", "#") if isinstance(c.get("canonicalUrl"), dict) else "#",
                    "time": c.get("pubDate", ""),
                })
            elif isinstance(item, dict):
                items.append({
                    "title": item.get("title", "No title"),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", "#"),
                    "time": item.get("providerPublishTime", ""),
                })
        except Exception:
            continue
    return items

@st.cache_data(ttl=1800)
def get_market_news(market="🇮🇳 India"):
    index_ticker = "^NSEI" if market == "🇮🇳 India" else "^GSPC"
    try:
        t = yf.Ticker(index_ticker)
        raw = t.news if hasattr(t, "news") and t.news else []
        news = extract_news_items(raw)[:6]
        if news:
            return news
    except Exception:
        pass
    # GNews fallback — Indian business sources: ET, Moneycontrol, NDTV Business
    query = "Nifty NSE Sensex India stock market" if market == "🇮🇳 India" else "S&P 500 NASDAQ US stock market"
    country = "in" if market == "🇮🇳 India" else "us"
    return _gnews_fetch(query, country=country)

@st.cache_data(ttl=900)
def get_ai_summary(ticker, company_name, info_json_str, tech_json_str, currency="₹"):
    try:
        from groq import Groq
    except ImportError:
        return "⚠️ AI module not installed. Run: pip install groq"
        
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return "⚠️ No API key configured. Add GROQ_API_KEY to .streamlit/secrets.toml"
        client = Groq(api_key=api_key)
        prompt = f"""You are a concise stock market analyst. Analyze {company_name} ({ticker}).

Key data: {info_json_str}
Technicals: {tech_json_str}

Write exactly 4 paragraphs with these bold headings:
**📊 Company Overview** — What the company does and current market position
**📈 Bull vs Bear Case** — Key reasons to be optimistic vs cautious
**👤 Who Should Consider** — Ideal investor profile for this stock
**⏰ Buy/Sell/Hold Now?** — Is NOW a good time to buy, sell, or hold? Be specific about entry points and timing signals.

Keep it under 250 words. Use {currency} for prices where relevant. Be conversational, avoid jargon. Give actionable advice."""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI analysis temporarily unavailable: {str(e)[:100]}"
