import streamlit as st
import yfinance as yf
from data_service import load_ticker_list, _yf_session

def page_trending():
    market = st.session_state.get("market_mode", "🇮🇳 India")
    st.markdown(f'<div class="section-title">🔥 Trending Stocks ({market})</div>', unsafe_allow_html=True)
    
    # Static list based on market to avoid rate limits while simulating trending
    if market == "🇮🇳 India":
        trending = [
            ("Reliance", "RELIANCE.NS"), ("TCS", "TCS.NS"), ("HDFC Bank", "HDFCBANK.NS"),
            ("Infosys", "INFY.NS"), ("ICICI Bank", "ICICIBANK.NS"), ("SBI", "SBIN.NS"),
            ("Bajaj Finance", "BAJFINANCE.NS"), ("Wipro", "WIPRO.NS"), ("Tata Motors", "TATAMOTORS.NS"),
            ("L&T", "LT.NS"), ("Bharti Airtel", "BHARTIARTL.NS")
        ]
    else:
        trending = [
            ("Apple", "AAPL"), ("Microsoft", "MSFT"), ("Alphabet", "GOOGL"),
            ("Amazon", "AMZN"), ("NVIDIA", "NVDA"), ("Meta", "META"),
            ("Tesla", "TSLA"), ("AMD", "AMD"), ("Netflix", "NFLX"),
            ("Broadcom", "AVGO"), ("Berkshire", "BRK-B")
        ]
        
    _cur = st.session_state.get("_currency", "₹")

    progress = st.progress(0)
    rows = []
    
    # We can fetch multiple tickers in one shot to make it much faster!
    tickers = " ".join([t[1] for t in trending])
    # Mapping for name
    name_map = {t[1]: t[0] for t in trending}
    
    progress.progress(20)
    try:
        data = yf.download(tickers, period="2d", group_by='ticker', progress=False, session=_yf_session)
        for i, (name, ticker) in enumerate(trending):
            try:
                # If single ticker vs multiple, yfinance formats output differently
                if len(trending) == 1:
                    hist = data
                else:
                    hist = data[ticker]
                
                if len(hist) >= 2:
                    prev, curr = float(hist["Close"].iloc[-2]), float(hist["Close"].iloc[-1])
                    rows.append({"Name": name, "Ticker": ticker, "Price": curr, 
                                 "Change": curr - prev, "Change%": ((curr - prev) / prev) * 100})
            except Exception as e:
                pass
            progress.progress(20 + int((i / len(trending)) * 80))
    except Exception as e:
        pass
        
    progress.empty()
    
    if rows:
        # Sort by Change% to show top gainers first
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
        st.error("Could not fetch trending data. Try again later.")
