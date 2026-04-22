import streamlit as st
from data_service import load_ticker_list
from views.stock_detail import render_stock_detail

def page_search():
    st.markdown('<div class="section-title">🔍 Stock Analysis</div>', unsafe_allow_html=True)
    market = st.session_state.get("market_mode", "🇮🇳 India")
    ticker_data = load_ticker_list(market)
    stock_map = {t["name"]: t["ticker"] for t in ticker_data} if ticker_data else {}
    stock_names = [""] + sorted(stock_map.keys())
    
    selected_name = st.selectbox(f"Search {'500 Indian' if market == '🇮🇳 India' else '300 US'} stocks by name", stock_names, key="search_sel",
                                  help="Pick a stock or type a custom ticker below")
    pre = st.session_state.get("search_ticker","")
    ticker_input = st.text_input("Or enter ticker manually", value=pre,
        placeholder="NSE: RELIANCE.NS | BSE: 500325.BO | US: AAPL", key="search_input")

    if st.button("🔍 Analyse",key="search_go",use_container_width=True):
        if selected_name and selected_name in stock_map:
            ticker = stock_map[selected_name]
        elif ticker_input.strip():
            ticker = ticker_input.strip().upper()
        else:
            st.error("Please select a stock or enter a ticker.")
            return
            
        st.session_state.search_ticker = ticker
        st.session_state.last_search = selected_name
        try:
            render_stock_detail(ticker, show_news=True, show_back=False)
        except Exception:
            st.warning("⚠️ Data unavailable for this stock. Please try another.")
    elif pre:
        try:
            render_stock_detail(pre, show_news=True, show_back=False)
        except Exception:
            st.warning("⚠️ Data unavailable for this stock. Please try another.")
