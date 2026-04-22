import streamlit as st
from data_service import load_ticker_list, screen_stocks_with_progress
from ui_components import render_breadcrumb, render_sebi_disclaimer
from views.stock_detail import render_super_investors, render_simulator, get_stock_data

def page_beginner():
    steps = ["Risk Profile","Sector","Horizon","Budget","Results"]
    step = st.session_state.beginner_step
    if step > 1:
        if st.button("← Previous Step",key="beg_back",type="secondary"):
            st.session_state.beginner_step = step-1; st.rerun()
            
    render_breadcrumb(steps, step-1)
    st.markdown(f'<div class="section-title">🌱 Beginner Mode — Step {step} of 5</div>', unsafe_allow_html=True)
    bq = st.session_state.bq
    market = st.session_state.get("market_mode", "🇮🇳 India")
    _cur = st.session_state.get("_currency", "₹")

    if step == 1:
        st.markdown("### How do you feel about risk?")
        risk = st.radio("",["🟢 Low Risk — Safe, steady returns","🟡 Medium Risk — Balanced growth","🔴 High Risk — Maximum growth"],key="bq_risk")
        if st.button("Next →",key="bq1"):
            bq["risk"]=risk;st.session_state.bq=bq;st.session_state.beginner_step=2;st.rerun()

    elif step == 2:
        st.markdown("### Which sectors interest you?")
        sectors = st.multiselect("Select one or more",["Technology 💻","Banking & Finance 🏦","Pharma & Healthcare 💊","Energy & Power ⚡","FMCG & Consumer 🛒","Auto & EV 🚗","Infrastructure 🏗️","Defence 🛡️","No Preference 🌐"],key="bq_sec")
        if st.button("Next →",key="bq2"):
            bq["sectors"]=sectors or ["No Preference 🌐"];st.session_state.bq=bq;st.session_state.beginner_step=3;st.rerun()

    elif step == 3:
        st.markdown("### How long do you plan to invest?")
        horizon = st.radio("",["⚡ Short-term (< 1 year)","📅 Medium-term (1–3 years)","📅 Mid-Long term (3–6 years)","🏛️ Long-term (6+ years)"],key="bq_hor")
        if st.button("Next →",key="bq3"):
            bq["horizon"]=horizon;st.session_state.bq=bq;st.session_state.beginner_step=4;st.rerun()

    elif step == 4:
        st.markdown("### What is your investment budget?")
        budget = st.number_input(f"Total budget ({_cur})",min_value=100,max_value=10000000,value=10000,step=500,key="bq_bud")
        use_q50 = st.toggle("⚡ Quick Scan (Top 50 stocks — faster results)", value=True, key="bq_q50")
        st.session_state.use_quick50 = use_q50
        if st.button("🔍 Find Stocks!",key="bq4"):
            bq["budget"]=budget;st.session_state.bq=bq;st.session_state.beginner_step=5;st.rerun()

    elif step == 5:
        bq = st.session_state.bq
        risk_raw = bq.get("risk","🟡 Medium")
        budget = bq.get("budget",None)
        if "Low" in risk_raw: max_pe,max_de,min_roe = 20,0.7,12
        elif "High" in risk_raw: max_pe,max_de,min_roe = 40,2.0,5
        else: max_pe,max_de,min_roe = 28,1.2,10

        ticker_data = load_ticker_list(market)
        stock_map = {t["name"]: t["ticker"] for t in ticker_data} if ticker_data else {}
        
        if st.session_state.use_quick50:
            stocks_to_scan = {k: v for i, (k, v) in enumerate(stock_map.items()) if i < 50}
        else:
            stocks_to_scan = stock_map

        scan_label = "Top 50" if st.session_state.use_quick50 else f"{len(stock_map)}+"
        st.markdown(f"""<div style="background:rgba(0,208,156,.08);border:1px solid rgba(0,208,156,.2);border-radius:10px;padding:12px 16px;margin-bottom:16px">
          🔍 Scanning {scan_label} {market.split()[1]} market stocks with your filters...<br>
          <span style="font-size:11px;color:#616161">Filtering by risk parameters.</span></div>""", unsafe_allow_html=True)

        df = screen_stocks_with_progress(stocks_to_scan, max_pe=max_pe, max_de=max_de, min_roe=min_roe, budget=budget)

        if df.empty:
            st.error("No stocks found. Try relaxing your filters.")
            if st.button("← Try Again",key="beg_retry"): st.session_state.beginner_step=1;st.rerun()
            return

        passed = df[df["Status"]=="✅ Pass"]
        if budget: passed = passed[passed["Price"]<=budget]
        top3 = passed.head(3); top10 = passed.head(10)

        st.markdown('<div class="section-title">🏆 Top 3 Picks For You</div>', unsafe_allow_html=True)
        medals = ["🥇","🥈","🥉"]
        for i,(_,row) in enumerate(top3.iterrows()):
            c1,c2,c3 = st.columns([3,2,2])
            with c1:
                st.markdown(f'<div class="ss-card" style="padding:14px"><span style="font-size:1.3rem">{medals[i]}</span> <strong>{row["Name"]}</strong><br><span style="color:#9E9E9E;font-size:.8rem">{row["Ticker"]}</span></div>', unsafe_allow_html=True)
            with c2:
                color = "green" if row["Score"]>=70 else "gold"
                st.markdown(f'<div class="metric-chip"><div class="label">Score</div><div class="value {color}">{row["Score"]}/100</div></div>', unsafe_allow_html=True)
            with c3:
                if budget and row.get("Shares with Budget"):
                    st.markdown(f'<div class="metric-chip"><div class="label">With {_cur}{budget:,}</div><div class="value gold">{row["Shares with Budget"]} shares</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-chip"><div class="label">Price</div><div class="value">{_cur}{row["Price"]:,.2f}</div></div>', unsafe_allow_html=True)

        # Clickable result cards (top 10)
        st.markdown('<div class="section-title">🏆 Top Picks — Click to Analyze</div>', unsafe_allow_html=True)
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
                st.markdown(f'<div style="font-size:12px;color:{"#00D09C" if row["Status"]=="✅ Pass" else "#EB5B3C"}">{row["Status"]}</div>', unsafe_allow_html=True)
            with rc5:
                if st.button("📊 Analyze →", key=f"screen_pick_{i}_{row['Ticker']}", use_container_width=True):
                    st.session_state.search_ticker = row["Ticker"]
                    st.session_state.prev_page = st.session_state.page
                    st.session_state.page = "search"
                    st.rerun()

        with st.expander("📋 View Full Screener Table"):
            cols_list = ["Name","Price","P/E","D/E","ROE%","Promoter%","Sales Growth%","Score","Status"]
            if budget: cols_list.append("Shares with Budget")
            st.dataframe(top10[cols_list].reset_index(drop=True),use_container_width=True,hide_index=True)

        st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
        if not top3.empty:
            render_super_investors(top3.iloc[0]["Ticker"])
            st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
            data = get_stock_data(top3.iloc[0]["Ticker"])
            if data: render_simulator(data["info"])

        if st.button("🔄 Start Over",key="beg_rst"):
            st.session_state.beginner_step=1;st.session_state.bq={};st.rerun()
        render_sebi_disclaimer()
