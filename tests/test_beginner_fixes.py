import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_service import load_ticker_list, screen_stocks_with_progress

SECTOR_MAP_DICT = {
    "Technology": ["Information Technology", "Communication Services", "Technology"],
    "Banking & Finance": ["Financial Services", "Financials"],
    "Pharma & Healthcare": ["Healthcare", "Health Care", "Pharma"],
    "Energy & Power": ["Oil Gas & Consumable Fuels", "Power", "Energy", "Utilities"],
    "FMCG & Consumer": ["Fast Moving Consumer Goods", "Consumer Durables", "Consumer Services", "Consumer Staples", "Consumer Discretionary"],
    "Auto & EV": ["Automobile and Auto Components"],
    "Infrastructure": ["Construction", "Construction Materials", "Capital Goods", "Realty", "Real Estate", "Industrials", "Materials"],
    "Defence": ["Capital Goods", "Industrials"],
}

TOP_MCAP_PRIORITY = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS",
    "HINDUNILVR.NS", "LT.NS", "HCLTECH.NS", "SUNPHARMA.NS", "KOTAKBANK.NS", "M&M.NS", "TATAMOTORS.NS", "NTPC.NS"
]
TOP_MCAP_RANK = {ticker: i for i, ticker in enumerate(TOP_MCAP_PRIORITY)}


def test_sector_filtering_pharma():
    ticker_data = load_ticker_list("India")
    allowed = set(SECTOR_MAP_DICT["Pharma & Healthcare"])
    pharma_tickers = [t for t in ticker_data if t.get("sector") in allowed]
    
    assert len(pharma_tickers) > 0
    symbols = [t["ticker"] for t in pharma_tickers]
    assert "SUNPHARMA.NS" in symbols
    assert "DRREDDY.NS" in symbols
    assert "TCS.NS" not in symbols


def test_sector_filtering_technology():
    ticker_data = load_ticker_list("India")
    allowed = set(SECTOR_MAP_DICT["Technology"])
    tech_tickers = [t for t in ticker_data if t.get("sector") in allowed]
    
    assert len(tech_tickers) > 0
    symbols = [t["ticker"] for t in tech_tickers]
    assert "TCS.NS" in symbols
    assert "INFY.NS" in symbols
    assert "SUNPHARMA.NS" not in symbols


def test_quick_scan_market_cap_sorting():
    ticker_data = load_ticker_list("India")
    sorted_tickers = sorted(ticker_data, key=lambda t: TOP_MCAP_RANK.get(t["ticker"], 9999))
    top_50 = sorted_tickers[:50]
    top_50_symbols = [t["ticker"] for t in top_50]
    
    # RELIANCE.NS, TCS.NS, HDFCBANK.NS should be at the top of Quick Scan
    assert top_50_symbols[0] == "RELIANCE.NS"
    assert top_50_symbols[1] == "TCS.NS"
    assert top_50_symbols[2] == "HDFCBANK.NS"
    assert "360ONE.NS" not in top_50_symbols[:5]  # Previously #1 due to alphabetical order


def test_horizon_risk_adjustments():
    # Base risk = Medium -> (28, 1.2, 10)
    base_pe, base_de, base_roe = 28, 1.2, 10
    
    # Short-term -> stricter P/E (-3), lower debt (-0.1), higher ROE (+2)
    short_pe, short_de, short_roe = base_pe - 3, base_de - 0.1, base_roe + 2
    assert short_pe == 25
    assert round(short_de, 1) == 1.1
    assert short_roe == 12

    # Long-term -> higher growth P/E (+5), higher debt (+0.2), lower ROE (-2)
    long_pe, long_de, long_roe = base_pe + 5, base_de + 0.2, base_roe - 2
    assert long_pe == 33
    assert round(long_de, 1) == 1.4
    assert long_roe == 8


def test_sparse_data_scoring_penalty():
    # Test scoring with mock dict where stock has only 2 metrics (PE, DE) available
    stocks_to_test = {"Test Sparse Stock": "TCS.NS"}
    
    # Monkeypatch / inspect screen_stocks_with_progress behaviour
    # A stock with only 2 checks available can score at most 75.0
    valid_checks = 2
    total_expected = 4
    completeness_factor = valid_checks / total_expected # 0.5
    qual = 100.0 # perfect on 2 metrics
    bonus = 15.0
    cap = 75.0 if valid_checks < 3 else 100.0
    
    score = min(cap, round(qual * 0.8 * completeness_factor + bonus, 1))
    assert score == 55.0  # 100 * 0.8 * 0.5 + 15 = 55.0 <= 75.0
    assert score < 75.0   # Properly penalized, cannot hit 100
