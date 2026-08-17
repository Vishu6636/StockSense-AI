import streamlit as st
import datetime
from data_service import get_market_news
from ui_components import render_sebi_disclaimer

def page_home():
    mkt = st.session_state.get("market_mode", "India")
    pill_label = "500 Indian Stocks" if "India" in mkt else "300 US Stocks"
    
    st.markdown(f"""<div style="padding:30px 0 10px;text-align:center">
      <div class="hero-title"><span class="gradient">StockSense</span> AI</div>
      <div class="hero-sub">Smart Stock Analysis · Risk-Aware · Built for You</div>
      <div class="hero-pills" style="justify-content:center">
        <span class="hero-pill green">{pill_label}</span>
        <span class="hero-pill purple">Live Market Data</span>
        <span class="hero-pill gold">Auto Risk Filter</span>
        <span class="hero-pill red">Educational Purpose Only</span>
      </div>
    </div>""", unsafe_allow_html=True)
    
    c_hero1, c_hero2, c_hero3 = st.columns([1, 2, 1])
    with c_hero2:
        if st.button("Start Stock Analysis", key="btn_start_hero", type="primary", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "beginner"
            st.session_state.beginner_step = 1
            st.session_state.bq = {}
            st.rerun()

    st.markdown('<div style="margin-top:20px"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="mode-card"><div class="mode-title green">Beginner Mode</div>
          <div class="mode-desc">Answer a few quick questions.<br>We handle all the analysis.</div>
          <div class="mode-tag">Perfect for first-time investors.</div></div>""", unsafe_allow_html=True)
        if st.button("Start Beginner Wizard", key="btn_beg", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "beginner"
            st.session_state.beginner_step = 1
            st.session_state.bq = {}
            st.rerun()
    with c2:
        st.markdown("""<div class="mode-card"><div class="mode-title purple">Pro Mode</div>
          <div class="mode-desc">Set your own thresholds.<br>Full control over every metric.</div>
          <div class="mode-tag">For experienced investors.</div></div>""", unsafe_allow_html=True)
        if st.button("Enter Pro Screener", key="btn_pro", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "pro"
            st.rerun()
    with c3:
        st.markdown("""<div class="mode-card"><div class="mode-title gold">Trending Movers</div>
          <div class="mode-desc">See today's highlighted stocks.<br>Quick snapshot of daily movers.</div>
          <div class="mode-tag">View Daily Highlighted Stocks.</div></div>""", unsafe_allow_html=True)
        if st.button("View Daily Movers", key="btn_trend", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "trending"
            st.rerun()
            
    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="ss-card" style="text-align:center;padding:18px">
          <div style="font-weight:700;margin:6px 0;font-size:1.1rem">Compare Stocks</div>
          <div style="color:#9E9E9E;font-size:.85rem">Side-by-side metric comparison</div></div>""", unsafe_allow_html=True)
        if st.button("Compare Stocks", key="btn_cmp", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "compare"
            st.rerun()
    with cb:
        st.markdown("""<div class="ss-card" style="text-align:center;padding:18px">
          <div style="font-weight:700;margin:6px 0;font-size:1.1rem">Search Stock Details</div>
          <div style="color:#9E9E9E;font-size:.85rem">Full AI & technical analysis</div></div>""", unsafe_allow_html=True)
        if st.button("Search Stock", key="btn_srch", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "search"
            st.rerun()

    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    market_label = "India" if "India" in mkt else "US"
    st.markdown(f'<div class="section-title">Latest Market News ({market_label})</div>', unsafe_allow_html=True)
    with st.spinner("Fetching market news..."):
        mnews = get_market_news(market=mkt)
    if mnews:
        for item in mnews:
            title = item.get("title", "No title")
            publisher = item.get("publisher", "")
            link = item.get("link", "#")
            dt = item.get("dt")
            pub_time = item.get("time", "")
            time_str = ""
            if isinstance(dt, datetime.datetime):
                time_str = dt.strftime("%d %b %Y, %I:%M %p")
            elif pub_time:
                time_str = str(pub_time)[:25]
            meta_str = f"{publisher} · {time_str}" if publisher and time_str else (publisher or time_str)
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none"><div class="mnews-card"><div style="font-weight:600;font-size:.9rem;color:var(--text-primary);margin-bottom:4px">{title}</div><div style="font-size:.75rem;color:var(--text-muted)">{meta_str}</div></div></a>', unsafe_allow_html=True)
    else:
        st.info("Market news temporarily unavailable. Please check your connection or try again later.")

    render_sebi_disclaimer()
