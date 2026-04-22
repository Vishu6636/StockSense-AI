import streamlit as st
import base64
import os
import plotly.graph_objects as go
import plotly.express as px
from data_service import get_index_data, get_market_indices, search_tickers
import streamlit.components.v1 as components

# ── LOGO & CSS ──
LOGO_SVG = '''<svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="1" y="1" width="28" height="28" rx="7" fill="#1A1A1A" stroke="#00D09C" stroke-width="1.5"/>
<line x1="8.5" y1="7" x2="8.5" y2="10" stroke="#00D09C" stroke-width="1.5" stroke-linecap="round"/>
<rect x="7" y="10" width="3" height="9" rx="1" fill="#00D09C"/>
<line x1="14.5" y1="6" x2="14.5" y2="9" stroke="#EB5B3C" stroke-width="1.5" stroke-linecap="round"/>
<rect x="13" y="9" width="3" height="11" rx="1" fill="#EB5B3C"/>
<line x1="20.5" y1="8" x2="20.5" y2="11" stroke="#00D09C" stroke-width="1.5" stroke-linecap="round"/>
<rect x="19" y="11" width="3" height="8" rx="1" fill="#00D09C"/>
</svg>'''

def inject_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root {
      --bg-primary:#0D0D0D;--bg-secondary:#151515;--bg-card:#1A1A1A;--bg-card2:#222222;
      --bg-hover:#2A2A2A;--accent-green:#00D09C;--accent-red:#EB5B3C;--accent-gold:#E8A838;
      --accent-purple:#7C5CFC;--accent-blue:#4C9AFF;--text-primary:#FAFAFA;
      --text-secondary:#9E9E9E;--text-muted:#616161;--border:#2A2A2A;--border-hover:#3A3A3A;
    }
    html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif!important;background-color:var(--bg-primary)!important;color:var(--text-primary)!important}
    .main{background:var(--bg-primary)!important;padding:0!important}
    .block-container{padding:0 2rem 2rem!important;max-width:1200px!important}
    #MainMenu,footer,header{visibility:hidden!important}.stDeployButton{display:none!important}

    /* Loading */
    .loading-overlay{position:fixed;top:0;left:0;width:100vw;height:100vh;background:#0D0D0D;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:99999;animation:fadeOut .6s ease 2.8s forwards}
    @keyframes fadeOut{to{opacity:0;pointer-events:none}}
    .candle-loader{display:flex;gap:10px;align-items:flex-end;height:100px;margin-bottom:20px;position:relative}
    .candle{width:14px;border-radius:3px;animation:candlePulse .8s ease-in-out infinite alternate}
    .candle.green{background:var(--accent-green)}.candle.red{background:var(--accent-red)}
    .candle:nth-child(1){height:45px;animation-delay:0s}.candle:nth-child(2){height:65px;animation-delay:.15s}
    .candle:nth-child(3){height:35px;animation-delay:.3s}.candle:nth-child(4){height:80px;animation-delay:.45s}
    .candle:nth-child(5){height:55px;animation-delay:.6s}.candle:nth-child(6){height:70px;animation-delay:.75s}
    @keyframes candlePulse{0%{transform:scaleY(.7);opacity:.5}100%{transform:scaleY(1.2);opacity:1}}
    .bull-runner{position:absolute;bottom:10px;left:0;width:70px;height:auto;animation:bullRun 2.5s linear infinite;filter:invert(0.9) sepia(1) saturate(3) hue-rotate(110deg);z-index:10}
    @keyframes bullRun{0%{transform:translateX(-80px)}100%{transform:translateX(150px)}}
    .loading-text{color:var(--text-secondary);font-size:.9rem;margin-top:16px;letter-spacing:.5px}

    /* Ticker marquee */
    .ticker-bar{background:#151515!important;border-bottom:1px solid #2A2A2A;overflow:hidden;white-space:nowrap;padding:10px 0;position:sticky;top:0;z-index:100}
    .ticker-scroll{display:inline-block;animation:tickerScroll 25s linear infinite;font-family:'JetBrains Mono',monospace;font-size:13px}
    .ticker-scroll:hover{animation-play-state:paused}
    @keyframes tickerScroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    .ticker-item{display:inline-flex;align-items:center;gap:6px;margin-right:40px}
    .ticker-name{color:#9E9E9E!important;font-weight:500}.ticker-price{color:#FAFAFA!important;font-weight:700}
    .ticker-change.up{color:#00D09C!important}.ticker-change.down{color:#EB5B3C!important}
    .live-dot{width:6px;height:6px;border-radius:50%;background:#00D09C;animation:pulseDot 1.5s ease infinite;display:inline-block;margin-right:12px}
    @keyframes pulseDot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.7)}}

    /* Navbar */
    .navbar-brand{background:var(--bg-secondary);padding:16px 24px 6px;display:flex;align-items:center;justify-content:space-between}
    .nav-logo{display:flex;align-items:center;gap:10px;font-size:1.4rem;font-weight:700;color:var(--text-primary)}
    .nav-version{font-size:.6rem;color:var(--text-muted);margin-left:4px;letter-spacing:1px}

    /* Search bar styling */
    .search-wrap{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:2px 4px;margin-bottom:6px}
    .search-wrap:focus-within{border-color:var(--accent-green);box-shadow:0 0 0 2px rgba(0,208,156,.12)}

    /* Cards */
    .ss-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px;transition:all .2s ease}
    .ss-card:hover{border-color:var(--border-hover);background:var(--bg-card2)}

    /* Metric chips + info tooltip */
    .metric-row{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
    .metric-chip{background:var(--bg-card2);border:1px solid var(--border);border-radius:10px;padding:12px 16px;min-width:140px;position:relative}
    .metric-chip .label{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.8px;font-weight:600;display:flex;align-items:center;gap:6px}
    .metric-chip .value{font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:700;color:var(--text-primary);margin-top:4px}
    .metric-chip .value.green{color:var(--accent-green)}.metric-chip .value.red{color:var(--accent-red)}.metric-chip .value.gold{color:var(--accent-gold)}
    .info-i{display:inline-flex;align-items:center;justify-content:center;width:15px;height:15px;border-radius:50%;background:var(--bg-hover);color:var(--text-muted);font-size:9px;font-weight:700;cursor:help;position:relative;font-style:normal}
    .info-i:hover{background:var(--accent-purple);color:#fff}
    .info-i .info-tip{display:none;position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%);background:#2A2A2A;border:1px solid #3A3A3A;border-radius:8px;padding:10px 14px;width:220px;font-size:11px;line-height:1.5;color:var(--text-secondary);font-weight:400;text-transform:none;letter-spacing:0;z-index:1000;box-shadow:0 8px 24px rgba(0,0,0,.4)}
    .info-i .info-tip strong{color:var(--text-primary);display:block;margin-bottom:4px}
    .info-i:hover .info-tip{display:block}

    /* Buttons */
    .stButton>button,button[data-testid="baseButton-primary"]{background:var(--accent-green)!important;color:#0D0D0D!important;font-weight:700!important;border:none!important;border-radius:8px!important;padding:8px 8px!important;font-size:13px!important;transition:all .2s ease!important;font-family:'Inter',sans-serif!important;white-space:nowrap!important;display:flex!important;align-items:center!important;justify-content:center!important;height:44px!important;text-overflow:ellipsis!important;overflow:hidden!important}
    .stButton>button:hover,button[data-testid="baseButton-primary"]:hover{filter:brightness(1.1)!important;transform:translateY(-1px)!important;box-shadow:0 4px 12px rgba(0,208,156,.3)!important}
    button[data-testid="baseButton-secondary"]{background:var(--bg-card2)!important;color:var(--text-secondary)!important;font-weight:600!important;border:1px solid var(--border)!important;border-radius:8px!important;padding:8px 8px!important;transition:all .2s ease!important;font-family:'Inter',sans-serif!important;white-space:nowrap!important;display:flex!important;align-items:center!important;justify-content:center!important;height:44px!important;text-overflow:ellipsis!important;overflow:hidden!important}
    button[data-testid="baseButton-secondary"]:hover{border-color:var(--accent-green)!important;color:var(--accent-green)!important;background:rgba(0,208,156,.08)!important}

    /* Section */
    .section-title{font-size:1.15rem;font-weight:700;color:var(--text-primary);border-left:3px solid var(--accent-green);padding-left:12px;margin:20px 0 12px}
    .section-subtitle{font-size:.85rem;color:var(--text-secondary);margin-bottom:14px}

    /* Login */
    .login-greeting{font-size:1.5rem;font-weight:700;text-align:center;margin-bottom:6px;color:var(--text-primary)}
    .login-sub{text-align:center;color:var(--text-secondary);font-size:.85rem;margin-bottom:28px}
    .divider{display:flex;align-items:center;gap:12px;margin:20px 0}.divider hr{flex:1;border-color:var(--border)}.divider span{color:var(--text-muted);font-size:12px}

    /* Hero */
    .hero-title{font-size:2.8rem;font-weight:800;color:var(--text-primary);text-align:center;line-height:1.15;margin-bottom:10px;letter-spacing:-1px}
    .hero-title .gradient{background:linear-gradient(135deg,var(--accent-green),var(--accent-purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .hero-sub{text-align:center;color:var(--text-secondary);font-size:1rem;margin-bottom:20px}
    .hero-pills{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:32px}
    .hero-pill{padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid var(--border);color:var(--text-secondary);background:var(--bg-card)}
    .hero-pill.green{border-color:rgba(0,208,156,.3);color:var(--accent-green)}
    .hero-pill.purple{border-color:rgba(124,92,252,.3);color:var(--accent-purple)}
    .hero-pill.gold{border-color:rgba(232,168,56,.3);color:var(--accent-gold)}
    .hero-pill.red{border-color:rgba(235,91,60,.3);color:var(--accent-red)}

    /* Mode cards */
    .mode-card{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:28px 22px;text-align:center;cursor:pointer;transition:all .25s ease}
    .mode-card:hover{transform:translateY(-3px);border-color:var(--border-hover);box-shadow:0 8px 24px rgba(0,0,0,.3)}
    .mode-icon{font-size:2.2rem;margin-bottom:12px}.mode-title{font-size:1.1rem;font-weight:700;margin-bottom:6px}
    .mode-title.green{color:var(--accent-green)}.mode-title.purple{color:var(--accent-purple)}.mode-title.gold{color:var(--accent-gold)}
    .mode-desc{color:var(--text-secondary);font-size:.83rem;line-height:1.5}.mode-tag{font-style:italic;color:var(--text-muted);font-size:.75rem;margin-top:6px}

    /* Badge */
    .badge{display:inline-block;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;letter-spacing:.3px}
    .badge-green{background:rgba(0,208,156,.12);color:var(--accent-green)}
    .badge-red{background:rgba(235,91,60,.12);color:var(--accent-red)}
    .badge-gold{background:rgba(232,168,56,.12);color:var(--accent-gold)}
    .badge-blue{background:rgba(76,154,255,.12);color:var(--accent-blue)}
    .badge-gray{background:rgba(158,158,158,.12);color:var(--text-secondary)}

    /* Breadcrumb */
    .breadcrumb{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text-muted);padding:12px 0}
    .breadcrumb .active{color:var(--accent-green);font-weight:600}.breadcrumb .sep{color:var(--border-hover)}

    /* Inputs */
    .stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input{background:var(--bg-card)!important;border:1px solid var(--border)!important;color:var(--text-primary)!important;border-radius:8px!important}
    .stTextInput>div>div>input:focus{border-color:var(--accent-green)!important;box-shadow:0 0 0 2px rgba(0,208,156,.12)!important}
    .stSlider>div>div>div{background:var(--accent-green)!important}
    .stRadio>div{gap:8px!important}.stRadio label{color:var(--text-secondary)!important}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"]{background:var(--bg-secondary)!important;border-radius:10px;padding:4px;gap:2px;border:1px solid var(--border)}
    .stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-muted)!important;border-radius:8px!important;font-weight:600!important;font-size:13px!important}
    .stTabs [aria-selected="true"]{background:var(--accent-green)!important;color:#0D0D0D!important}
    .stTabs [data-baseweb="tab-panel"]{padding:16px 0!important}
    .stTabs [data-baseweb="tab-list"] {gap: 12px!important}
    .stTabs [data-baseweb="tab-list"] button {padding: 10px 16px!important; margin-right: 4px!important; white-space:nowrap!important; height:auto!important}

    /* Analyst */
    .analyst-bar-wrap{background:var(--bg-card2);border-radius:10px;padding:14px;margin:10px 0}
    .analyst-bar{height:8px;border-radius:4px;margin:8px 0;background:linear-gradient(90deg,var(--accent-red) 0%,var(--accent-gold) 50%,var(--accent-green) 100%);position:relative}
    .analyst-needle{position:absolute;top:-5px;width:18px;height:18px;border-radius:50%;background:#fff;border:3px solid var(--accent-green);transform:translateX(-50%);transition:left .8s cubic-bezier(.34,1.56,.64,1)}

    /* News */
    .news-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:8px;border-left:3px solid var(--accent-green);transition:all .2s}
    .news-card:hover{border-left-color:var(--accent-gold);background:var(--bg-card2)}
    .news-title{font-weight:600;font-size:.88rem;color:var(--text-primary)}.news-meta{font-size:.75rem;color:var(--text-muted);margin-top:4px}

    /* Investor */
    .investor-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;transition:all .2s}
    .investor-card:hover{border-color:var(--accent-gold)}
    .investor-name{font-weight:600;font-size:.88rem}.investor-type{font-size:.75rem;color:var(--text-muted)}
    .investor-holding{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--accent-gold)}

    /* Recommendation */
    .rec-banner{border-radius:12px;padding:18px 24px;display:flex;align-items:center;gap:16px;margin:16px 0}
    .rec-banner.buy{background:rgba(0,208,156,.08);border:1px solid rgba(0,208,156,.25)}
    .rec-banner.sell{background:rgba(235,91,60,.08);border:1px solid rgba(235,91,60,.25)}
    .rec-banner.hold{background:rgba(232,168,56,.08);border:1px solid rgba(232,168,56,.25)}
    .rec-icon{font-size:2rem}.rec-label{font-size:1.3rem;font-weight:800}
    .rec-label.buy{color:var(--accent-green)}.rec-label.sell{color:var(--accent-red)}.rec-label.hold{color:var(--accent-gold)}
    .rec-reason{color:var(--text-secondary);font-size:.85rem;margin-top:3px}

    /* Simulator */
    .sim-result{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center}
    .sim-amount{font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700}

    /* Misc */
    .ss-sep{border:none;border-top:1px solid var(--border);margin:20px 0}
    ::-webkit-scrollbar{width:5px;height:5px}::-webkit-scrollbar-track{background:var(--bg-primary)}::-webkit-scrollbar-thumb{background:var(--border-hover);border-radius:3px}
    .watermark{text-align:center;color:var(--text-muted);font-size:11px;padding:24px;border-top:1px solid var(--border);margin-top:40px}
    .stAlert{border-radius:10px!important}
    .dataframe{background:var(--bg-card)!important}thead tr th{background:var(--bg-card2)!important;color:var(--text-secondary)!important}tbody tr:hover{background:var(--bg-card2)!important}
    .streamlit-expanderHeader{background:var(--bg-card)!important;border-radius:8px!important}
    .stSpinner>div{border-top-color:var(--accent-green)!important}

    /* Watchlist */
    .wl-stock{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin-bottom:10px;transition:all .2s ease}
    .wl-stock:hover{border-color:var(--accent-green);background:var(--bg-card2)}
    .wl-empty{text-align:center;padding:60px 20px;color:var(--text-muted)}
    .wl-empty .wl-icon{font-size:3rem;margin-bottom:12px}

    /* AI Summary */
    .ai-card{background:linear-gradient(135deg,rgba(124,92,252,.06),rgba(0,208,156,.06));border:1px solid rgba(124,92,252,.2);border-radius:14px;padding:24px;margin:12px 0;line-height:1.8}
    .ai-card p{color:var(--text-secondary);font-size:.9rem;margin-bottom:12px}
    .ai-card strong{color:var(--text-primary)}
    .ai-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(124,92,252,.12);border:1px solid rgba(124,92,252,.25);border-radius:20px;padding:5px 14px;font-size:12px;font-weight:600;color:#7C5CFC;margin-bottom:16px}

    /* Guest lock */
    .guest-lock{text-align:center;padding:40px 20px;background:var(--bg-card);border:1px solid var(--border);border-radius:14px}
    .guest-lock .lock-icon{font-size:2.5rem;margin-bottom:12px}
    .guest-lock .lock-title{font-size:1.1rem;font-weight:700;color:var(--text-primary);margin-bottom:6px}
    .guest-lock .lock-desc{color:var(--text-secondary);font-size:.85rem;margin-bottom:16px}

    /* Market news */
    .mnews-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:8px;transition:all .2s;border-left:3px solid var(--accent-purple)}
    .mnews-card:hover{border-left-color:var(--accent-green);background:var(--bg-card2)}

    /* Market toggle pill */
    div[data-testid="stRadio"] > div {
        display: flex !important; gap: 6px !important; background: #1a1a2e !important;
        padding: 4px !important; border-radius: 30px !important; width: fit-content !important;
    }
    div[data-testid="stRadio"] > div > label {
        padding: 6px 20px !important; border-radius: 30px !important; cursor: pointer !important;
        font-size: 14px !important; font-weight: 500 !important; color: #aaa !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] > div > label:has(input:checked) {
        background: #ffffff14 !important; color: #fff !important;
        box-shadow: 0 0 0 1px #ffffff22 !important;
    }

    @media(max-width:768px){
        .block-container{padding:0 1rem 1rem!important}
        .hero-title{font-size:1.8rem}
        .metric-chip{min-width:110px;padding:8px 12px}
        .metric-chip .value{font-size:.95rem}
        .mode-card{padding:18px 14px}
        .info-i .info-tip{width:180px;font-size:10px}
        .nav-logo{font-size:1.1rem}
    }
    </style>""", unsafe_allow_html=True)


def render_loading():
    if not st.session_state.get("app_loaded"):
        b64_str = ""
        gif_path = "real_bull.gif"
        if os.path.exists(gif_path):
            with open(gif_path, "rb") as f:
                b64_str = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="loading-overlay">
          <div class="candle-loader">
            <img class="bull-runner" src="data:image/gif;base64,{b64_str}" alt="Running Bull">
            <div class="candle green"></div>
            <div class="candle red"></div>
            <div class="candle green"></div>
            <div class="candle red"></div>
            <div class="candle green"></div>
            <div class="candle red"></div>
          </div>
          <div class="loading-text">Loading StockSense AI...</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.app_loaded = True


def render_ticker_bar():
    indices = get_market_indices()
    data = get_index_data(indices)
    items = '<span class="live-dot"></span>'
    for name, d in data.items():
        direction = "up" if d["pct"] >= 0 else "down"
        arrow = "▲" if d["pct"] >= 0 else "▼"
        items += (f'<span class="ticker-item"><span class="ticker-name">{name}</span>'
                  f'<span class="ticker-price">{d["price"]:,.0f}</span>'
                  f'<span class="ticker-change {direction}">{arrow} {abs(d["pct"]):.2f}%</span></span>')
    st.markdown(f'<div class="ticker-bar"><div class="ticker-scroll">{items}{items}</div></div>',
                unsafe_allow_html=True)


def render_navbar():
    current_page = st.session_state.page
    market = st.session_state.get("market_mode", "🇮🇳 India")

    nav_items = [
        ("🏠 Home", "home"),
        ("🌱 Beginner", "beginner"),
        ("🚀 Pro", "pro"),
        ("🔥 Trending", "trending"),
        ("🆚 Compare", "compare"),
        ("📋 Watchlist", "watchlist"),
    ]

    # ── ROW 1: Logo + Mobile hamburger ──
    logo_col, mob_col = st.columns([6, 1], vertical_alignment="center")
    with logo_col:
        market_label = "500 Indian Stocks · Live Data" if market == "🇮🇳 India" else "300 US Stocks · Live Data"
        st.markdown(f'''
        <div class="navbar-brand">
          <div class="nav-logo">{LOGO_SVG}
            <span style="font-size:1.4rem;font-weight:700;color:#FAFAFA">StockSense AI</span>
            <span style="font-size:.6rem;color:#616161;margin-left:4px;letter-spacing:1px">v4.0</span>
          </div>
          <div style="color:#616161;font-size:11px;font-family:'JetBrains Mono',monospace">{market_label}</div>
        </div>''', unsafe_allow_html=True)

    with mob_col:
        # Mobile only — hamburger popover (always rendered but only useful on mobile)
        with st.popover("☰", use_container_width=True,
                        key=f"mob_pop_{st.session_state.get('nav_counter', 0)}"):
            for label, page in nav_items:
                is_active = current_page == page
                if st.button(label, key=f"mob_{page}",
                             use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.prev_page = current_page
                    st.session_state.page = page
                    st.session_state.nav_counter = st.session_state.get("nav_counter", 0) + 1
                    if page == "beginner" and current_page != "beginner":
                        st.session_state.beginner_step = 1
                        st.session_state.bq = {}
                    st.rerun()
            st.markdown("---")
            if st.session_state.logged_in:
                st.markdown(f'<div style="color:#E8A838;font-size:12px;font-weight:600;padding:4px 0">👤 {st.session_state.user_name}</div>',
                            unsafe_allow_html=True)
                if st.button("🚪 Logout", key="mob_logout", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.user_name = "Guest"
                    st.session_state.page = "home"
                    st.session_state.nav_counter = st.session_state.get("nav_counter", 0) + 1
                    if "cookie_controller" in st.session_state:
                        st.session_state.cookie_controller.set("ss_email", "")
                        st.session_state.cookie_controller.set("ss_name", "")
                    st.rerun()
            else:
                if st.button("🔐 Login", key="mob_login", use_container_width=True,
                             type="primary" if current_page == "login" else "secondary"):
                    st.session_state.prev_page = current_page
                    st.session_state.page = "login"
                    st.session_state.nav_counter = st.session_state.get("nav_counter", 0) + 1
                    st.rerun()

    st.markdown('<hr class="ss-sep" style="margin:6px 0 10px"/>', unsafe_allow_html=True)

    # ── ROW 2: Search bar (full width, always visible) ──
    search_placeholder = "🔍 Search Indian stocks by name or ticker..." if market == "🇮🇳 India" else "🔍 Search US stocks by name or ticker..."
    search_query = st.text_input(
        "Stock Search",
        placeholder=search_placeholder,
        key="global_search_input",
        label_visibility="collapsed"
    )
    if search_query and len(search_query) > 1:
        results = search_tickers(search_query, market)
        if results:
            def on_search_click(ticker, name, curr_page):
                st.session_state.search_ticker = ticker
                st.session_state.last_search = name
                st.session_state.prev_page = curr_page
                st.session_state.page = "search"
                st.session_state["global_search_input"] = ""

            result_cols = st.columns(min(len(results), 3))
            for idx, r in enumerate(results[:6]):
                with result_cols[idx % 3]:
                    btn_label = f"{r['name'][:28]}  ({r['ticker']})"
                    st.button(btn_label, key=f"gs_{r['ticker']}_{idx}",
                              use_container_width=True, type="secondary",
                              on_click=on_search_click, args=(r["ticker"], r["name"], current_page))
        else:
            st.caption("No results found.")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    # ── ROW 3: Desktop nav buttons + Login (hidden on mobile via CSS) ──
    # Hide desktop nav on mobile and mobile hamburger on desktop using CSS
    st.markdown("""
    <style>
    /* Hide mobile hamburger column on desktop */
    @media(min-width: 769px) {
        div[data-testid="stHorizontalBlock"]:has(.nav-logo) > div:nth-child(2) {
            display: none !important;
        }
    }
    
    /* Hide desktop nav row on mobile */
    @media(max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.desktop-nav-marker) {
            display: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    nav_cols = st.columns([1, 1, 1, 1, 1, 1, 1])  # 6 nav + 1 login
    for i, (label, page) in enumerate(nav_items):
        with nav_cols[i]:
            if i == 0:
                st.markdown('<div class="desktop-nav-marker"></div>', unsafe_allow_html=True)
            is_active = current_page == page
            if st.button(label, key=f"nav_{page}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.prev_page = current_page
                st.session_state.page = page
                if page == "beginner" and current_page != "beginner":
                    st.session_state.beginner_step = 1
                    st.session_state.bq = {}
                st.rerun()

    with nav_cols[6]:
        if st.session_state.logged_in:
            with st.popover(f"👤 {st.session_state.user_name[:8]}", use_container_width=True):
                if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.user_name = "Guest"
                    st.session_state.page = "home"
                    if "cookie_controller" in st.session_state:
                        st.session_state.cookie_controller.set("ss_email", "")
                        st.session_state.cookie_controller.set("ss_name", "")
                    st.rerun()
        else:
            if st.button("🔐 Login", key="nav_login",
                         use_container_width=True,
                         type="primary" if current_page == "login" else "secondary"):
                st.session_state.prev_page = current_page
                st.session_state.page = "login"
                st.rerun()

    st.markdown('<hr class="ss-sep" style="margin:10px 0 16px"/>', unsafe_allow_html=True)

    # ── ROW 4: Market toggle ──
    c_mode, _ = st.columns([2, 3])
    with c_mode:
        selected_market = st.radio(
            "Market",
            ["🇮🇳 ₹ India", "🇺🇸 $ US"],
            horizontal=True,
            index=0 if market == "🇮🇳 India" else 1,
            label_visibility="collapsed"
        )
        resolved_market = "🇮🇳 India" if "India" in selected_market else "🇺🇸 US"
        if resolved_market != st.session_state.get("market_mode", "🇮🇳 India"):
            st.session_state.market_mode = resolved_market
            st.session_state._currency = "₹" if resolved_market == "🇮🇳 India" else "$"
            st.rerun()

    # Hide Streamlit sidebar toggle
    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;
        var toggle = doc.querySelector('button[data-testid="collapsedControl"]');
        var sidebar = doc.querySelector('section[data-testid="stSidebar"]');
        if (toggle) toggle.style.display = 'none';
        if (sidebar) sidebar.style.display = 'none';
    })();
    </script>
    """, height=0, width=0)


def render_back_button(label="← Back"):
    if st.button(label, key=f"back_{st.session_state.page}", type="secondary"):
        st.session_state.page = st.session_state.prev_page or "home"
        st.rerun()


def render_breadcrumb(steps, current):
    parts = []
    for i, step in enumerate(steps):
        parts.append(f'<span class="active">{step}</span>' if i == current else f'<span>{step}</span>')
        if i < len(steps) - 1:
            parts.append('<span class="sep">›</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)


def safe_pct(value, max_val=80.0, min_val=-100.0, label=""):
    """Returns formatted % string or '—' for None, NaN, or physically impossible values."""
    if value is None:
        return "—"
    try:
        v = float(value)
        if v != v:  # NaN check
            return "—"
        if label in ("Div Yield", "Dividend Yield") and (v < 0 or v > 20):
            return "—"
        if v > max_val or v < min_val:
            return "—"
        return f"{v:.1f}%"
    except Exception:
        return "—"


def safe_ratio(value):
    """Returns formatted ratio string or '—' for None, NaN, negative, or >999."""
    if value is None:
        return "—"
    try:
        v = float(value)
        if v != v or v <= 0 or v > 999:
            return "—"
        return f"{v:.2f}"
    except Exception:
        return "—"


def metric_chip(label, value, color="", tip_html=""):
    return (f'<div class="metric-chip"><div class="label">{label} {tip_html}</div>'
            f'<div class="value {color}">{value}</div></div>')


def render_metric_row(chips):
    st.markdown('<div class="metric-row">' + "".join(chips) + '</div>', unsafe_allow_html=True)


def render_badge(text, kind="gray"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def render_stock_header(info):
    name = info.get("longName") or info.get("shortName") or "Unknown"
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    prev = info.get("previousClose") or price
    chg = price - prev
    pct = (chg / prev * 100) if prev else 0
    direction = "up" if chg >= 0 else "down"
    arrow = "▲" if chg >= 0 else "▼"
    sector = info.get("sector") or "N/A"
    mcap = info.get("marketCap") or 0
    exchange = info.get("exchange") or "EXCHANGE"

    _cur = st.session_state.get("_currency", "₹")
    if _cur == "₹":
        mcap_str = f"{_cur}{mcap / 1e7:,.0f} Cr" if mcap else "N/A"
    else:
        mcap_str = f"{_cur}{mcap / 1e9:,.2f} B" if mcap else "N/A"

    st.markdown(f"""
    <div class="ss-card" style="margin-bottom:16px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
        <div>
          <div style="font-size:1.5rem;font-weight:800;color:#FAFAFA;margin-bottom:4px">{name}</div>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            {render_badge(sector, "gray")}
            {render_badge(exchange, "blue")}
            <span style="color:#9E9E9E;font-size:12px">Market Cap: {mcap_str}</span>
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#FAFAFA">{_cur}{price:,.2f}</div>
          <div class="ticker-change {direction}" style="font-size:1rem;font-weight:600">
            {arrow} {abs(chg):,.2f} ({abs(pct):.2f}%)
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_sebi_disclaimer():
    st.markdown("""<div style="background:rgba(235,91,60,.06);border:1px solid rgba(235,91,60,.15);border-radius:10px;padding:12px 16px;margin-top:16px">
      <span style="color:#EB5B3C;font-weight:700;font-size:12px">⚠️ Disclaimer:</span>
      <span style="color:#9E9E9E;font-size:12px"> StockSense AI is educational only. NOT registered with SEBI or SEC. Always consult a registered advisor. Investments are subject to market risk.</span>
    </div>""", unsafe_allow_html=True)


# ── CHARTS ──
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26,26,26,0.8)",
    font=dict(family="Inter", color="#9E9E9E"),
    xaxis=dict(gridcolor="#2A2A2A", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#2A2A2A", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=30, b=10),
)


def apply_theme(fig, height=300, title="", extra_yaxis=None):
    layout = {k: v for k, v in CHART_THEME.items() if k != "yaxis" and k != "xaxis"}
    layout["xaxis"] = dict(**CHART_THEME["xaxis"])
    if extra_yaxis:
        layout["yaxis"] = {**CHART_THEME["yaxis"], **extra_yaxis}
    else:
        layout["yaxis"] = dict(**CHART_THEME["yaxis"])
    layout["height"] = height
    layout["title"] = title
    layout["title_font"] = dict(size=13, color="#FAFAFA")
    fig.update_layout(**layout)
    return fig


def candlestick_chart(hist, title="Price Chart"):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        increasing_line_color="#00D09C", decreasing_line_color="#EB5B3C",
        increasing_fillcolor="#00D09C", decreasing_fillcolor="#EB5B3C", name="OHLC"))
    apply_theme(fig, height=380, title=title)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def volume_chart(hist):
    colors = ["#00D09C" if c >= o else "#EB5B3C" for c, o in zip(hist["Close"], hist["Open"])]
    fig = go.Figure(go.Bar(x=hist.index, y=hist["Volume"], marker_color=colors, name="Volume", opacity=0.8))
    apply_theme(fig, height=160, title="Volume")
    return fig


