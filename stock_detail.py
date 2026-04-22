import streamlit as st
import datetime
from data_service import (get_stock_data, compute_technicals, generate_recommendation, 
                          get_analyst_consensus, get_ai_summary, SUPER_INVESTORS, DEFAULT_INVESTORS)
from ui_components import (render_back_button, metric_chip, render_metric_row, 
                           render_stock_header, apply_theme, candlestick_chart, 
                           volume_chart, rsi_chart, macd_chart, bollinger_chart, 
                           radar_chart, render_sebi_disclaimer)

def safe_pct(value, max_val=80.0, min_val=-100.0):
    """Returns formatted % string or '—' for missing/unrealistic values."""
    if value is None: return "—"
    try:
        v = float(value)
        if v != v: return "—"  # NaN check
        if v > max_val or v < min_val: return "—"
        return f"{v:.1f}%"
    except: return "—"

def render_fundamentals(ticker, info):
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="section-title" style="margin-top:0">📊 Company Essentials</div>', unsafe_allow_html=True)
    with c2:
        stock_name = info.get("longName") or info.get("shortName") or ticker
        wl = st.session_state.get("watchlist", [])
        in_watchlist = any(w["ticker"] == ticker for w in wl)
        if st.session_state.logged_in:
            if in_watchlist:
                if st.button("✅ Saved", key=f"fund_wl_rm_{ticker}", type="secondary", use_container_width=True):
                    st.session_state.watchlist = [w for w in wl if w["ticker"] != ticker]
                    st.rerun()
            else:
                if st.button("⭐ Watch", key=f"fund_wl_add_{ticker}", use_container_width=True):
                    st.session_state.watchlist.append({"name": stock_name, "ticker": ticker})
                    st.rerun()
        else:
            if st.button("🔒 Login to Watch", key=f"fund_wl_lock_{ticker}", type="secondary", use_container_width=True):
                st.session_state.prev_page = st.session_state.page
                st.session_state.page = "login"
                st.rerun()

    pe = info.get("trailingPE") or info.get("forwardPE") or 0
    if isinstance(pe, str): pe = 0
    pb = info.get("priceToBook") or 0
    roe = (info.get("returnOnEquity") or 0)*100
    de = info.get("debtToEquity") or 0
    if de > 100: de = de/100
    div_yield = (info.get("dividendYield") or 0)*100
    eps = info.get("trailingEps") or 0
    sales_g = (info.get("revenueGrowth") or 0)*100
    profit_g = (info.get("earningsGrowth") or 0)*100
    wk52h = info.get("fiftyTwoWeekHigh") or 0
    wk52l = info.get("fiftyTwoWeekLow") or 0
    book_val = info.get("bookValue") or 0
    promoter = (info.get("heldPercentInsiders") or 0)*100
    npm = (info.get("profitMargins") or 0)*100
    _cur = st.session_state.get("_currency", "₹")

    def pc(v,g=10):
        if not isinstance(v, (int, float)) or v != v: return ""
        return "green" if v>=g else ("red" if v<0 else "")

    def safe_ratio(v):
        if v is None: return "—"
        try:
            val = float(v)
            if val != val or val < 0 or val > 999: return "—"
            return val
        except: return "—"

    safe_pe = safe_ratio(pe)
    safe_pb = safe_ratio(pb)
    safe_de = safe_ratio(de)

    pe_str = f"{safe_pe:.1f}" if isinstance(safe_pe, float) else "—"
    pb_str = f"{safe_pb:.2f}" if isinstance(safe_pb, float) else "—"
    de_str = f"{safe_de:.2f}" if isinstance(safe_de, float) else "—"

    chips = [
        metric_chip("P/E Ratio", pe_str, "green" if isinstance(safe_pe, float) and 0<safe_pe<25 else "red" if isinstance(safe_pe, float) and safe_pe>40 else ""),
        metric_chip("P/B Ratio", pb_str, "green" if isinstance(safe_pb, float) and 0<safe_pb<3 else "red" if isinstance(safe_pb, float) and safe_pb>6 else ""),
        metric_chip("ROE", safe_pct(roe, max_val=200), pc(roe, 15)),
        metric_chip("Debt/Equity", de_str, "green" if isinstance(safe_de, float) and safe_de<0.5 else "red" if isinstance(safe_de, float) and safe_de>2 else ""),
        metric_chip("Div Yield", safe_pct(div_yield, max_val=20, min_val=0), "green" if div_yield>1 else ""),
        metric_chip("EPS (TTM)", f"{_cur}{eps:.2f}" if eps else "N/A", "green" if eps>0 else "red"),
        metric_chip("Sales Growth", safe_pct(sales_g, max_val=500), pc(sales_g, 10)),
        metric_chip("Profit Growth", safe_pct(profit_g, max_val=500), pc(profit_g, 10)),
        metric_chip("Net Margin", safe_pct(npm, max_val=100), pc(npm, 10)),
        metric_chip("52W High", f"{_cur}{wk52h:,.0f}" if wk52h else "N/A", ""),
        metric_chip("52W Low", f"{_cur}{wk52l:,.0f}" if wk52l else "N/A", ""),
        metric_chip("Promoter Hold", f"{promoter:.1f}%" if promoter else "N/A", "green" if promoter>50 else ""),
    ]
    render_metric_row(chips)

