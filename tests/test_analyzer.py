"""Unit tests for IndicatorEngine — ensures signal logic is deterministic."""
import pytest
import pandas as pd
import numpy as np

from src.analyzer import IndicatorEngine


@pytest.fixture
def sample_market_data() -> pd.DataFrame:
    """Generate controlled synthetic data for reproducible tests.
    Needs at least 200 points for SMA_200.
    """
    np.random.seed(42)
    n = 250
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

    def test_apply_indicators_schema(self, sample_market_data: pd.DataFrame):
        """Should return original columns plus all new indicator columns."""
        result = IndicatorEngine.apply_indicators(sample_market_data)
        expected_cols = {
            "open", "high", "low", "close", "volume",
            "ema_9", "ema_21", "sma_50", "sma_200",
            "rsi", "macd", "macd_signal", "atr", "pct_change"
        }
        assert expected_cols.issubset(result.columns), f"Missing columns: {expected_cols - set(result.columns)}"
        assert len(result) == len(sample_market_data)

    def test_apply_indicators_integrity(self, sample_market_data: pd.DataFrame):
        """Indicator values must be within expected numerical bounds."""
        result = IndicatorEngine.apply_indicators(sample_market_data)
        last = result.iloc[-1]
        
        # Numerical sanity
        assert 0 <= last["rsi"] <= 100
        assert not pd.isna(last["sma_200"]), "SMA 200 should be computed for 250 rows"
        assert last["atr"] > 0, "ATR should be positive"
        assert isinstance(last["pct_change"], (float, np.float64))

    def test_generate_signal_schema(self, sample_market_data: pd.DataFrame):
        """Signal dict must contain all keys required by report generator."""
        enriched = IndicatorEngine.apply_indicators(sample_market_data)
        signal = IndicatorEngine.generate_signal(enriched, "TEST/USD")
        
        required_keys = {
            "asset", "action", "price", "pct_change", "rsi", 
            "trend", "macd_signal", "atr_pct", "volatility", "score", "reasons"
        }
        assert required_keys.issubset(signal.keys()), f"Missing signal keys: {required_keys - set(signal.keys())}"
        assert signal["action"] in ("BUY", "SELL", "HOLD")
        assert signal["volatility"] in ("Low", "Normal", "High")

    def test_not_enough_data_raises(self):
        """Should raise ValueError if dataframe is too short (< 50)."""
        df = pd.DataFrame({"close": [10.0] * 10})
        with pytest.raises(ValueError, match="Not enough data"):
            IndicatorEngine.generate_signal(df, "FAIL")