def rsi_chart(rsi_series):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rsi_series.index, y=rsi_series.values,
                             line=dict(color="#00D09C", width=2), name="RSI"))
    fig.add_hline(y=70, line_dash="dash", line_color="#EB5B3C", opacity=0.6)
    fig.add_hline(y=30, line_dash="dash", line_color="#00D09C", opacity=0.6)
    fig.add_hrect(y0=70, y1=100, fillcolor="#EB5B3C", opacity=0.05, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="#00D09C", opacity=0.05, line_width=0)
    apply_theme(fig, height=200, title="RSI (14)", extra_yaxis={"range": [0, 100]})
    return fig


def macd_chart(macd, signal, hist_macd):
    colors = ["#00D09C" if v >= 0 else "#EB5B3C" for v in hist_macd.values]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=macd.index, y=macd.values,
                             line=dict(color="#4C9AFF", width=2), name="MACD"))
    fig.add_trace(go.Scatter(x=signal.index, y=signal.values,
                             line=dict(color="#E8A838", width=2), name="Signal"))
    fig.add_trace(go.Bar(x=hist_macd.index, y=hist_macd.values,
                         marker_color=colors, name="Histogram", opacity=0.7))
    apply_theme(fig, height=200, title="MACD")
    return fig


def bollinger_chart(hist, ta):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=ta["bb_upper"].values,
                             line=dict(color="#E8A838", width=1, dash="dash"), name="Upper"))
    fig.add_trace(go.Scatter(x=hist.index, y=ta["bb_lower"].values,
                             line=dict(color="#E8A838", width=1, dash="dash"), name="Lower",
                             fill="tonexty", fillcolor="rgba(232,168,56,0.05)"))
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"].values,
                             line=dict(color="#00D09C", width=2), name="Close"))
    fig.add_trace(go.Scatter(x=hist.index, y=ta["ma20"].values,
                             line=dict(color="#FAFAFA", width=1, dash="dot"), name="MA20"))
    apply_theme(fig, height=300, title="Bollinger Bands")
    return fig


