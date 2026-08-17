import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_service import (
    compute_technicals,
    generate_recommendation,
    get_analyst_consensus,
    search_tickers,
)


# ==========================================
# 1. TESTS FOR compute_technicals()
# ==========================================
class TestComputeTechnicals:

    def test_empty_or_short_dataframe_returns_empty_dict(self):
        assert compute_technicals(None) == {}
        assert compute_technicals(pd.DataFrame()) == {}

        # DataFrame with fewer than 30 rows
        dates = pd.date_range("2024-01-01", periods=25)
        df_short = pd.DataFrame(
            {"Close": np.linspace(100, 120, 25), "Volume": np.full(25, 1000)},
            index=dates,
        )
        assert compute_technicals(df_short) == {}

    def test_mathematical_correctness_on_synthetic_data(self):
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=60)
        # Synthetic price series with subtle variations
        prices = 100.0 + np.cumsum(np.random.randn(60) * 1.5)
        volumes = np.random.randint(1000, 5000, 60)
        df = pd.DataFrame({"Close": prices, "Volume": volumes}, index=dates)

        tech = compute_technicals(df)

        assert isinstance(tech, dict)
        assert "rsi" in tech
        assert "macd" in tech
        assert "signal" in tech
        assert "macd_hist" in tech
        assert "ma20" in tech
        assert "ma50" in tech
        assert "bb_upper" in tech
        assert "bb_lower" in tech

        # Mathematical Invariants Validation
        # 1. MACD Histogram = MACD - Signal
        macd_last = tech["macd"].iloc[-1]
        sig_last = tech["signal"].iloc[-1]
        hist_last = tech["macd_hist"].iloc[-1]
        assert np.isclose(hist_last, macd_last - sig_last)

        # 2. Bollinger Bands = MA20 ± 2 * Std20
        ma20_last = tech["ma20"].iloc[-1]
        std20_last = df["Close"].rolling(20).std().iloc[-1]
        bb_upper_expected = ma20_last + 2 * std20_last
        bb_lower_expected = ma20_last - 2 * std20_last

        assert np.isclose(tech["bb_upper"].iloc[-1], bb_upper_expected)
        assert np.isclose(tech["bb_lower"].iloc[-1], bb_lower_expected)

        # 3. Moving Average 20 and 50 check
        assert np.isclose(tech["ma20"].iloc[-1], df["Close"].tail(20).mean())
        assert np.isclose(tech["ma50"].iloc[-1], df["Close"].tail(50).mean())

        # 4. RSI Range check (0 to 100)
        rsi_valid = tech["rsi"].dropna()
        assert (rsi_valid >= 0).all() and (rsi_valid <= 100).all()


# ==========================================
# 2. TESTS FOR generate_recommendation()
# ==========================================
class TestGenerateRecommendation:

    def test_clear_buy_case(self):
        buy_info = {
            "trailingPE": 15,
            "returnOnEquity": 0.22,      # 22%
            "debtToEquity": 30,          # 0.30 after /100 conversion
            "revenueGrowth": 0.18,       # 18%
            "earningsGrowth": 0.25,      # 25%
            "heldPercentInsiders": 0.55, # 55%
            "dividendYield": 0.025,      # 2.5%
            "profitMargins": 0.18,       # 18%
        }
        # Technicals with oversold RSI and bullish MACD crossover
        tech = {
            "rsi": pd.Series([30.0]),
            "macd": pd.Series([2.5]),
            "signal": pd.Series([1.0]),
        }

        verdict, verdict_cls, icon, reasons = generate_recommendation(buy_info, tech)

        assert verdict == "BUY"
        assert verdict_cls == "buy"
        assert icon == "🟢"
        assert len(reasons) > 0
        assert any("Low P/E" in r for r in reasons)
        assert any("RSI" in r for r in reasons)

    def test_clear_sell_case(self):
        sell_info = {
            "trailingPE": 55,
            "returnOnEquity": 0.02,       # 2%
            "debtToEquity": 250,          # 2.5 after /100 conversion
            "revenueGrowth": -0.10,       # -10%
            "earningsGrowth": -0.15,      # -15%
            "heldPercentInsiders": 0.10,  # 10%
            "dividendYield": 0.00,
            "profitMargins": 0.02,        # 2%
        }
        tech = {
            "rsi": pd.Series([75.0]),     # Overbought RSI
            "macd": pd.Series([1.0]),
            "signal": pd.Series([2.5]),   # Bearish MACD
        }

        verdict, verdict_cls, icon, reasons = generate_recommendation(sell_info, tech)

        assert verdict == "SELL"
        assert verdict_cls == "sell"
        assert icon == "🔴"
        assert any("High P/E" in r for r in reasons)
        assert any("High debt" in r for r in reasons)

    def test_hold_case(self):
        hold_info = {
            "trailingPE": 25,
            "returnOnEquity": 0.12,       # 12%
            "debtToEquity": 80,           # 0.8
            "revenueGrowth": 0.05,        # 5%
            "earningsGrowth": 0.08,       # 8%
            "heldPercentInsiders": 0.30,  # 30%
            "dividendYield": 0.01,        # 1%
            "profitMargins": 0.08,        # 8%
        }

        verdict, verdict_cls, icon, reasons = generate_recommendation(hold_info, {})

        assert verdict == "HOLD"
        assert verdict_cls == "hold"
        assert icon == "🟡"

    def test_empty_or_malformed_info(self):
        # Empty dict should execute cleanly without exceptions
        verdict, verdict_cls, icon, reasons = generate_recommendation({}, {})
        assert verdict in ["BUY", "HOLD", "SELL"]
        assert isinstance(reasons, list)


