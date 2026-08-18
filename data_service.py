import json
import os
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Removed custom session as it interferes with yfinance's internal crumb management.

# ── DYNAMIC ASSETS ──
@st.cache_data(ttl=86402)
def load_ticker_list(market: str):
    filename = "tickers_india.json" if "India" in market else "tickers_us.json"
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=86402)
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
@st.cache_data(ttl=3602)
def _alpha_vantage_history(ticker: str) -> pd.DataFrame:
    """OHLCV history fallback. Indian stocks use BSE format. Returns DataFrame or empty."""
    api_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")
    if not api_key or api_key == "your-alpha-vantage-key-here":
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
@st.cache_data(ttl=1802)
def _gnews_fetch(query: str, country: str = "in") -> list:
    """News fallback. Covers ET, NDTV Business, Moneycontrol etc. Returns list or []."""
    api_key = st.secrets.get("GNEWS_KEY", "")
    if not api_key or api_key == "your-gnews-key-here":
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

# ── INDICES FOR MARKET TOP BAR ──
INDICES_INDIA = {"SENSEX": "^BSESN", "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
INDICES_US = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DOW JONES": "^DJI"}

def get_market_indices():
    market = st.session_state.get("market_mode", "🇮🇳 India")
    return INDICES_INDIA if "India" in market else INDICES_US


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
    "NTPC.NS":"Cost Advantage","POWERGRID.NS":"Cost Advantage",
    "ULTRACEMCO.NS":"Scale Advantage","LT.NS":"Scale Advantage","JSWSTEEL.NS":"Scale Advantage",
    "BAJFINANCE.NS":"Distribution Moat","BAJAJFINSV.NS":"Distribution Moat",
    "SUNPHARMA.NS":"R&D Moat","DRREDDY.NS":"R&D Moat","DIVISLAB.NS":"R&D Moat",
    # US Examples
    "AAPL":"Brand Power", "MSFT":"Switching Cost", "GOOGL":"Network Effect", "NVDA":"Monopoly"
}

import datetime

SUPER_INVESTORS = {}  # Deprecated stub for backwards compatibility
DEFAULT_INVESTORS = []

@st.cache_data(ttl=86400)
def get_us_institutional_holders(ticker: str) -> list:
    """Fetches real top institutional holders for US tickers from yfinance."""
    if not ticker or ticker.endswith(".NS") or ticker.endswith(".BO"):
        return []
    holders = []
    try:
        t = yf.Ticker(ticker)
        inst = t.institutional_holders
        if inst is not None and hasattr(inst, "empty") and not inst.empty:
            for _, row in inst.head(6).iterrows():
                h_name = str(row.get("Holder", "Unknown"))
                pct = row.get("pctHeld")
                shares = row.get("Shares")
                val = row.get("Value")
                
                if pct is not None and isinstance(pct, (int, float)) and pct == pct and pct > 0:
                    h_str = f"{pct * 100:.2f}%"
                elif shares and isinstance(shares, (int, float)) and shares == shares:
                    h_str = f"{shares:,.0f} shares"
                else:
                    h_str = "Institutional"
                    
                if val and isinstance(val, (int, float)) and val == val and val > 0:
                    v_str = f"${val/1e9:.2f}B" if val >= 1e9 else f"${val/1e6:.1f}M"
                else:
                    v_str = ""
                    
                holders.append({
                    "name": h_name,
                    "type": "Institutional Holder",
                    "holding": h_str,
                    "value": v_str
                })
    except Exception:
        pass
    return holders

