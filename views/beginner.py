import streamlit as st
from data_service import load_ticker_list, screen_stocks_with_progress
from ui_components import render_breadcrumb, render_sebi_disclaimer, render_sip_calculator
from views.stock_detail import render_super_investors, render_simulator, get_stock_data

def page_beginner():
    steps = ["Risk Profile", "Sector", "Horizon", "Budget", "Results"]
    step = st.session_state.beginner_step
    if step > 1:
        if st.button("Previous Step", key="beg_back", type="secondary"):
            st.session_state.beginner_step = step - 1
            st.rerun()
            
    render_breadcrumb(steps, step - 1)
    st.markdown(f'<div class="section-title">Beginner Mode — Step {step} of 5</div>', unsafe_allow_html=True)
    bq = st.session_state.bq
    market = st.session_state.get("market_mode", "India")
    _cur = st.session_state.get("_currency", "₹")

    if step == 1:
        st.markdown("### How do you feel about risk?")
        risk = st.radio("Risk level", ["Low Risk — Safe, steady returns", "Medium Risk — Balanced growth", "High Risk — Maximum growth"], key="bq_risk", label_visibility="collapsed")
        if st.button("Next Step", key="bq1", type="primary"):
            bq["risk"] = risk
            st.session_state.bq = bq
            st.session_state.beginner_step = 2
            st.rerun()

    elif step == 2:
        st.markdown("### Which sectors interest you?")
        sectors = st.multiselect("Select one or more", ["Technology", "Banking & Finance", "Pharma & Healthcare", "Energy & Power", "FMCG & Consumer", "Auto & EV", "Infrastructure", "Defence", "No Preference"], key="bq_sec")
        if st.button("Next Step", key="bq2", type="primary"):
            bq["sectors"] = sectors or ["No Preference"]
            st.session_state.bq = bq
            st.session_state.beginner_step = 3
            st.rerun()

    elif step == 3:
        st.markdown("### How long do you plan to invest?")
        horizon = st.radio("Investment horizon", ["Short-term (< 1 year)", "Medium-term (1–3 years)", "Mid-Long term (3–6 years)", "Long-term (6+ years)"], key="bq_hor", label_visibility="collapsed")
        if st.button("Next Step", key="bq3", type="primary"):
            bq["horizon"] = horizon
            st.session_state.bq = bq
            st.session_state.beginner_step = 4
            st.rerun()

    elif step == 4:
        st.markdown("### What is your investment budget?")
        budget = st.number_input(f"Total budget ({_cur})", min_value=100, max_value=10000000, value=10000, step=500, key="bq_bud")
        use_q50 = st.toggle("Quick Scan (Top 50 stocks — faster results)", value=True, key="bq_q50")
        st.session_state.use_quick50 = use_q50
        if st.button("Find Stocks", key="bq4", type="primary"):
            bq["budget"] = budget
            st.session_state.bq = bq
            st.session_state.beginner_step = 5
            st.rerun()

    elif step == 5:
        bq = st.session_state.bq
        risk_raw = bq.get("risk", "Medium")
        budget = bq.get("budget", None)
        horizon_raw = bq.get("horizon", "Medium-term (1–3 years)")

        # Risk base mapping
        if "Low" in risk_raw: max_pe, max_de, min_roe = 20, 0.7, 12
        elif "High" in risk_raw: max_pe, max_de, min_roe = 40, 2.0, 5
        else: max_pe, max_de, min_roe = 28, 1.2, 10

        # Bug 3 — Subtle Horizon Adjustments
        if "Short" in horizon_raw:
            max_pe -= 3; max_de -= 0.1; min_roe += 2
        elif "Mid-Long" in horizon_raw:
            max_pe += 3; max_de += 0.1; min_roe -= 1
        elif "Long" in horizon_raw:
            max_pe += 5; max_de += 0.2; min_roe -= 2

        max_pe = max(10, max_pe)
        max_de = max(0.1, round(max_de, 2))
        min_roe = max(1, min_roe)

        # Sector Mapping & Defence Ticker Helper (Bug 1)
        sector_map_dict = {
            "Technology": ["Information Technology", "Communication Services", "Technology"],
            "Banking & Finance": ["Financial Services", "Financials"],
            "Pharma & Healthcare": ["Healthcare", "Health Care", "Pharma"],
            "Energy & Power": ["Oil Gas & Consumable Fuels", "Power", "Energy", "Utilities"],
            "FMCG & Consumer": ["Fast Moving Consumer Goods", "Consumer Durables", "Consumer Services", "Consumer Staples", "Consumer Discretionary"],
            "Auto & EV": ["Automobile and Auto Components"],
            "Infrastructure": ["Construction", "Construction Materials", "Capital Goods", "Realty", "Real Estate", "Industrials", "Materials"],
            "Defence": ["Capital Goods", "Industrials"],
        }
        defence_tickers = {"HAL.NS", "BEL.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "BDL.NS"}

        # Market Cap Rank Priority for Quick Scan (Bug 2)
        top_mcap_priority = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS",
            "HINDUNILVR.NS", "LT.NS", "HCLTECH.NS", "SUNPHARMA.NS", "KOTAKBANK.NS", "M&M.NS", "TATAMOTORS.NS", "NTPC.NS",
            "AXISBANK.NS", "ONGC.NS", "ADANIENT.NS", "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "BAJFINANCE.NS",
            "WIPRO.NS", "ASIANPAINT.NS", "COALINDIA.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HAL.NS", "BEL.NS", "VBL.NS",
            "ZOMATO.NS", "NESTLEIND.NS", "SIEMENS.NS", "DLF.NS", "GRASIM.NS", "TECHM.NS", "HDFCLIFE.NS", "IOC.NS",
            "PIDILITIND.NS", "HINDALCO.NS", "BPCL.NS", "ADANIPORTS.NS", "SHRIRAMFIN.NS", "SBILIFE.NS", "INDIGO.NS", "GAIL.NS",
            "BRITANNIA.NS", "TRENT.NS", "EICHERMOT.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BAJAJ-AUTO.NS",
            "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AVGO", "TSLA", "BRK-B", "JPM", "LLY", "V", "UNH",
            "MA", "WMT", "XOM", "PG", "COST", "JNJ", "HD", "ORCL", "ABBV", "BAC", "CRM", "KO", "NFLX", "CVX", "AMD",
            "PEP", "MRK", "TMO", "LIN", "ADBE", "ACN", "WFC", "MCD", "DIS", "CSCO", "GE", "TXN", "PM", "MS", "AMAT"
        ]
        top_mcap_rank = {ticker: i for i, ticker in enumerate(top_mcap_priority)}

        ticker_data = load_ticker_list(market)
        selected_sectors = bq.get("sectors", ["No Preference"])
        if isinstance(selected_sectors, str):
            selected_sectors = [selected_sectors]
            
        no_pref = "No Preference" in selected_sectors or not selected_sectors

        if not no_pref and ticker_data:
            allowed_sectors = set()
            for s_ui in selected_sectors:
                allowed_sectors.update(sector_map_dict.get(s_ui, []))
            
            is_defence = "Defence" in selected_sectors
            filtered_tickers = []
            for t in ticker_data:
                t_sec = t.get("sector", "")
                t_tick = t.get("ticker", "")
                t_name = t.get("name", "").lower()
                
                matches = t_sec in allowed_sectors
                if is_defence and (t_tick in defence_tickers or "defence" in t_name or "defense" in t_name):
                    matches = True
                if matches:
                    filtered_tickers.append(t)

            if len(filtered_tickers) < 10:
                st.info("Limited stocks available in selected sectors — showing closest matches")
                scanned_tickers = ticker_data
            else:
                scanned_tickers = filtered_tickers
        else:
            scanned_tickers = ticker_data

        scanned_tickers_sorted = sorted(scanned_tickers, key=lambda t: top_mcap_rank.get(t["ticker"], 9999))
        stock_map = {t["name"]: t["ticker"] for t in scanned_tickers_sorted} if scanned_tickers_sorted else {}
        
        if st.session_state.use_quick50:
            stocks_to_scan = {k: v for i, (k, v) in enumerate(stock_map.items()) if i < 50}
        else:
            stocks_to_scan = stock_map

        m_name = "Indian" if "India" in market else "US"
        scan_label = "Top 50" if st.session_state.use_quick50 else f"{len(stock_map)}+"
        st.markdown(f"""<div style="background:rgba(0,208,156,.08);border:1px solid rgba(0,208,156,.2);border-radius:10px;padding:12px 16px;margin-bottom:16px">
          Scanning {scan_label} {m_name} market stocks tailored for your {horizon_raw} horizon...<br>
          <span style="font-size:11px;color:#616161">Filtering by risk parameters and sector preferences.</span></div>""", unsafe_allow_html=True)

        df = screen_stocks_with_progress(stocks_to_scan, max_pe=max_pe, max_de=max_de, min_roe=min_roe, budget=budget)

        if df.empty:
            st.warning("No stocks matched your exact criteria. Try broadening your budget or risk preferences.")
            st.info("Tip: Toggle 'Quick Scan 50' off or choose a higher risk level to see more results.")
            if st.button("Adjust Preferences", key="beg_retry"):
                st.session_state.beginner_step = 1
                st.rerun()
            return

        passed = df[df["Status"].str.contains("Pass")]
        if budget: passed = passed[passed["Price"] <= budget]

        # A live-data outage or strict filters can leave the scan with only
        # rejected rows. Do not render empty "Top picks" sections in that case.
        if passed.empty:
            st.warning("No stocks matched these filters with the currently available market data.")
            st.info("Try a higher-risk profile, a larger budget, or run the scan again in a few minutes.")
            if st.button("Adjust Preferences", key="beg_retry"):
                st.session_state.beginner_step = 1
                st.rerun()
            return

        top3 = passed.head(3); top10 = passed.head(10)

        st.markdown('<div class="section-title">Top 3 Picks For You</div>', unsafe_allow_html=True)
        ranks = ["#1 Pick", "#2 Pick", "#3 Pick"]
        for i, (_, row) in enumerate(top3.iterrows()):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f'<div class="ss-card" style="padding:14px"><span style="font-size:0.85rem;font-weight:700;color:var(--accent-green)">{ranks[i]}</span><br><strong>{row["Name"]}</strong><br><span style="color:#9E9E9E;font-size:.8rem">{row["Ticker"]}</span></div>', unsafe_allow_html=True)
            with c2:
                color = "green" if row["Score"] >= 70 else "gold"
                st.markdown(f'<div class="metric-chip"><div class="label">Score</div><div class="value {color}">{row["Score"]}/100</div></div>', unsafe_allow_html=True)
            with c3:
                if budget and row.get("Shares with Budget"):
                    st.markdown(f'<div class="metric-chip"><div class="label">With {_cur}{budget:,}</div><div class="value gold">{row["Shares with Budget"]} shares</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-chip"><div class="label">Price</div><div class="value">{_cur}{row["Price"]:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Top Picks — Click to Analyze</div>', unsafe_allow_html=True)
        for i, row in top10.iterrows():
            rc1, rc2, rc3, rc4, rc5 = st.columns([3, 1.5, 1.5, 1.5, 1.5])
            with rc1:
                st.markdown(f'<div style="font-weight:600;color:#FAFAFA">{row["Name"]}</div><div style="font-size:11px;color:#9E9E9E">{row["Ticker"]}</div>', unsafe_allow_html=True)
            with rc2:
                st.markdown(f'<div style="font-size:13px;color:#FAFAFA">{_cur}{row["Price"]:,.2f}</div>', unsafe_allow_html=True)
            with rc3:
                sc_color = "#00D09C" if row["Score"] >= 50 else "#E8A838" if row["Score"] >= 35 else "#EB5B3C"
                st.markdown(f'<div style="font-weight:700;color:{sc_color}">{row["Score"]}/100</div>', unsafe_allow_html=True)
            with rc4:
                is_pass = "Pass" if "Pass" in row["Status"] else "Fail"
                st.markdown(f'<div style="font-size:12px;font-weight:600;color:{"#00D09C" if is_pass == "Pass" else "#EB5B3C"}">{is_pass}</div>', unsafe_allow_html=True)
            with rc5:
                if st.button("Analyze", key=f"screen_pick_{i}_{row['Ticker']}", use_container_width=True):
                    st.session_state.search_ticker = row["Ticker"]
                    st.session_state.prev_page = st.session_state.page
                    st.session_state.page = "search"
                    st.rerun()

        with st.expander("View Full Screener Table"):
            cols_list = ["Name", "Price", "P/E", "D/E", "ROE%", "Promoter%", "Sales Growth%", "Score", "Status"]
            if budget: cols_list.append("Shares with Budget")
            st.dataframe(top10[cols_list].reset_index(drop=True), use_container_width=True, hide_index=True)

        st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
        if not top3.empty:
            render_super_investors(top3.iloc[0]["Ticker"])
            st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
            data = get_stock_data(top3.iloc[0]["Ticker"])
            if data: render_simulator(data["info"])

        st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
        render_sip_calculator()
        st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)

        if st.button("Start Over", key="beg_rst"):
            st.session_state.beginner_step = 1
            st.session_state.bq = {}
            st.rerun()
        render_sebi_disclaimer()

