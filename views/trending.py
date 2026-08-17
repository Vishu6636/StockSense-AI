import streamlit as st
import yfinance as yf
import datetime
import random

CURATED_TRENDING_INDIA = [
    ("Reliance Industries", "RELIANCE.NS"), ("TCS", "TCS.NS"), ("HDFC Bank", "HDFCBANK.NS"),
    ("Infosys", "INFY.NS"), ("ICICI Bank", "ICICIBANK.NS"), ("State Bank of India", "SBIN.NS"),
    ("Bajaj Finance", "BAJFINANCE.NS"), ("Wipro", "WIPRO.NS"), ("Tata Motors", "TATAMOTORS.NS"),
    ("Larsen & Toubro", "LT.NS"), ("Bharti Airtel", "BHARTIARTL.NS"), ("ITC Ltd.", "ITC.NS"),
    ("HCL Technologies", "HCLTECH.NS"), ("Kotak Mahindra Bank", "KOTAKBANK.NS"), ("Asian Paints", "ASIANPAINT.NS"),
    ("Maruti Suzuki", "MARUTI.NS"), ("Sun Pharma", "SUNPHARMA.NS"), ("Titan Company", "TITAN.NS"),
    ("UltraTech Cement", "ULTRACEMCO.NS"), ("Axis Bank", "AXISBANK.NS"), ("NTPC", "NTPC.NS"),
    ("Power Grid Corp", "POWERGRID.NS"), ("Tata Steel", "TATASTEEL.NS"), ("Mahindra & Mahindra", "M&M.NS"),
    ("Bajaj Finserv", "BAJAJFINSV.NS"), ("LTIMindtree", "LTIM.NS"), ("Coal India", "COALINDIA.NS"),
    ("Hindalco", "HINDALCO.NS"), ("Nestle India", "NESTLEIND.NS"), ("Adani Ports", "ADANIPORTS.NS"),
    ("Adani Enterprises", "ADANIENT.NS"), ("ONGC", "ONGC.NS"), ("JSW Steel", "JSWSTEEL.NS"),
    ("Grasim Industries", "GRASIM.NS"), ("Tech Mahindra", "TECHM.NS"), ("Britannia Industries", "BRITANNIA.NS"),
    ("IndusInd Bank", "INDUSINDBK.NS"), ("Eicher Motors", "EICHERMOT.NS"), ("Divi's Labs", "DIVISLAB.NS"),
    ("Hero MotoCorp", "HEROMOTOCO.NS"), ("Apollo Hospitals", "APOLLOHOSP.NS"), ("Cipla", "CIPLA.NS"),
    ("Dr. Reddy's Labs", "DRREDDY.NS"), ("BPCL", "BPCL.NS"), ("Tata Consumer", "TATACONSUM.NS"),
    ("SBI Life Insurance", "SBILIFE.NS"), ("HDFC Life", "HDFCLIFE.NS"), ("Pidilite Industries", "PIDILITIND.NS")
]

CURATED_TRENDING_US = [
    ("Apple Inc.", "AAPL"), ("Microsoft", "MSFT"), ("Alphabet Inc.", "GOOGL"),
    ("Amazon.com", "AMZN"), ("NVIDIA", "NVDA"), ("Meta Platforms", "META"),
    ("Tesla", "TSLA"), ("AMD", "AMD"), ("Netflix", "NFLX"),
    ("Broadcom", "AVGO"), ("Berkshire Hathaway", "BRK-B"), ("JPMorgan Chase", "JPM"),
    ("Eli Lilly", "LLY"), ("Visa Inc.", "V"), ("Walmart", "WMT"),
    ("UnitedHealth Group", "UNH"), ("Mastercard", "MA"), ("Procter & Gamble", "PG"),
    ("Johnson & Johnson", "JNJ"), ("Costco Wholesale", "COST"), ("Oracle", "ORCL"),
    ("Home Depot", "HD"), ("Abbott Labs", "ABT"), ("Salesforce", "CRM"),
    ("Chevron", "CVX"), ("ExxonMobil", "XOM"), ("Bank of America", "BAC"),
    ("Coca-Cola", "KO"), ("PepsiCo", "PEP"), ("Thermo Fisher", "TMO"),
    ("Merck & Co.", "MRK"), ("Adobe", "ADBE"), ("Linde plc", "LIN"),
    ("Texas Instruments", "TXN"), ("McDonald's", "MCD"), ("Cisco Systems", "CSCO"),
    ("Qualcomm", "QCOM"), ("Wells Fargo", "WFC"), ("Morgan Stanley", "MS"),
    ("GE Aerospace", "GE"), ("Intuit", "INTU"), ("IBM", "IBM"),
    ("Amgen", "AMGN"), ("Honeywell", "HON"), ("Applied Materials", "AMAT"),
    ("Uber Technologies", "UBER"), ("ServiceNow", "NOW"), ("Intel", "INTC")
]