def radar_chart(info):
    pe = info.get("trailingPE") or info.get("forwardPE") or 50
    if isinstance(pe, str): pe = 50
    roe = (info.get("returnOnEquity") or 0) * 100
    de = (info.get("debtToEquity") or 50) / 100 if (info.get("debtToEquity") or 0) > 10 else (
                info.get("debtToEquity") or 1)
    sales_g = (info.get("revenueGrowth") or 0) * 100
    profit_g = (info.get("earningsGrowth") or 0) * 100
    promoter = (info.get("heldPercentInsiders") or 0) * 100
    vals = [
        max(0, min(100, (25 - min(pe, 25)) / 25 * 100)),
        max(0, min(100, roe * 3)),
        max(0, min(100, (2 - min(de, 2)) / 2 * 100)),
        max(0, min(100, sales_g * 3)),
        max(0, min(100, profit_g * 2)),
        max(0, min(100, promoter))
    ]
    cats = ["Valuation", "ROE", "Low Debt", "Sales Growth", "Profit", "Promoter"]
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
        fillcolor="rgba(0,208,156,0.15)", line=dict(color="#00D09C", width=2), name="Fundamentals"))
    fig.update_layout(
        polar=dict(bgcolor="rgba(26,26,26,0.8)",
                   radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2A2A2A",
                                   tickcolor="#2A2A2A", tickfont=dict(color="#616161", size=9)),
                   angularaxis=dict(gridcolor="#2A2A2A", tickfont=dict(color="#9E9E9E", size=11))),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#9E9E9E"), height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        title="Fundamental Scorecard", title_font=dict(size=13, color="#FAFAFA"))
    return fig