# ── DATA FUNCTIONS ──
@st.cache_data(ttl=300)
def get_index_data(market_indices: dict):
    results = {}
    for name, ticker in market_indices.items():
        fetched = False
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d", interval="1d")
            if hist is not None and len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                curr = float(hist["Close"].iloc[-1])
                chg = curr - prev
                pct = (chg / prev * 100) if prev > 0 else 0
                results[name] = {"price": curr, "change": chg, "pct": pct}
                fetched = True
        except Exception:
            pass

        if not fetched:
            try:
                t = yf.Ticker(ticker)
                fi = getattr(t, "fast_info", None)
                if fi:
                    curr = float(getattr(fi, "last_price", 0) or 0)
                    prev = float(getattr(fi, "previous_close", 0) or 0)
                    if curr > 0:
                        chg = curr - prev if prev > 0 else 0
                        pct = (chg / prev * 100) if prev > 0 else 0
                        results[name] = {"price": curr, "change": chg, "pct": pct}
                        fetched = True
            except Exception:
                pass

        if not fetched:
            q = _nsepython_quote(ticker)
            if q.get("c", 0) > 0:
                curr, prev = q["c"], q.get("pc", q["c"])
                chg = curr - prev
                results[name] = {"price": curr, "change": chg, "pct": ((chg / prev) * 100) if prev else 0}
                fetched = True

        if not fetched:
            default_prices = {
                "^BSESN": 77500.0,
                "^NSEI": 24200.0,
                "^NSEBANK": 57000.0,
                "^GSPC": 5400.0,
                "^IXIC": 17000.0,
                "^DJI": 40000.0,
            }
            price = default_prices.get(ticker, 0.0)
            results[name] = {"price": price, "change": 0.0, "pct": 0.0}

    return results

def _alpha_vantage_overview(ticker: str) -> dict:
    """Fetches fundamental overview data from Alpha Vantage API as a secondary fallback."""
    api_key = st.secrets.get("ALPHA_VANTAGE_KEY") or st.secrets.get("ALPHA_VANTAGE_API_KEY", "")
    if not api_key:
        return {}
    sym = ticker.replace(".NS", "").replace(".BO", "")
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={sym}&apikey={api_key}"
    try:
        r = requests.get(url, timeout=4.0)
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, dict) and "Name" in data:
                def _parse(v):
                    if v is None or v == "None" or v == "-" or v == "None":
                        return None
                    try:
                        f = float(v)
                        return None if f != f else f
                    except (ValueError, TypeError):
                        return None

                pe = _parse(data.get("PERatio"))
                pb = _parse(data.get("PriceToBookRatio"))
                roe = _parse(data.get("ReturnOnEquityTTM"))
                eps = _parse(data.get("EPS"))
                div_y = _parse(data.get("DividendYield"))
                sales_g = _parse(data.get("QuarterlyRevenueGrowthYOY"))
                earnings_g = _parse(data.get("QuarterlyEarningsGrowthYOY"))
                profit_m = _parse(data.get("ProfitMargin"))
                de = _parse(data.get("DebtToEquityTTM"))
                mcap = _parse(data.get("MarketCapitalization"))
                hi52 = _parse(data.get("52WeekHigh"))
                lo52 = _parse(data.get("52WeekLow"))

                return {
                    "longName": data.get("Name", ticker),
                    "sector": data.get("Sector", "N/A"),
                    "trailingPE": pe,
                    "priceToBook": pb,
                    "returnOnEquity": roe,
                    "debtToEquity": de,
                    "dividendYield": div_y,
                    "revenueGrowth": sales_g,
                    "earningsGrowth": earnings_g,
                    "profitMargins": profit_m,
                    "trailingEps": eps,
                    "marketCap": mcap,
                    "fiftyTwoWeekHigh": hi52,
                    "fiftyTwoWeekLow": lo52,
                    "_source": "AlphaVantage"
                }
    except Exception:
        pass
    return {}

