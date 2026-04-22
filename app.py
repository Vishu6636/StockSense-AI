"""
StockSense AI — Production-Grade Stock Analysis Platform
Version: 4.0.0 | Launch-Ready Edition
"""
import streamlit as st
import warnings

# Use CookieController for persistent session
try:
    from streamlit_cookies_controller import CookieController
except ImportError:
    CookieController = None

warnings.filterwarnings("ignore")

st.set_page_config(page_title="StockSense AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

from ui_components import inject_css, render_loading, render_ticker_bar, render_navbar
from views.home import page_home
from views.search import page_search
from views.compare import page_compare
from views.watchlist import page_watchlist
from views.trending import page_trending
from views.beginner import page_beginner
from views.pro import page_pro
from views.login import page_login


# ── SESSION STATE ──
def init_session():
    defaults = {
        "logged_in": False, "user_email": "", "user_name": "Guest",
        "page": "home", "prev_page": "home", "beginner_step": 1, "bq": {},
        "search_ticker": "", "compare_tickers": [], "loading": False,
        "app_loaded": False, "use_quick50": True,
        "watchlist": [], "nav_counter": 0,
        "market_mode": "🇮🇳 India",
        "_currency": "₹",
        "last_search": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if CookieController is not None and "cookie_controller" not in st.session_state:
        st.session_state.cookie_controller = CookieController()
    
    if "cookie_controller" in st.session_state and not st.session_state.logged_in:
        c = st.session_state.cookie_controller
        if c is not None:
            saved_email = c.get("ss_email")
            saved_name = c.get("ss_name")
            if saved_email and saved_name:
                st.session_state.logged_in = True
                st.session_state.user_email = saved_email
                st.session_state.user_name = saved_name


init_session()

# ── DEEP LINKING (FIX 10) ──
query_params = st.query_params
if "ticker" in query_params and not st.session_state.get("_deep_link_handled"):
    st.session_state.search_ticker = query_params["ticker"]
    st.session_state.page = "search"
    st.session_state._deep_link_handled = True

inject_css()

# ═══════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════
def main():
    render_loading()
    render_ticker_bar()
    render_navbar()
    
    page = st.session_state.page
    if page == "login": page_login()
    elif page == "home": page_home()
    elif page == "beginner": page_beginner()
    elif page == "pro": page_pro()
    elif page == "trending": page_trending()
    elif page == "search": page_search()
    elif page == "compare": page_compare()
    elif page == "watchlist": page_watchlist()
    else: page_home()
    
    st.markdown(f"""<div class="watermark">
      StockSense AI v4.0 · India & US Markets · Built with ❤️ using Python & Streamlit · Live data via yfinance ·
      <span style="color:#EB5B3C">⚠️ Not SEBI/SEC registered. Not financial advice.</span></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
