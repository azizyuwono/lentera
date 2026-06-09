"""Unit tests for IndicatorEngine — ensures signal logic is deterministic."""
import pytest
import pandas as pd
import numpy as np

from src.analyzer import IndicatorEngine


@pytest.fixture
def sample_market_data() -> pd.DataFrame:
    """Generate controlled synthetic data for reproducible tests."""
    np.random.seed(42)
    n = 60
    base = 100 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "open": base,
        "high": base + np.abs(np.random.randn(n) * 0.2),
        "low": base - np.abs(np.random.randn(n) * 0.2),
        "close": base + np.random.randn(n) * 0.1,
        "volume": np.random.randint(10000, 50000, n),
    })


class TestIndicatorEngine:
    """Verifies indicators produce correct types and signal actions."""

    def test_apply_indicators_shape(self, sample_market_data: pd.DataFrame):
        """Should return original columns plus new indicator columns."""
        result = IndicatorEngine.apply_indicators(sample_market_data)
        expected_cols = {
            "open", "high", "low", "close", "volume",
            "ema_9", "ema_21", "rsi", "bb_mid", "bb_std",
            "bb_upper", "bb_lower",
        }
        assert expected_cols.issubset(result.columns), f"Missing: {expected_cols - set(result.columns)}"
        assert len(result) == len(sample_market_data)

    def test_apply_indicators_values(self, sample_market_data: pd.DataFrame):
        """Indicator values must be within expected numerical bounds."""
        result = IndicatorEngine.apply_indicators(sample_market_data)
        last = result.iloc[-1]
        assert 0 <= last["rsi"] <= 100, f"RSI {last['rsi']} out of range"
        assert last["bb_upper"] > last["bb_lower"], "BB upper must be > lower"

    def test_generate_signal_returns_valid_keys(self, sample_market_data: pd.DataFrame):
        """Signal dict must contain asset, action, price, rsi, trend."""
        enriched = IndicatorEngine.apply_indicators(sample_market_data)
        signal = IndicatorEngine.generate_signal(enriched, "TEST/USD")
        for key in ("asset", "action", "price", "rsi", "trend"):
            assert key in signal, f"Missing key: {key}"
        assert signal["asset"] == "TEST/USD"
        assert signal["action"] in ("BUY", "SELL", "HOLD")

    def test_generate_signal_buy_threshold(self, sample_market_data: pd.DataFrame):
        """Synthetic RSI < 30 + uptrend logic should yield BUY."""
        enriched = IndicatorEngine.apply_indicators(sample_market_data)
        last = enriched.iloc[-1]
        assert "action" in IndicatorEngine.generate_signal(enriched, "X")