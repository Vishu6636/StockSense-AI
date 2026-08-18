import pytest
import pandas as pd
from data_service import (
    calculate_sip_lumpsum,
    get_sector_heatmap_data,
    get_eli5_explanation,
    get_insider_ownership_analysis,
    get_sector_peers_cached,
    analyze_portfolio_holdings
)

def test_calculate_sip_lumpsum():
    res = calculate_sip_lumpsum(monthly_investment=5000, lumpsum=10000, annual_return_pct=12.0, tenure_years=5, inflation_pct=6.0)
    assert "summary" in res
    assert "df" in res
    
    summary = res["summary"]
    assert summary["total_invested"] > 0
    assert summary["final_wealth"] > summary["total_invested"]
    assert summary["total_gain"] > 0
    assert summary["wealth_multiplier"] >= 1.0
    
    df = res["df"]
    assert len(df) == 5
    assert list(df.columns) == ["Year", "Total Invested", "Estimated Wealth", "Wealth Gain", "Inflation Adjusted"]

def test_get_eli5_explanation():
    pe_info = get_eli5_explanation("P/E", 15)
    assert pe_info["title"] == "Price to Earnings Ratio"
    assert "Bargain" in pe_info["status"] or "Undervalued" in pe_info["status"]
    
    de_info = get_eli5_explanation("D/E", 0.2)
    assert "Low Debt" in de_info["status"]
    
    roe_info = get_eli5_explanation("ROE", 22)
    assert "High Capital Efficiency" in roe_info["status"]
    
    unknown = get_eli5_explanation("UNKNOWN_METRIC", 100)
    assert unknown["title"] == "UNKNOWN_METRIC"

def test_get_insider_ownership_analysis():
    mock_info = {
        "heldPercentInsiders": 0.65,
        "heldPercentInstitutions": 0.20
    }
    res = get_insider_ownership_analysis("RELIANCE.NS", mock_info)
    assert res["promoter_pct"] == 65.0
    assert res["inst_pct"] == 20.0
    assert res["public_pct"] == 15.0
    assert res["confidence_score"] > 70
    assert "High Promoter Skin in Game" in res["rating"]

def test_get_sector_peers_cached():
    peers = get_sector_peers_cached("TCS.NS", "🇮🇳 India")
    assert isinstance(peers, list)
    if peers:
        assert len(peers) <= 3
        assert any(p["ticker"] != "TCS.NS" for p in peers)

def test_analyze_portfolio_holdings():
    sample_holdings = [
        {"ticker": "TCS.NS", "shares": 10, "buy_price": 3000.0},
        {"ticker": "INFY.NS", "shares": 15, "buy_price": 1400.0}
    ]
    res = analyze_portfolio_holdings(sample_holdings, "🇮🇳 India")
    assert not res.get("empty")
    assert res["total_invested"] == (10 * 3000.0 + 15 * 1400.0)
    assert res["num_stocks"] == 2
    assert "health_status" in res
    assert len(res["stocks"]) == 2
    assert len(res["sectors"]) >= 1

def test_analyze_empty_portfolio():
    res = analyze_portfolio_holdings([], "🇮🇳 India")
    assert res.get("empty") is True
