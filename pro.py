import streamlit as st
import plotly.express as px
from data_service import screen_stocks_with_progress, load_ticker_list
from views.stock_detail import render_super_investors
from ui_components import apply_theme

def page_pro():
    st.markdown('<div class="section-title">🚀 Pro Mode — Advanced Stock Screener</div>', unsafe_allow_html=True)
    
    market = st.session_state.get("market_mode", "🇮🇳 India")
    _cur = st.session_state.get("_currency", "₹")

    with st.expander("📊 Fundamental Filters (What to Buy)", expanded=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            max_pe = st.slider("Max P/E Ratio",5,100,25,key="pro_pe")
            st.caption("💡 Good companies: P/E < 25")
            max_de = st.slider("Max Debt/Equity",0.1,5.0,1.0,step=0.1,key="pro_de")
            st.caption("💡 Low risk: D/E < 1.0")
        with c2:
            min_roe = st.slider("Min ROE (%)",0,40,15,key="pro_roe")
            st.caption("💡 Strong business: ROE > 15%")
            min_promoter = st.slider("Min Promoter Holding (%)",0,80,40,key="pro_prom")
            st.caption("💡 Confidence: Promoter > 50%")
        with c3:
            min_npm = st.slider("Min Net Profit Margin (%)",0,40,10,key="pro_npm")
            st.caption("💡 Healthy: NPM > 10%")
            min_eps = st.number_input(f"Min EPS ({_cur})",min_value=0.0,max_value=500.0,value=0.0,step=1.0,key="pro_eps")
            st.caption(f"💡 Profitable: EPS > 0")

        c4,c5,c6 = st.columns(3)
        with c4:
            fcf_pos = st.checkbox("Only Positive Free Cash Flow",key="pro_fcf")
        with c5:
            adv_options = ["Any","Monopoly","Duopoly","Oligopoly","Brand Power","Switching Cost","Network Effect","Conglomerate Moat","Cost Advantage","Scale Advantage","Distribution Moat","R&D Moat"]
            adv_filter = st.selectbox("Competitive Advantage",adv_options,key="pro_adv")
        with c6:
            budget = st.number_input(f"Budget ({_cur}, 0=no filter)",min_value=0,max_value=10000000,value=0,step=1000,key="pro_bud")

    use_q50 = st.toggle("⚡ Quick 50 (faster scan)", value=True, key="pro_q50")

    if st.button("🔍 Run Screener",key="pro_run",use_container_width=True):
        ticker_data = load_ticker_list(market)
        stock_map = {t["name"]: t["ticker"] for t in ticker_data} if ticker_data else {}
        
        if use_q50:
            stocks = {k: v for i, (k, v) in enumerate(stock_map.items()) if i < 50}
        else:
            stocks = stock_map
            
        budget_val = budget if budget > 0 else None
        adv_val = adv_filter if adv_filter != "Any" else None
        
        df = screen_stocks_with_progress(stocks, max_pe=max_pe, max_de=max_de, min_roe=min_roe,
            min_promoter=min_promoter, min_npm=min_npm, min_eps=min_eps,
            fcf_positive=fcf_pos, adv_filter=adv_val, budget=budget_val)
            
        if budget_val and not df.empty: df = df[df["Price"]<=budget_val]
        st.session_state.pro_df = df

    if "pro_df" in st.session_state:
        df = st.session_state.pro_df
        if df.empty:
            st.warning("No stocks found. Try relaxing filters."); return
        passed = df[df["Status"]=="✅ Pass"]
        rejected = df[df["Status"]=="❌ Reject"]

        tab_pass,tab_rej,tab_chart,tab_inv = st.tabs([f"✅ Passed ({len(passed)})",f"❌ Rejected ({len(rejected)})","📊 Score Chart","👑 Super Investors"])

        with tab_pass:
            # Clickable result cards (top 10)
            top10_passed = passed.head(10)
            st.markdown('<div class="section-title">🏆 Top Picks — Click to Analyze</div>', unsafe_allow_html=True)
            for i, row in top10_passed.iterrows():
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
                    if st.button("📊 Analyze →", key=f"screen_pick_pro_{i}_{row['Ticker']}", use_container_width=True):
                        st.session_state.search_ticker = row["Ticker"]
                        st.session_state.prev_page = st.session_state.page
                        st.session_state.page = "search"
                        st.rerun()

            with st.expander("📋 View Full Screener Table"):
                display = ["Name","Price","P/E","D/E","ROE%","NPM%","EPS","Promoter%","Sales Growth%","Advantage","Score"]
                if budget > 0: display.append("Shares with Budget")
                st.dataframe(passed[display],use_container_width=True,hide_index=True)
            if not passed.empty:
                sel = st.selectbox("Select stock to analyse:",passed["Name"].tolist(),key="pro_sel")
                sel_ticker = passed[passed["Name"]==sel]["Ticker"].values[0]
                if st.button(f"📈 Analyse {sel}",key="pro_an"):
                    st.session_state.search_ticker=sel_ticker;
                    st.session_state.last_search=sel;
                    st.session_state.prev_page="pro";
                    st.session_state.page="search";
                    st.rerun()

        with tab_rej:
            st.dataframe(rejected[["Name","Price","P/E","D/E","ROE%","Score"]],use_container_width=True,hide_index=True)

        with tab_chart:
            if not passed.empty:
                fig = px.bar(passed.head(15),x="Name",y="Score",color="Score",color_continuous_scale=["#EB5B3C","#E8A838","#00D09C"],title="Stock Score Comparison")
                apply_theme(fig,height=350,title="Stock Score Comparison")
                fig.update_layout(coloraxis_showscale=False)
                fig.update_xaxes(tickangle=-30)
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

        with tab_inv:
            if not passed.empty: render_super_investors(passed.iloc[0]["Ticker"])
