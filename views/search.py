import streamlit as st
from views.stock_detail import render_stock_detail

def page_search():
    ticker = st.session_state.get("search_ticker", "").strip()
    if ticker:
        try:
            render_stock_detail(ticker, show_news=True, show_back=False)
        except Exception:
            st.warning("Data unavailable for this stock. Please try another.")
    else:
        market = st.session_state.get("market_mode", "India")
        is_in = "India" in market
        m_name = "Indian" if is_in else "US"
        st.markdown(f"""
        <div class="ss-card" style="text-align:center;padding:40px 20px;margin-top:20px">
          <div style="font-size:1.3rem;font-weight:700;color:#FAFAFA;margin-bottom:8px">Search Any Stock</div>
          <div style="color:#9E9E9E;font-size:0.9rem;max-width:500px;margin:0 auto">
            Use the search bar at the top of the page to look up any {m_name} stock by company name or ticker symbol.
          </div>
        </div>
        """, unsafe_allow_html=True)

