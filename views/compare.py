import streamlit as st
import plotly.graph_objects as go
from data_service import load_ticker_list, get_stock_data, compute_technicals, generate_recommendation
from ui_components import apply_theme, radar_chart, render_sebi_disclaimer

def page_compare():
    st.markdown('<div class="section-title">🆚 Compare 3 Stocks</div>', unsafe_allow_html=True)
    market = st.session_state.get("market_mode", "🇮🇳 India")
    ticker_data = load_ticker_list(market)
    stock_map = {t["name"]: t["ticker"] for t in ticker_data} if ticker_data else {}
    stock_names = sorted(stock_map.keys())
    
    c1,c2,c3 = st.columns(3)
    with c1: s1 = st.selectbox("Stock 1",[""]+stock_names,key="cmp1")
    with c2: s2 = st.selectbox("Stock 2",[""]+stock_names,key="cmp2")
    with c3: s3 = st.selectbox("Stock 3",[""]+stock_names,key="cmp3")

    if st.button("🆚 Compare Now",key="cmp_go",use_container_width=True):
        tickers = [stock_map[s] for s in [s1,s2,s3] if s and s in stock_map]
        if len(tickers) < 2:
            st.error("Please select at least 2 stocks.")
            return
            
        with st.spinner("Fetching data..."):
            stocks = [d for t in tickers if (d:=get_stock_data(t))]
            
        if len(stocks) < 2:
            st.error("Need at least 2 valid stocks.")
            return

        st.markdown('<div class="section-title">📈 Price Performance (3 Months)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        colors = ["#00D09C","#E8A838","#7C5CFC"]
        for i,s in enumerate(stocks):
            hist=s["hist_3m"];name=s["info"].get("shortName") or s["ticker"]
            if not hist.empty:
                norm = hist["Close"]/hist["Close"].iloc[0]*100
                fig.add_trace(go.Scatter(x=hist.index,y=norm.values,name=name,line=dict(color=colors[i],width=2.5)))
        apply_theme(fig,height=320,title="Normalized Price (Base 100)")
        fig.update_layout(legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#FAFAFA")))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

        st.markdown('<div class="section-title">📊 Side-by-Side Metrics</div>', unsafe_allow_html=True)
        _cur = st.session_state.get("_currency", "₹")
        metrics = [
            ("Price",lambda i:f"{_cur}{(i.get('currentPrice') or i.get('regularMarketPrice') or 0):,.2f}"),
            ("P/E",lambda i:f"{(i.get('trailingPE') or i.get('forwardPE') or 0):.1f}" if not isinstance(i.get('trailingPE'), str) else "N/A"),
            ("ROE",lambda i:f"{(i.get('returnOnEquity') or 0)*100:.1f}%"),
            ("D/E",lambda i:f"{(i.get('debtToEquity') or 0)/100 if (i.get('debtToEquity') or 0)>10 else (i.get('debtToEquity') or 0):.2f}"),
            ("Sales Growth",lambda i:f"{(i.get('revenueGrowth') or 0)*100:.1f}%"),
            ("Profit Growth",lambda i:f"{(i.get('earningsGrowth') or 0)*100:.1f}%"),
            ("Div Yield",lambda i:f"{(i.get('dividendYield') or 0)*100:.2f}%"),
            ("Market Cap",lambda i:f"{_cur}{(i.get('marketCap') or 0)/1e7:,.0f} Cr" if _cur=="₹" else f"{_cur}{(i.get('marketCap') or 0)/1e9:,.2f} B"),
            ("52W High",lambda i:f"{_cur}{(i.get('fiftyTwoWeekHigh') or 0):,.0f}"),
            ("52W Low",lambda i:f"{_cur}{(i.get('fiftyTwoWeekLow') or 0):,.0f}"),
            ("Promoter %",lambda i:f"{(i.get('heldPercentInsiders') or 0)*100:.1f}%"),
        ]
        names = [s["info"].get("shortName") or s["ticker"] for s in stocks]
        hdr = st.columns([2]+[1]*len(stocks))
        hdr[0].markdown("**Metric**")
        for i,n in enumerate(names): hdr[i+1].markdown(f"**{n}**")
        st.markdown('<hr class="ss-sep" style="margin:6px 0"/>', unsafe_allow_html=True)
        for label,fn in metrics:
            rc = st.columns([2]+[1]*len(stocks))
            rc[0].markdown(f'<span style="color:#9E9E9E;font-size:13px">{label}</span>',unsafe_allow_html=True)
            for i,s in enumerate(stocks):
                try: val=fn(s["info"])
                except: val="N/A"
                rc[i+1].markdown(f'<span style="font-family:JetBrains Mono,monospace;font-size:13px">{val}</span>',unsafe_allow_html=True)
            st.markdown('<hr class="ss-sep" style="margin:3px 0"/>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🎯 Scorecard Comparison</div>', unsafe_allow_html=True)
        rcols = st.columns(len(stocks))
        for i,s in enumerate(stocks):
            with rcols[i]:
                st.markdown(f"<div style='text-align:center;font-weight:700;margin-bottom:6px'>{names[i]}</div>",unsafe_allow_html=True)
                st.plotly_chart(radar_chart(s["info"]),use_container_width=True,config={"displayModeBar":False})

        st.markdown('<div class="section-title">📝 StockSense AI Conclusion</div>', unsafe_allow_html=True)
        scores = []
        for s in stocks:
            ta=compute_technicals(s["hist_1y"])
            verdict,cls,icon,reasons=generate_recommendation(s["info"],ta)
            scores.append((s,verdict,cls,icon,reasons))
            
        best = sorted(scores,key=lambda x:{"BUY":2,"HOLD":1,"SELL":0}[x[1]],reverse=True)[0]
        best_name = best[0]["info"].get("shortName") or best[0]["ticker"]
        st.markdown(f"""<div class="rec-banner {best[2]}"><div class="rec-icon">{best[3]}</div><div>
          <div class="rec-label {best[2]}">Best Pick: {best_name} ({best[1]})</div>
          <div class="rec-reason">Combined fundamental + technical scoring.</div></div></div>""", unsafe_allow_html=True)
        for s,verdict,cls,icon,reasons in scores:
            name=s["info"].get("shortName") or s["ticker"]
            with st.expander(f"{icon} {name} — {verdict}"):
                for r in reasons: st.markdown(f"- {r}")
        render_sebi_disclaimer()