def _fetch_stock_info_with_fallback(ticker: str) -> dict:
    """
    Fetches ticker info using a 2-attempt retry on yfinance, 
    falls back to Alpha Vantage OVERVIEW, and finally fast_info.
    Sets _fallback_mode = True if fundamental fields are missing.
    """
    info = {}
    
    # 1. Retry up to 2 attempts on yfinance t.info (handles transient 429 rate-limits)
    for attempt in range(2):
        try:
            t = yf.Ticker(ticker)
            res = t.info
            if res and isinstance(res, dict) and len(res) > 5 and any(k in res for k in ["trailingPE", "marketCap", "currentPrice"]):
                info = dict(res)
                break
        except Exception:
            pass
        if attempt == 0:
            time.sleep(1.0)

    # 2. Secondary Fallback: Alpha Vantage OVERVIEW if yfinance info is empty or missing fundamentals
    has_fund = info and any(info.get(k) is not None for k in ["trailingPE", "returnOnEquity", "dividendYield"])
    if not has_fund:
        av_info = _alpha_vantage_overview(ticker)
        if av_info:
            if info:
                for k, v in av_info.items():
                    if info.get(k) is None and v is not None:
                        info[k] = v
            else:
                info = av_info

    # 3. Final Fallback: fast_info if price/mcap/52w range is still missing
    if not info or not info.get("currentPrice"):
        try:
            t = yf.Ticker(ticker)
            fi = getattr(t, "fast_info", None)
            if fi:
                price = getattr(fi, "last_price", 0) or getattr(fi, "previous_close", 0) or 0
                prev = getattr(fi, "previous_close", 0) or 0
                mcap = getattr(fi, "market_cap", 0) or 0
                hi = getattr(fi, "year_high", 0) or 0
                lo = getattr(fi, "year_low", 0) or 0
                if not info:
                    info = {}
                info.update({
                    "currentPrice": price if price > 0 else info.get("currentPrice", 0),
                    "previousClose": prev if prev > 0 else info.get("previousClose", 0),
                    "marketCap": mcap if mcap > 0 else info.get("marketCap", 0),
                    "fiftyTwoWeekHigh": hi if hi > 0 else info.get("fiftyTwoWeekHigh", 0),
                    "fiftyTwoWeekLow": lo if lo > 0 else info.get("fiftyTwoWeekLow", 0),
                    "longName": info.get("longName") or ticker
                })
        except Exception:
            pass

    # 4. Final NSEPython quote fallback for Indian stocks if currentPrice is still 0
    if (not info or not info.get("currentPrice")) and (ticker.endswith(".NS") or ticker.endswith(".BO")):
        q = _nsepython_quote(ticker)
        if q.get("c"):
            if not info:
                info = {}
            info.update({
                "currentPrice": q.get("c"),
                "previousClose": q.get("pc"),
                "fiftyTwoWeekHigh": q.get("h"),
                "fiftyTwoWeekLow": q.get("l"),
                "longName": ticker
            })

    # Flag _fallback_mode = True if fundamental metrics (P/E, ROE, P/B) could not be retrieved
    if not any(info.get(k) is not None for k in ["trailingPE", "forwardPE", "priceToBook", "returnOnEquity", "debtToEquity"]):
        info["_fallback_mode"] = True

    return info

@st.cache_data(ttl=1802)
def get_stock_info_cached(ticker):
    return _fetch_stock_info_with_fallback(ticker)