def render_technicals(ta, hist):
    if not ta:
        st.warning("Not enough data for technical analysis (need 30+ trading days).")
        return
    st.markdown('<div class="section-title">📉 Technical Analysis</div>', unsafe_allow_html=True)
    _cur = st.session_state.get("_currency", "₹")
    try:
        rsi_val = float(ta["rsi"].iloc[-1])
        macd_val = float(ta["macd"].iloc[-1])
        sig_val = float(ta["signal"].iloc[-1])
        ma50_val = float(ta["ma50"].iloc[-1])
        close_val = float(hist["Close"].iloc[-1])
        trend = "Bullish" if close_val > ma50_val else "Bearish"
        support_val = float(ta["support"].iloc[-1]) if ta.get("support") is not None else 0
        resistance_val = float(ta["resistance"].iloc[-1]) if ta.get("resistance") is not None else 0
        vol_ratio = float(ta["vol_sma5"].iloc[-1] / ta["vol_sma20"].iloc[-1]) if ta.get("vol_sma5") is not None and float(ta["vol_sma20"].iloc[-1]) > 0 else 1
        vol_trend = "Increasing 📈" if vol_ratio > 1.1 else ("Decreasing 📉" if vol_ratio < 0.9 else "Stable →")
        breaking = "Breaking Out ↑" if close_val > resistance_val*0.98 else ("Near Support ↓" if close_val < support_val*1.02 else "Ranging ↔")
        chips = [
            metric_chip("RSI (14)",f"{rsi_val:.1f}","green" if rsi_val<40 else ("red" if rsi_val>70 else "gold"),"RSI"),
            metric_chip("MACD","Bullish" if macd_val>sig_val else "Bearish","green" if macd_val>sig_val else "red","MACD"),
            metric_chip("MA50 Trend",trend,"green" if trend=="Bullish" else "red"),
            metric_chip("Volume Trend",vol_trend,"green" if vol_ratio>1.1 else ""),
            metric_chip("Support",f"{_cur}{support_val:,.0f}",""),
            metric_chip("Resistance",f"{_cur}{resistance_val:,.0f}",""),
            metric_chip("Price Action",breaking,"green" if "Out" in breaking else ("red" if "Support" in breaking else "gold")),
        ]
        render_metric_row(chips)
    except Exception: pass

    tab1,tab2,tab3,tab4 = st.tabs(["🕯️ Candles","📈 RSI","📊 MACD","🎯 Bollinger"])
    with tab1:
        st.plotly_chart(candlestick_chart(hist,"Price (1 Year)"),use_container_width=True,config={"displayModeBar":False})
        st.plotly_chart(volume_chart(hist),use_container_width=True,config={"displayModeBar":False})
    with tab2:
        st.plotly_chart(rsi_chart(ta["rsi"].dropna()),use_container_width=True,config={"displayModeBar":False})
        if rsi_val<30: st.success("🟢 RSI below 30 — **Oversold**. Potential buying opportunity!")
        elif rsi_val>70: st.error("🔴 RSI above 70 — **Overbought**. Be cautious!")
        else: st.info(f"🟡 RSI at {rsi_val:.0f} — Neutral zone.")
    with tab3:
        st.plotly_chart(macd_chart(ta["macd"].dropna(),ta["signal"].dropna(),ta["macd_hist"].dropna()),use_container_width=True,config={"displayModeBar":False})
    with tab4:
        st.plotly_chart(bollinger_chart(hist,ta),use_container_width=True,config={"displayModeBar":False})

