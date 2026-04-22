import streamlit as st
import yfinance as yf

def page_watchlist():
    st.markdown('<div class="section-title">📋 Your Watchlist</div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.markdown("""<div class="guest-lock">
          <div class="lock-icon">🔒</div>
          <div class="lock-title">Watchlist — Login Required</div>
          <div class="lock-desc">Sign in to save stocks, track your custom portfolio, and sort by gains!</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔐 Login to Unlock", key="wl_login_btn", use_container_width=True):
            st.session_state.prev_page = st.session_state.page
            st.session_state.page = "login"
            st.rerun()
        return

    wl = st.session_state.get("watchlist", [])
    if not wl:
        st.markdown("""<div class="wl-empty">
          <div class="wl-icon">🤷</div>
          <div style="font-weight:700;font-size:1.2rem;margin-bottom:8px">Your watchlist is empty</div>
          <div>Go to any stock's detail page and click the ⭐ Watch button to add it here.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔍 Find Stocks to Watch", key="wl_empty_btn"):
            st.session_state.prev_page = "watchlist"
            st.session_state.page = "search"
            st.rerun()
        return

    st.markdown(f'<div style="color:var(--text-secondary);font-size:13px;margin-bottom:16px">You are tracking {len(wl)} stocks.</div>', unsafe_allow_html=True)
    
    # Sorting option
    sort_by = st.selectbox("Sort by", ["Default", "Top Gainers", "Top Losers", "A-Z"], key="wl_sort")
    
    with st.spinner("Fetching live prices..."):
        enriched_wl = []
        for item in wl:
            ticker = item["ticker"]
            name = item["name"]
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="2d")
                price, chg, pct = 0, 0, 0
                if len(hist) >= 2:
                    prev, curr = hist["Close"].iloc[-2], hist["Close"].iloc[-1]
                    price = curr
                    chg = curr - prev
                    pct = (chg/prev)*100
                elif len(hist) == 1:
                    price = hist["Close"].iloc[-1]
            except:
                price, chg, pct = 0, 0, 0
                
            enriched_wl.append({
                "ticker": ticker, "name": name, "price": price, "chg": chg, "pct": pct
            })
            
    # Apply Sorting
    if sort_by == "Top Gainers":
        enriched_wl.sort(key=lambda x: x["pct"], reverse=True)
    elif sort_by == "Top Losers":
        enriched_wl.sort(key=lambda x: x["pct"])
    elif sort_by == "A-Z":
        enriched_wl.sort(key=lambda x: x["name"])

    _cur = st.session_state.get("_currency", "₹")

    for item in enriched_wl:
        ticker = item["ticker"]
        name = item["name"]
        price = item["price"]
        chg = item["chg"]
        pct = item["pct"]

        color = "#00D09C" if pct >= 0 else "#EB5B3C"
        arrow = "▲" if pct >= 0 else "▼"
        
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        with c1:
            st.markdown(f'<div style="font-weight:700;padding-top:10px">{name}</div><div style="color:var(--text-muted);font-size:12px">{ticker}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-weight:700;padding-top:10px">{_cur}{price:,.2f}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="color:{color};font-weight:600;padding-top:10px">{arrow} {abs(pct):.2f}%</div>', unsafe_allow_html=True)
        with c4:
            ck1, ck2 = st.columns(2)
            with ck1:
                if st.button("📉", key=f"wl_go_{ticker}", help=f"Analyze {ticker}"):
                    st.session_state.search_ticker = ticker
                    st.session_state.last_search = name
                    st.session_state.prev_page = "watchlist"
                    st.session_state.page = "search"
                    st.rerun()
            with ck2:
                if st.button("❌", key=f"wl_rmbtn_{ticker}", help="Remove from watchlist"):
                    st.session_state.watchlist = [w for w in st.session_state.watchlist if w["ticker"] != ticker]
                    st.rerun()
        st.markdown('<hr class="ss-sep" style="margin:8px 0"/>', unsafe_allow_html=True)