# ==========================================
# 3. TESTS FOR get_analyst_consensus()
# ==========================================
class TestGetAnalystConsensus:

    def test_malformed_or_empty_inputs_return_none(self):
        assert get_analyst_consensus(None) is None
        assert get_analyst_consensus(pd.DataFrame()) is None
        assert get_analyst_consensus("invalid_string") is None
        assert get_analyst_consensus(12345) is None
        assert get_analyst_consensus([]) is None

    def test_dataframe_without_period_column_returns_none(self):
        df_no_period = pd.DataFrame({"strongBuy": [10], "buy": [5]})
        assert get_analyst_consensus(df_no_period) is None

    def test_zero_total_consensus_returns_none(self):
        df_zero = pd.DataFrame(
            [{
                "period": "0m",
                "strongBuy": 0,
                "buy": 0,
                "hold": 0,
                "sell": 0,
                "strongSell": 0,
            }]
        )
        assert get_analyst_consensus(df_zero) is None

    def test_valid_analyst_recommendations(self):
        df_valid = pd.DataFrame(
            [{
                "period": "0m",
                "strongBuy": 10,
                "buy": 8,
                "hold": 4,
                "sell": 1,
                "strongSell": 0,
            }]
        )

        res = get_analyst_consensus(df_valid)

        assert res is not None
        assert res["strongBuy"] == 10
        assert res["buy"] == 8
        assert res["hold"] == 4
        assert res["sell"] == 1
        assert res["strongSell"] == 0
        assert res["total"] == 23


# ==========================================
# 4. TESTS FOR search_tickers()
# ==========================================
class TestSearchTickers:

    def test_partial_match(self):
        results_in = search_tickers("rel", "🇮🇳 India")
        assert len(results_in) > 0
        assert any(t["ticker"] == "RELIANCE.NS" for t in results_in)

        results_us = search_tickers("aap", "🇺🇸 US")
        assert len(results_us) > 0
        assert any(t["ticker"] == "AAPL" for t in results_us)

    def test_case_insensitivity(self):
        res_lower = search_tickers("tcs", "🇮🇳 India")
        res_upper = search_tickers("TCS", "🇮🇳 India")
        res_mixed = search_tickers("Tcs", "🇮🇳 India")

        assert len(res_lower) > 0
        assert res_lower == res_upper == res_mixed
        assert any(t["ticker"] == "TCS.NS" for t in res_lower)

    def test_search_by_name(self):
        results = search_tickers("tata", "🇮🇳 India")
        assert len(results) > 0
        assert any("tata" in t["name"].lower() for t in results)

    def test_no_match_returns_empty_list(self):
        assert search_tickers("NONEXISTENT_TICKER_9999", "🇮🇳 India") == []
        assert search_tickers("NONEXISTENT_TICKER_9999", "🇺🇸 US") == []