def render_analyst_consensus(recs):
    st.markdown('<div class="section-title">🎯 Analyst Consensus</div>', unsafe_allow_html=True)
    consensus = get_analyst_consensus(recs)
    if consensus is None:
        st.markdown("""<div class="ss-card" style="text-align:center;padding:20px">
          <div style="font-size:1.8rem;margin-bottom:8px">📡</div>
          <div style="color:#9E9E9E">Analyst ratings not available for this stock.</div>
        </div>""", unsafe_allow_html=True)
        return
    total=consensus["total"];sb=consensus["strongBuy"];b=consensus["buy"];h=consensus["hold"];s=consensus["sell"];ss=consensus["strongSell"]
    bull_pct=(sb+b)/total*100;bear_pct=(ss+s)/total*100;needle_pos=bull_pct
    if bull_pct>=70: label,color="Strongly Bullish 🐂","#00D09C"
    elif bull_pct>=50: label,color="Bullish 📈","#90EE90"
    elif bear_pct>=70: label,color="Strongly Bearish 🐻","#EB5B3C"
    elif bear_pct>=50: label,color="Bearish 📉","#FF8C00"
    else: label,color="Neutral ⚖️","#E8A838"
    cols=st.columns(5)
    for col,(lbl,val) in zip(cols,[("Strong Buy",sb),("Buy",b),("Hold",h),("Sell",s),("Strong Sell",ss)]):
        clr="#00D09C" if "Buy" in lbl else ("#EB5B3C" if "Sell" in lbl else "#E8A838")
        col.markdown(f'<div style="text-align:center;background:rgba(255,255,255,.03);border-radius:10px;padding:12px"><div style="font-size:1.5rem;font-weight:700;color:{clr}">{val}</div><div style="font-size:11px;color:#9E9E9E">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="analyst-bar-wrap" style="margin-top:14px">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="color:#EB5B3C;font-size:12px;font-weight:600">Bearish</span>
        <span style="color:{color};font-size:14px;font-weight:700">{label}</span>
        <span style="color:#00D09C;font-size:12px;font-weight:600">Bullish</span>
      </div>
      <div class="analyst-bar"><div class="analyst-needle" style="left:{needle_pos:.0f}%"></div></div>
      <div style="text-align:center;margin-top:10px;color:#9E9E9E;font-size:12px">Based on {total} analyst ratings</div>
    </div>""", unsafe_allow_html=True)

def render_news(news_list):
    st.markdown('<div class="section-title">📰 Recent News</div>', unsafe_allow_html=True)
    if not news_list:
        st.markdown('<div class="news-card"><div class="news-title">No recent news available.</div></div>', unsafe_allow_html=True)
        return
    for item in news_list[:5]:
        title = item.get("title", "No title")
        publisher = item.get("publisher", "")
        link = item.get("link", "#")
        pub_time = item.get("time", "")
        time_str = ""
        if pub_time:
            try:
                if isinstance(pub_time, (int, float)):
                    time_str = datetime.datetime.fromtimestamp(int(pub_time)).strftime("%d %b %Y, %I:%M %p")
                else:
                    time_str = str(pub_time)[:25]
            except:
                time_str = str(pub_time)[:25]
        st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none"><div class="news-card"><div class="news-title">{title}</div><div class="news-meta">{publisher} · {time_str}</div></div></a>', unsafe_allow_html=True)

def render_super_investors(ticker):
    st.markdown('<div class="section-title">👑 Super Investors</div>', unsafe_allow_html=True)
    investors = SUPER_INVESTORS.get(ticker, DEFAULT_INVESTORS)
    for inv in investors:
        st.markdown(f"""<div class="investor-card"><div><div class="investor-name">{inv['name']}</div><div class="investor-type">{inv['type']}</div></div>
          <div style="text-align:right"><div class="investor-holding">{inv['holding']}</div><div style="font-size:11px;color:#616161">{inv.get('value','')}</div></div></div>""", unsafe_allow_html=True)

def render_recommendation(info, ta):
    verdict,cls,icon,reasons = generate_recommendation(info, ta)
    st.markdown(f"""<div class="rec-banner {cls}"><div class="rec-icon">{icon}</div><div>
      <div class="rec-label {cls}">StockSense Says: {verdict}</div>
      <div class="rec-reason">Based on fundamental + technical analysis</div></div></div>""", unsafe_allow_html=True)
    with st.expander("📋 Why this recommendation?"):
        for r in reasons: st.markdown(f"- {r}")

def render_simulator(info):
    st.markdown('<div class="section-title">💰 What-If Investment Simulator</div>', unsafe_allow_html=True)
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 100
    c1,c2,c3 = st.columns(3)
    _cur = st.session_state.get("_currency", "₹")
    with c1: invest = st.number_input(f"Amount ({_cur})",min_value=100,max_value=1000000,value=10000,step=500,key="sim_amt")
    with c2: growth = st.slider("Expected Return %",-30,50,12,key="sim_g")
    with c3: years = st.slider("Years",1,20,3,key="sim_y")
    shares = invest/price if price>0 else 0
    future_price = price*((1+growth/100)**years)
    future_value = shares*future_price
    profit = future_value-invest
    pct_gain = (profit/invest*100) if invest>0 else 0
    color = "#00D09C" if profit>=0 else "#EB5B3C"
    st.markdown(f"""<div class="sim-result" style="margin-top:12px">
      <div style="color:#9E9E9E;font-size:13px;margin-bottom:4px">{shares:.2f} shares × {_cur}{future_price:,.2f} in {years}yr</div>
      <div class="sim-amount" style="color:{color}">{_cur}{future_value:,.0f}</div>
      <div style="color:{color};font-size:1.1rem;font-weight:600">{'📈' if profit>=0 else '📉'} {'+' if profit>=0 else ''}{profit:,.0f} ({'+' if pct_gain>=0 else ''}{pct_gain:.1f}%)</div>
      <div style="color:#616161;font-size:11px;margin-top:8px">⚠️ Simulation only. Not financial advice.</div></div>""", unsafe_allow_html=True)

def render_ai_tab(ticker, info, ta):
    if not st.session_state.logged_in:
        st.markdown("""<div class="guest-lock">
          <div class="lock-icon">🔒</div>
          <div class="lock-title">AI Analysis — Login Required</div>
          <div class="lock-desc">Sign in to unlock AI-powered stock analysis powered by Llama 3.3</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔐 Login to Unlock", key="ai_login_btn", use_container_width=True):
            st.session_state.prev_page = st.session_state.page
            st.session_state.page = "login"
            st.rerun()
        return

    st.markdown('<div class="ai-badge">🤖 Powered by Llama 3.3 · Groq</div>', unsafe_allow_html=True)
    company_name = info.get("longName") or info.get("shortName") or ticker
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    _cur = st.session_state.get("_currency", "₹")
    mcap = f"{_cur}{(info.get('marketCap') or 0)/1e7:,.0f} Cr" if _cur == "₹" else f"{_cur}{(info.get('marketCap') or 0)/1e9:,.2f} B"
    info_summary = {
        "price": f"{price:,.2f}", "pe": f"{info.get('trailingPE') or info.get('forwardPE') or 'N/A'}",
        "roe": f"{(info.get('returnOnEquity') or 0)*100:.1f}",
        "de": f"{(info.get('debtToEquity') or 0)/100 if (info.get('debtToEquity') or 0)>10 else (info.get('debtToEquity') or 0):.2f}",
        "sales_g": f"{(info.get('revenueGrowth') or 0)*100:.1f}",
        "profit_g": f"{(info.get('earningsGrowth') or 0)*100:.1f}",
        "div_yield": f"{(info.get('dividendYield') or 0)*100:.2f}",
        "high52": f"{info.get('fiftyTwoWeekHigh') or 'N/A'}",
        "low52": f"{info.get('fiftyTwoWeekLow') or 'N/A'}",
        "sector": info.get("sector", "N/A"),
        "mcap": mcap,
    }
    tech_summary = {"rsi": "N/A", "macd_signal": "N/A"}
    if ta:
        try:
            rsi_val = float(ta["rsi"].iloc[-1])
            macd_val = float(ta["macd"].iloc[-1])
            sig_val = float(ta["signal"].iloc[-1])
            tech_summary["rsi"] = f"{rsi_val:.1f}"
            tech_summary["macd_signal"] = "Bullish" if macd_val > sig_val else "Bearish"
        except:
            pass
    info_str = str(info_summary)
    tech_str = str(tech_summary)
    with st.spinner("🤖 AI is analyzing this stock..."):
        summary = get_ai_summary(ticker, company_name, info_str, tech_str, _cur)
    st.markdown(f'<div class="ai-card">{summary}</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#616161;font-size:11px;margin-top:8px">⚠️ AI analysis is for educational purposes only. Not financial advice. Always do your own research.</div>', unsafe_allow_html=True)

def render_stock_detail(ticker, show_news=False, show_back=True):
    with st.spinner("Fetching live data..."):
        data = get_stock_data(ticker)
    
    # Error handling for invalid ticker
    if data is None or not data.get("info"):
        st.error(f"⚠️ Stock not found or data unavailable for **{ticker}**.")
        st.info("Try checking the selection, or search by company name instead of ticker.")
        return
        
    info=data["info"];hist_1y=data["hist_1y"];news=data["news"];recs=data["recs"]
    ta = compute_technicals(hist_1y)
    if show_back: render_back_button()
    render_stock_header(info)

    tab_fund,tab_tech,tab_ai,tab_radar,tab_analyst,tab_investors,tab_sim = st.tabs(
        ["📊 Fundamentals","📉 Technicals","🤖 AI Summary","🎯 Scorecard","🗣️ Analysts","👑 Super Investors","💰 Simulator"])
    with tab_fund:
        render_fundamentals(ticker, info)
        if show_news: render_news(news)
    with tab_tech: render_technicals(ta, hist_1y)
    with tab_ai: render_ai_tab(ticker, info, ta)
    with tab_radar:
        c1,c2 = st.columns([1,1])
        with c1: st.plotly_chart(radar_chart(info),use_container_width=True,config={"displayModeBar":False})
        with c2: render_recommendation(info,ta); render_sebi_disclaimer()
    with tab_analyst: render_analyst_consensus(recs)
    with tab_investors: render_super_investors(ticker)
    with tab_sim: render_simulator(info)
