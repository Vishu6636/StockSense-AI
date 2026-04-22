import streamlit as st
import datetime
from data_service import get_market_news, load_ticker_list
from ui_components import render_sebi_disclaimer

def page_home():
    mkt = st.session_state.get("market_mode", "🇮🇳 India")
    pill_label = "✓ 500 Indian Stocks" if mkt == "🇮🇳 India" else "✓ 300 US Stocks"
    
    st.markdown(f"""<div style="padding:40px 0 20px">
      <div class="hero-title"><span class="gradient">StockSense</span> AI</div>
      <div class="hero-sub">Smart Stock Analysis · Risk-Aware · Built for You</div>
      <div class="hero-pills">
        <span class="hero-pill green">{pill_label}</span>
        <span class="hero-pill purple">✓ Live Market Data</span>
        <span class="hero-pill gold">✓ Auto Risk Filter</span>
        <span class="hero-pill red">✗ Not Financial Advice</span>
      </div>
      <div style="text-align:center;margin-bottom:30px">
        <button onclick="parent.document.querySelector('[data-testid=\\'baseButton-primary\\']#btn_start').click()" style="padding:12px 24px;border-radius:24px;background:var(--accent-green);color:#0D0D0D;font-weight:700;font-size:14px;border:none;cursor:pointer;transition:transform 0.2s;box-shadow:0 4px 12px rgba(0,208,156,0.3)">
            🚀 Start Here — Get your first stock analysis
        </button>
      </div>
    </div>""", unsafe_allow_html=True)
    
    # Hide the ugly standard button with custom CSS and use it to capture click
    st.markdown("<style>#btn_start { display: none !important; }</style>", unsafe_allow_html=True)
    if st.button("Start Here", key="btn_start"):
        st.session_state.prev_page="home"; st.session_state.page="beginner"; st.session_state.beginner_step=1; st.session_state.bq={}; st.rerun()

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="mode-card"><div class="mode-icon">🌱</div><div class="mode-title green">Beginner Mode</div>
          <div class="mode-desc">Answer a few quick questions.<br>We handle all the analysis.</div>
          <div class="mode-tag">Perfect for first-time investors.</div></div>""", unsafe_allow_html=True)
        if st.button("Start as Beginner 🌱",key="btn_beg",use_container_width=True):
            st.session_state.prev_page="home";st.session_state.page="beginner";st.session_state.beginner_step=1;st.session_state.bq={};st.rerun()
    with c2:
        st.markdown("""<div class="mode-card"><div class="mode-icon">🚀</div><div class="mode-title purple">Pro Mode</div>
          <div class="mode-desc">Set your own thresholds.<br>Full control over every metric.</div>
          <div class="mode-tag">For experienced investors.</div></div>""", unsafe_allow_html=True)
        if st.button("Enter Pro Mode 🚀",key="btn_pro",use_container_width=True):
            st.session_state.prev_page="home";st.session_state.page="pro";st.rerun()
    with c3:
        st.markdown("""<div class="mode-card"><div class="mode-icon">🔥</div><div class="mode-title gold">Trending Now</div>
          <div class="mode-desc">See today's popular stocks.<br>Quick snapshot of the market.</div>
          <div class="mode-tag">See Top Gainers/Losers.</div></div>""", unsafe_allow_html=True)
        if st.button("View Trending 🔥",key="btn_trend",use_container_width=True):
            st.session_state.prev_page="home";st.session_state.page="trending";st.rerun()
            
    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        st.markdown("""<div class="ss-card" style="text-align:center;padding:18px"><div style="font-size:1.5rem">🆚</div>
          <div style="font-weight:700;margin:6px 0">Compare 3 Stocks</div>
          <div style="color:#9E9E9E;font-size:.83rem">Side-by-side analysis</div></div>""", unsafe_allow_html=True)
        if st.button("Compare Stocks",key="btn_cmp",use_container_width=True):
            st.session_state.prev_page="home";st.session_state.page="compare";st.rerun()
    with cb:
        st.markdown("""<div class="ss-card" style="text-align:center;padding:18px"><div style="font-size:1.5rem">🔍</div>
          <div style="font-weight:700;margin:6px 0">Search Any Stock</div>
          <div style="color:#9E9E9E;font-size:.83rem">Full AI & Technical analysis</div></div>""", unsafe_allow_html=True)
        if st.button("Search Stock",key="btn_srch",use_container_width=True):
            st.session_state.prev_page="home";st.session_state.page="search";st.rerun()

    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📰 Latest Market News ({"India" if mkt == "🇮🇳 India" else "US"})</div>', unsafe_allow_html=True)
    with st.spinner("Fetching market news..."):
        mnews = get_market_news(market=mkt)
    if mnews:
        for item in mnews:
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
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none"><div class="mnews-card"><div style="font-weight:600;font-size:.9rem;color:var(--text-primary);margin-bottom:4px">{title}</div><div style="font-size:.75rem;color:var(--text-muted)">{publisher} · {time_str}</div></div></a>', unsafe_allow_html=True)
    else:
        st.info("Market news currently unavailable.")

    render_sebi_disclaimer()