@st.cache_data(ttl=1202)
def get_stock_data(ticker):
    try:
        t = yf.Ticker(ticker)
        info = _fetch_stock_info_with_fallback(ticker)

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
    # Yahoo blocks bursts of fundamental-data requests from shared cloud IPs.
    est_time = max(4, total * 0.18)
    # Using dynamic currency and handling limit sizes
    market = st.session_state.get("market_mode", "🇮🇳 India")
    currency = "₹" if "India" in market else "$"
    
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

    # A small pool avoids Yahoo Finance throttling that caused partial scans.
    with ThreadPoolExecutor(max_workers=3) as executor:
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
            def number(value, default=None):
                """Return a finite numeric value without discarding valid zeroes."""
                try:
                    value = float(value)
                    return value if value == value else default
                except (TypeError, ValueError):
                    return default

            price = number(info.get("currentPrice"))
            if price is None:
                price = number(info.get("regularMarketPrice"), 0)

            # FIX 7 — Budget filter: skip stocks above budget
            if budget and price and price > budget:
                continue

            pe = number(info.get("trailingPE"))
            if pe is None:
                pe = number(info.get("forwardPE"))

            de = number(info.get("debtToEquity"))
            if de is not None and de > 5:
                de = de / 100
            
            raw_roe = info.get("returnOnEquity")
            if raw_roe is not None and isinstance(raw_roe, (int, float)) and raw_roe == raw_roe:
                roe = float(raw_roe) * 100
            elif info.get("trailingEps") and info.get("bookValue") and info.get("bookValue") > 0:
                roe = (float(info.get("trailingEps")) / float(info.get("bookValue"))) * 100
            else:
                roe = None

            promoter_raw = number(info.get("heldPercentInsiders"))
            # Yahoo often omits promoter data for NSE stocks; it is not a fail.
            promoter = promoter_raw * 100 if promoter_raw and promoter_raw > 0 else None
            market_cap = number(info.get("marketCap"), 0)
            sales_growth = number(info.get("revenueGrowth"))
            sales_growth = sales_growth * 100 if sales_growth is not None else None
            profit_growth = number(info.get("earningsGrowth"))
            profit_growth = profit_growth * 100 if profit_growth is not None else None

            raw_dy = info.get("dividendYield")
            if raw_dy is not None and isinstance(raw_dy, (int, float)) and raw_dy == raw_dy:
                tdy = info.get("trailingAnnualDividendYield")
                if raw_dy < 0.2 and tdy is not None and isinstance(tdy, (int, float)) and abs(raw_dy - tdy) < 0.001:
                    div_yield = float(raw_dy) * 100
                else:
                    div_yield = float(raw_dy)
            elif info.get("trailingAnnualDividendYield"):
                div_yield = float(info.get("trailingAnnualDividendYield")) * 100
            elif info.get("dividendRate") and price and price > 0:
                div_yield = (float(info.get("dividendRate")) / float(price)) * 100
            else:
                div_yield = 0.0

            pb = number(info.get("priceToBook"), 0)
            eps = number(info.get("trailingEps"), 0)
            npm_raw = number(info.get("profitMargins"))
            npm = npm_raw * 100 if npm_raw is not None else None
            fcf = number(info.get("freeCashflow"), 0)
            adv = COMPETITIVE_ADVANTAGES.get(ticker, "None")

            if adv_filter and adv_filter != "Any" and adv != adv_filter:
                continue
            if fcf_positive and fcf <= 0:
                continue

            # Qualify against metrics Yahoo actually returned. Previously,
            # missing promoter/fundamental data was counted as a failed filter.
            checks = []
            if pe is not None and pe > 0: checks.append((20, pe <= max_pe))
            if de is not None and de >= 0: checks.append((15, de <= max_de))
            if roe is not None: checks.append((20, roe >= min_roe))
            if promoter is not None: checks.append((10, promoter >= min_promoter))
            if min_npm > 0 and npm is not None: checks.append((5, npm >= min_npm))
            if min_eps > 0 and eps is not None: checks.append((5, eps >= min_eps))

            available_weight = sum(weight for weight, _ in checks)
            matched_weight = sum(weight for weight, matched in checks if matched)
            qualification = (matched_weight / available_weight * 100) if available_weight else 0
            bonus = sum((10 if sales_growth is not None and sales_growth > 10 else 0,
                         10 if profit_growth is not None and profit_growth > 10 else 0,
                         5 if div_yield > 1 else 0))
            score = min(100, round(qualification * 0.8 + bonus, 1))
            # Do not recommend a company when fewer than two independent
            # fundamentals are available.
            is_pass = len(checks) >= 2 and qualification >= 60
            # Keep the existing status/rendering contract (Pass is score >= 35)
            # while deriving qualification from available data above.
            score = max(score, 35) if is_pass else min(score, 34.9)
            npm = npm if npm is not None else 0

            shares_can_buy = int(budget / price) if budget and price > 0 else None
            
            mcap_val = round(market_cap/1e7,0) if "India" in market else round(market_cap/1e9,2) # Cr for India, B for US
            fcf_val = round(fcf/1e7,0) if "India" in market else round(fcf/1e9,2)

            results.append({
                "Name":name,"Ticker":ticker,"Price":price,"P/E":round(pe,1) if pe is not None else 0,
                "D/E":round(de,2) if de is not None else 0,"ROE%":round(roe,1) if roe is not None else 0,"Promoter%":round(promoter,1) if promoter is not None else 0,
                "Sales Growth%":round(sales_growth,1) if sales_growth is not None else 0,"Profit Growth%":round(profit_growth,1) if profit_growth is not None else 0,
                "Div Yield%":round(div_yield,2),"P/B":round(pb,2),"EPS":round(eps,2),
                "NPM%":round(npm,1),f"FCF ({'Cr' if 'India' in market else 'B'})":fcf_val if fcf else 0,
                "Advantage":adv,f"Market Cap ({'Cr' if 'India' in market else 'B'})":mcap_val if market_cap else 0,
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
    
    raw_roe = info.get("returnOnEquity")
    if raw_roe is not None and isinstance(raw_roe, (int, float)) and raw_roe == raw_roe:
        roe = float(raw_roe) * 100
    elif info.get("trailingEps") and info.get("bookValue") and info.get("bookValue") > 0:
        roe = (float(info.get("trailingEps")) / float(info.get("bookValue"))) * 100
    else:
        roe = 0.0

    de = (info.get("debtToEquity") or 0)
    if de > 5: de = de / 100
    sales_growth = (info.get("revenueGrowth") or 0) * 100
    profit_growth = (info.get("earningsGrowth") or 0) * 100
    promoter = (info.get("heldPercentInsiders") or 0) * 100
    
    raw_dy = info.get("dividendYield")
    if raw_dy is not None and isinstance(raw_dy, (int, float)) and raw_dy == raw_dy:
        tdy = info.get("trailingAnnualDividendYield")
        if raw_dy < 0.2 and tdy is not None and isinstance(tdy, (int, float)) and abs(raw_dy - tdy) < 0.001:
            div_yield = float(raw_dy) * 100
        else:
            div_yield = float(raw_dy)
    elif info.get("trailingAnnualDividendYield"):
        div_yield = float(info.get("trailingAnnualDividendYield")) * 100
    else:
        div_yield = 0.0
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
        except (KeyError, IndexError, TypeError, ValueError): pass

    if score >= 5: return "BUY","buy","🟢",reasons
    elif score >= 0: return "HOLD","hold","🟡",reasons
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
    except (KeyError, IndexError, TypeError, ValueError, AttributeError): pass
    return None


def _parse_news_datetime(val):
    """Safely parses news publication timestamp (ISO string or UNIX integer) into UTC datetime."""
    if not val:
        return None
    if isinstance(val, (int, float)):
        try:
            return datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
        except Exception:
            return None
    if isinstance(val, str):
        val = val.strip()
        try:
            val_clean = val.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(val_clean)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            pass
        try:
            ts = float(val)
            return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        except Exception:
            pass
    return None

def extract_news_items(raw_news):
    if not raw_news:
        return []
    
    parsed = []
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now_utc - datetime.timedelta(days=45)
    
    for item in raw_news:
        try:
            if isinstance(item, dict) and "content" in item:
                c = item["content"]
                raw_time = c.get("pubDate", "")
                dt = _parse_news_datetime(raw_time)
                parsed.append({
                    "title": c.get("title", "No title"),
                    "publisher": c.get("provider", {}).get("displayName", "") if isinstance(c.get("provider"), dict) else "",
                    "link": c.get("canonicalUrl", {}).get("url", "#") if isinstance(c.get("canonicalUrl"), dict) else "#",
                    "time": raw_time,
                    "dt": dt
                })
            elif isinstance(item, dict):
                raw_time = item.get("providerPublishTime") or item.get("time", "")
                dt = _parse_news_datetime(raw_time)
                parsed.append({
                    "title": item.get("title", "No title"),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", "#"),
                    "time": raw_time,
                    "dt": dt
                })
        except Exception:
            continue
            
    # Sort descending by publish date (items with valid dt first)
    parsed.sort(
        key=lambda x: x["dt"] if x["dt"] is not None else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
        reverse=True
    )
    
    # Filter items within 45-day window
    recent = [item for item in parsed if item["dt"] is not None and item["dt"] >= cutoff]
    
    if len(recent) >= 3:
        return recent[:6]
    elif parsed:
        # Fallback to sorted list if fewer than 3 recent items exist
        return parsed[:6]
    return []

@st.cache_data(ttl=1802)
def get_market_news(market="🇮🇳 India"):
    index_ticker = "^NSEI" if "India" in market else "^GSPC"
    try:
        t = yf.Ticker(index_ticker)
        raw = t.news if hasattr(t, "news") and t.news else []
        news = extract_news_items(raw)[:6]
        if news:
            return news
    except Exception:
        pass
    # GNews fallback — Indian business sources: ET, Moneycontrol, NDTV Business
    query = "Nifty NSE Sensex India stock market" if "India" in market else "S&P 500 NASDAQ US stock market"
    country = "in" if "India" in market else "us"
    return _gnews_fetch(query, country=country)

@st.cache_data(ttl=902)
def get_ai_summary(ticker, company_name, info_json_str, tech_json_str, currency="₹"):
    try:
        from groq import Groq
    except ImportError:
        return "⚠️ AI module not installed. Run: pip install groq"
        
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key or api_key == "your-groq-api-key-here":
            return "⚠️ No API key configured. Add GROQ_API_KEY to .streamlit/secrets.toml"
        client = Groq(api_key=api_key, timeout=15.0)
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


# ═══════════════════════════════════════════
#  PHASE 4: NEW FEATURE DATA SERVICES
# ═══════════════════════════════════════════

def calculate_sip_lumpsum(monthly_investment=5000, lumpsum=0, annual_return_pct=12.0, tenure_years=10, inflation_pct=6.0):
    """Calculates year-by-year projected wealth for SIP and/or Lumpsum investment."""
    months = tenure_years * 12
    r_monthly = (annual_return_pct / 100) / 12
    
    records = []
    total_sip_invested = 0.0
    lumpsum_invested = float(lumpsum)
    
    current_sip_val = 0.0
    current_lumpsum_val = float(lumpsum)
    
    for yr in range(1, tenure_years + 1):
        for m in range(12):
            current_sip_val = (current_sip_val + monthly_investment) * (1 + r_monthly)
            total_sip_invested += monthly_investment
            current_lumpsum_val = current_lumpsum_val * (1 + r_monthly)
            
        total_invested = total_sip_invested + lumpsum_invested
        total_wealth = current_sip_val + current_lumpsum_val
        est_returns = max(0.0, total_wealth - total_invested)
        real_wealth = total_wealth / ((1 + (inflation_pct / 100)) ** yr)
        
        records.append({
            "Year": yr,
            "Total Invested": round(total_invested, 2),
            "Estimated Wealth": round(total_wealth, 2),
            "Wealth Gain": round(est_returns, 2),
            "Inflation Adjusted": round(real_wealth, 2)
        })
        
    df = pd.DataFrame(records)
    final_invested = total_sip_invested + lumpsum_invested
    final_wealth = current_sip_val + current_lumpsum_val
    final_gain = max(0.0, final_wealth - final_invested)
    final_real = final_wealth / ((1 + (inflation_pct / 100)) ** tenure_years)
    
    return {
        "summary": {
            "total_invested": round(final_invested, 2),
            "final_wealth": round(final_wealth, 2),
            "total_gain": round(final_gain, 2),
            "real_wealth": round(final_real, 2),
            "wealth_multiplier": round(final_wealth / final_invested, 2) if final_invested > 0 else 1.0
        },
        "df": df
    }


@st.cache_data(ttl=1802)
def get_sector_heatmap_data(market_mode="🇮🇳 India"):
    """Computes sector performance summary using pre-cached tickers list and yfinance prices."""
    tickers = load_ticker_list(market_mode)
    if not tickers:
        return pd.DataFrame()
        
    sector_groups = {}
    for t in tickers:
        sec = t.get("sector") or "Other"
        sector_groups.setdefault(sec, []).append(t)
        
    results = []
    for sector, stock_list in sector_groups.items():
        changes = []
        top_gainer = ""
        top_gainer_pct = -999.0
        
        sample_stocks = stock_list[:6]
        for s in sample_stocks:
            sym = s.get("ticker")
            s_name = s.get("name")
            try:
                info = get_stock_info_cached(sym)
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                prev = info.get("previousClose") or price
                if price and prev and prev > 0:
                    pct = ((price - prev) / prev) * 100
                    changes.append(pct)
                    if pct > top_gainer_pct:
                        top_gainer_pct = pct
                        top_gainer = f"{s_name} ({sym.split('.')[0]})"
            except Exception:
                continue
                
        if changes:
            avg_pct = sum(changes) / len(changes)
            results.append({
                "Sector": sector,
                "Stocks": len(stock_list),
                "AvgChange%": round(avg_pct, 2),
                "Top Gainer": top_gainer if top_gainer else "N/A",
                "TopGainer%": round(top_gainer_pct, 2) if top_gainer_pct > -900 else 0.0,
                "Status": "🟢 Bullish" if avg_pct > 0.5 else ("🔴 Bearish" if avg_pct < -0.5 else "🟡 Neutral")
            })
            
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values("AvgChange%", ascending=False).reset_index(drop=True)
    return df


def get_eli5_explanation(metric_name: str, value) -> dict:
    """Translates technical financial metrics into plain, simple explanations for beginner mode."""
    m = metric_name.upper().strip()
    try:
        val_num = float(value) if value is not None else None
    except (ValueError, TypeError):
        val_num = None
        
    explanations = {
        "P/E": {
            "title": "Price to Earnings Ratio",
            "desc": "How much money you pay for every ₹1 (or $1) of annual company profit.",
            "status": "Bargain / Undervalued" if (val_num and 0 < val_num < 18) else ("Fairly Priced" if (val_num and val_num <= 30) else "High Valuation"),
            "badge_color": "green" if (val_num and val_num < 20) else ("gold" if (val_num and val_num <= 35) else "red")
        },
        "P/B": {
            "title": "Price to Book Value",
            "desc": "Stock price relative to asset value if liquidating the company today.",
            "status": "Below Asset Value" if (val_num and 0 < val_num < 1.0) else ("Standard Asset Value" if (val_num and val_num <= 4.0) else "High Asset Multiple"),
            "badge_color": "green" if (val_num and val_num < 1.5) else "gold"
        },
        "D/E": {
            "title": "Debt to Equity Ratio",
            "desc": "Measures reliance on borrowed loans vs owner's invested money.",
            "status": "Low Debt Risk" if (val_num is not None and val_num < 0.5) else ("Moderate Debt" if (val_num is not None and val_num <= 1.0) else "High Debt Burden"),
            "badge_color": "green" if (val_num is not None and val_num < 0.5) else ("gold" if (val_num is not None and val_num <= 1.0) else "red")
        },
        "ROE": {
            "title": "Return on Equity",
            "desc": "Efficiency of management converting shareholder funds into net profit.",
            "status": "High Capital Efficiency" if (val_num and val_num >= 15) else "Moderate Efficiency",
            "badge_color": "green" if (val_num and val_num >= 15) else "gold"
        },
        "RSI": {
            "title": "Relative Strength Index",
            "desc": "Momentum score (0-100) showing if stock is overbought or oversold.",
            "status": "Oversold (Entry Zone)" if (val_num and val_num < 35) else ("Overbought (Caution)" if (val_num and val_num > 70) else "Neutral Momentum"),
            "badge_color": "green" if (val_num and val_num < 40) else ("red" if (val_num and val_num > 70) else "gray")
        },
        "MACD": {
            "title": "Moving Average Trend",
            "desc": "Moving average momentum direction for price action.",
            "status": "Bullish Trend" if str(value).lower() in ["buy", "bullish", "true", "up"] else "Bearish / Neutral",
            "badge_color": "green" if str(value).lower() in ["buy", "bullish", "true", "up"] else "gold"
        },
        "DIV YIELD": {
            "title": "Dividend Yield",
            "desc": "Annual cash rewards paid directly to shareholders as % of stock price.",
            "status": "Generous Cash Payout" if (val_num and val_num >= 2.0) else "Modest Payout",
            "badge_color": "green" if (val_num and val_num >= 2.0) else "gray"
        }
    }
    
    return explanations.get(m, {
        "title": metric_name,
        "desc": f"Technical indicator: {value}",
        "status": "Overview",
        "badge_color": "gray"
    })


def get_insider_ownership_analysis(ticker: str, info: dict) -> dict:
    """Parses promoter percentage, institutional holding, and calculates Insider Confidence."""
    raw_promoter = info.get("heldPercentInsiders") or 0
    raw_inst = info.get("heldPercentInstitutions") or 0
    
    promoter_pct = round(raw_promoter * 100, 1) if raw_promoter else 0.0
    inst_pct = round(raw_inst * 100, 1) if raw_inst else 0.0
    public_pct = max(0.0, round(100.0 - (promoter_pct + inst_pct), 1))
    
    score = 50
    reasons = []
    
    if promoter_pct > 60:
        score += 35
        reasons.append("🔥 High promoter skin in the game (>60%)")
    elif promoter_pct >= 40:
        score += 20
        reasons.append("✅ Healthy promoter holding (40-60%)")
    elif promoter_pct > 0 and promoter_pct < 20:
        score -= 20
        reasons.append("⚠️ Low promoter holding (<20%)")
        
    if inst_pct > 25:
        score += 15
        reasons.append("🏛️ Strong institutional backing (>25%)")
        
    score = max(10, min(100, score))
    rating = "High Promoter Skin in Game" if score >= 75 else ("Balanced Ownership" if score >= 50 else "Low Insider Commitment")
    
    return {
        "promoter_pct": promoter_pct,
        "inst_pct": inst_pct,
        "public_pct": public_pct,
        "confidence_score": score,
        "rating": rating,
        "reasons": reasons
    }


@st.cache_data(ttl=3602)
def get_sector_peers_cached(ticker: str, market_mode: str = "🇮🇳 India") -> list:
    """Finds up to 3 sector peers for a given stock ticker from loaded market tickers list."""
    tickers = load_ticker_list(market_mode)
    if not tickers:
        return []
        
    target = None
    for t in tickers:
        if t["ticker"] == ticker:
            target = t
            break
            
    target_sector = target.get("sector") if target else None
    
    peers = []
    for t in tickers:
        if t["ticker"] != ticker:
            if target_sector and t.get("sector") == target_sector:
                peers.append(t)
            elif not target_sector:
                peers.append(t)
                
    return peers[:3]


def analyze_portfolio_holdings(holdings_list: list, market_mode: str = "🇮🇳 India") -> dict:
    """Calculates portfolio valuation, profit/loss, weighted P/E, sector breakdown, and health rating."""
    if not holdings_list:
        return {"empty": True}
        
    currency = "₹" if "India" in market_mode else "$"
    total_invested = 0.0
    total_current_val = 0.0
    sector_values = {}
    valid_stocks = []
    
    weighted_pe_num = 0.0
    pe_weight_total = 0.0
    
    for h in holdings_list:
        sym = str(h.get("ticker", "")).strip().upper()
        if not sym:
            continue
        shares = float(h.get("shares", 0))
        buy_p = float(h.get("buy_price", 0))
        if shares <= 0:
            continue
            
        info = get_stock_info_cached(sym)
        curr_p = info.get("currentPrice") or info.get("regularMarketPrice") or buy_p
        sec = info.get("sector") or "Other"
        pe = info.get("trailingPE") or info.get("forwardPE")
        
        invested = shares * buy_p
        current = shares * curr_p
        pnl = current - invested
        pnl_pct = ((curr_p - buy_p) / buy_p * 100) if buy_p > 0 else 0.0
        
        total_invested += invested
        total_current_val += current
        sector_values[sec] = sector_values.get(sec, 0.0) + current
        
        if pe and isinstance(pe, (int, float)) and pe > 0:
            weighted_pe_num += pe * current
            pe_weight_total += current
            
        stock_name = info.get("longName") or info.get("shortName") or sym
        valid_stocks.append({
            "ticker": sym,
            "name": stock_name,
            "shares": shares,
            "buy_price": buy_p,
            "current_price": curr_p,
            "invested": round(invested, 2),
            "current_value": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "sector": sec,
            "pe": round(pe, 1) if pe else "N/A"
        })
        
    if not valid_stocks:
        return {"empty": True}
        
    total_pnl = total_current_val - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
    avg_pe = (weighted_pe_num / pe_weight_total) if pe_weight_total > 0 else None
    
    num_sectors = len(sector_values)
    max_sector_share = (max(sector_values.values()) / total_current_val * 100) if total_current_val > 0 else 100.0
    
    if num_sectors >= 4 and max_sector_share < 40:
        health_status = "🟢 Well Diversified & Low Risk"
        risk_rating = "Low Risk"
    elif max_sector_share > 60 or num_sectors <= 2:
        health_status = "🔴 High Sector Concentration Risk"
        risk_rating = "High Risk"
    else:
        health_status = "🟡 Moderately Diversified"
        risk_rating = "Moderate Risk"
        
    sec_records = [{"Sector": s, "Value": round(v, 2), "Share%": round(v / total_current_val * 100, 1)}
                   for s, v in sector_values.items()]
                   
    return {
        "empty": False,
        "currency": currency,
        "total_invested": round(total_invested, 2),
        "total_current_val": round(total_current_val, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "portfolio_pe": round(avg_pe, 1) if avg_pe else "N/A",
        "health_status": health_status,
        "risk_rating": risk_rating,
        "num_stocks": len(valid_stocks),
        "num_sectors": num_sectors,
        "max_sector_share": round(max_sector_share, 1),
        "stocks": valid_stocks,
        "sectors": sec_records
    }

