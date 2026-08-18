import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_service import analyze_portfolio_holdings, load_ticker_list
from ui_components import metric_chip, render_metric_row, render_badge, apply_theme, render_sebi_disclaimer

SAMPLE_INDIA_PORTFOLIO = """Ticker, Shares, Buy Price
RELIANCE.NS, 15, 2750.00
TCS.NS, 20, 3400.00
HDFCBANK.NS, 30, 1550.00
INFY.NS, 25, 1420.00
TATAMOTORS.NS, 50, 620.00"""

SAMPLE_US_PORTFOLIO = """Ticker, Shares, Buy Price
AAPL, 10, 175.00
MSFT, 8, 380.00
GOOGL, 12, 140.00
NVDA, 5, 450.00
AMZN, 15, 130.00"""

def page_portfolio():
    market = st.session_state.get("market_mode", "🇮🇳 India")
    currency = st.session_state.get("_currency", "₹")
    
    st.markdown('<div class="hero-title">💼 Portfolio Import & Health Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Upload or paste your stock holdings to get instant portfolio-level P/E, sector concentration, and risk rating.</div>', unsafe_allow_html=True)
    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    
    sample_text = SAMPLE_INDIA_PORTFOLIO if "India" in market else SAMPLE_US_PORTFOLIO
    
    c_input, c_results = st.columns([1, 2])
    
    with c_input:
        st.markdown('<div class="section-title">📥 Import Holdings</div>', unsafe_allow_html=True)
        st.caption("Paste holding data in CSV format (`Ticker, Shares, Buy Price`):")
        
        raw_csv = st.text_area(
            "Portfolio CSV",
            value=st.session_state.get("portfolio_csv_input", sample_text),
            height=200,
            key="portfolio_csv_text_area",
            label_visibility="collapsed"
        )
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("📊 Analyze Portfolio", type="primary", use_container_width=True, key="btn_analyze_portfolio"):
                st.session_state.portfolio_csv_input = raw_csv
                st.rerun()
        with btn_c2:
            if st.button("🔄 Reset Sample", type="secondary", use_container_width=True, key="btn_reset_sample"):
                st.session_state.portfolio_csv_input = sample_text
                st.rerun()
                
    # Parse input
    holdings_list = []
    lines = raw_csv.strip().split("\n")
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3 and parts[0].lower() != "ticker":
            try:
                sym = parts[0].upper()
                sh = float(parts[1])
                bp = float(parts[2])
                holdings_list.append({"ticker": sym, "shares": sh, "buy_price": bp})
            except ValueError:
                continue
                
    with c_results:
        if not holdings_list:
            st.info("👈 Paste your stock holdings or click 'Analyze Portfolio' to view your report.")
            return
            
        with st.spinner("Analyzing portfolio holdings and fetching live valuation..."):
            res = analyze_portfolio_holdings(holdings_list, market)
            
        if res.get("empty"):
            st.error("No valid stock tickers found in input. Please check the CSV format.")
            return
            
        st.markdown('<div class="section-title">📈 Portfolio Health Dashboard</div>', unsafe_allow_html=True)
        
        pnl_color = "green" if res["total_pnl"] >= 0 else "red"
        pnl_arrow = "▲" if res["total_pnl"] >= 0 else "▼"
        
        chips = [
            metric_chip("Total Invested", f"{currency}{res['total_invested']:,.2f}"),
            metric_chip("Current Value", f"{currency}{res['total_current_val']:,.2f}", "blue"),
            metric_chip("Total P&L", f"{currency}{res['total_pnl']:,.2f} ({pnl_arrow}{abs(res['total_pnl_pct']):.2f}%)", pnl_color),
            metric_chip("Weighted P/E", str(res['portfolio_pe']), "gold"),
            metric_chip("Holdings", f"{res['num_stocks']} Stocks", "gray")
        ]
        render_metric_row(chips)
        
        # Risk Rating Banner
        risk_color = "green" if "Low Risk" in res["risk_rating"] else ("gold" if "Moderate" in res["risk_rating"] else "red")
        st.markdown(f"""
        <div class="rec-banner {risk_color}" style="margin:12px 0">
          <div class="rec-icon">🛡️</div>
          <div>
            <div class="rec-label {risk_color}">{res['health_status']}</div>
            <div class="rec-reason">
              Top sector accounts for <strong>{res['max_sector_share']}%</strong> of total capital across <strong>{res['num_sectors']}</strong> sectors.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Charts section
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            # Sector Pie Chart
            sec_df = pd.DataFrame(res["sectors"])
            fig_sec = go.Figure(data=[go.Pie(
                labels=sec_df["Sector"],
                values=sec_df["Value"],
                hole=0.45
            )])
            apply_theme(fig_sec, height=260, title="Sector Concentration")
            st.plotly_chart(fig_sec, use_container_width=True)
            
        with col_c2:
            # Holdings Bar Chart
            stocks_df = pd.DataFrame(res["stocks"])
            fig_bar = go.Figure(go.Bar(
                x=stocks_df["ticker"],
                y=stocks_df["current_value"],
                marker_color=["#00D09C" if p >= 0 else "#EB5B3C" for p in stocks_df["pnl"]],
                text=[f"{currency}{v:,.0f}" for v in stocks_df["current_value"]],
                textposition="auto"
            ))
            apply_theme(fig_bar, height=260, title="Allocation per Stock")
            st.plotly_chart(fig_bar, use_container_width=True)
            
    # Holdings Detail Table
    st.markdown('<div class="section-title">📄 Holdings Breakdown Table</div>', unsafe_allow_html=True)
    df_display = pd.DataFrame(res["stocks"])
    df_display = df_display.rename(columns={
        "ticker": "Ticker", "name": "Company", "shares": "Shares",
        "buy_price": f"Avg Buy ({currency})", "current_price": f"Current ({currency})",
        "invested": f"Invested ({currency})", "current_value": f"Current Val ({currency})",
        "pnl": f"P&L ({currency})", "pnl_pct": "P&L %", "sector": "Sector", "pe": "P/E"
    })
    # Format missing P/E or NaN values safely for PyArrow display
    if "P/E" in df_display.columns:
        df_display["P/E"] = df_display["P/E"].apply(lambda x: "—" if (pd.isna(x) or x is None or x == "N/A") else f"{float(x):.1f}")
    st.dataframe(df_display, use_container_width=True)
    st.markdown('<hr class="ss-sep"/>', unsafe_allow_html=True)
    render_sebi_disclaimer()