def get_daily_trending_list(market: str, count: int = 12, date_offset: int = 0) -> list:
    """Deterministically selects a rotating subset of liquid tickers based on calendar day."""
    is_in = "India" in market or market == "IN ₹ India"
    pool = CURATED_TRENDING_INDIA if is_in else CURATED_TRENDING_US
    today_ordinal = datetime.date.today().toordinal() + date_offset
    rng = random.Random(today_ordinal)
    shuffled = list(pool)
    rng.shuffle(shuffled)
    return shuffled[:count]

def page_trending():
    market = st.session_state.get("market_mode", "India")
    m_name = "India" if "India" in market else "US"
    st.markdown(f'<div class="section-title">Daily Highlighted Movers ({m_name})</div>', unsafe_allow_html=True)
    st.caption("Daily rotating selection of 12 liquid large-cap stocks ranked by 1-day % change.")
    
    trending = get_daily_trending_list(market, count=12)
        
    _cur = st.session_state.get("_currency", "₹")

    progress = st.progress(0)
    rows = []
    
    tickers = " ".join([t[1] for t in trending])
    name_map = {t[1]: t[0] for t in trending}
    
    progress.progress(20)
    try:
        data = yf.download(tickers, period="2d", group_by='ticker', progress=False)
        for i, (name, ticker) in enumerate(trending):
            try:
                if len(trending) == 1:
                    hist = data
                else:
                    hist = data[ticker]
                
                if len(hist) >= 2:
                    prev, curr = float(hist["Close"].iloc[-2]), float(hist["Close"].iloc[-1])
                    rows.append({"Name": name, "Ticker": ticker, "Price": curr, 
                                 "Change": curr - prev, "Change%": ((curr - prev) / prev) * 100})
            except (KeyError, IndexError, TypeError, ValueError):
                pass
            progress.progress(20 + int((i / len(trending)) * 80))
    except Exception:
        pass
        
    progress.empty()
    
    if rows:
        rows.sort(key=lambda x: x["Change%"], reverse=True)
        for row in rows:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1: 
                st.markdown(f'<div style="padding:10px 0"><strong>{row["Name"]}</strong><span style="color:#616161;font-size:12px;margin-left:8px">{row["Ticker"]}</span></div>', unsafe_allow_html=True)
            with c2: 
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-weight:700;padding-top:10px">{_cur}{row["Price"]:,.2f}</div>', unsafe_allow_html=True)
            with c3:
                color = "#00D09C" if row["Change%"] >= 0 else "#EB5B3C"
                arrow = "▲" if row["Change%"] >= 0 else "▼"
                st.markdown(f'<div style="color:{color};font-weight:600;padding-top:10px">{arrow} {abs(row["Change%"]):.2f}%</div>', unsafe_allow_html=True)
            with c4:
                if st.button("Details", key=f"t_{row['Ticker']}"):
                    st.session_state.search_ticker = row["Ticker"]
                    st.session_state.last_search = row["Name"]
                    st.session_state.prev_page = "trending"
                    st.session_state.page = "search"
                    st.rerun()
            st.markdown('<hr class="ss-sep" style="margin:4px 0"/>', unsafe_allow_html=True)
    else:
        st.warning("Could not fetch trending stock data. Please check your connection or try again later.")
