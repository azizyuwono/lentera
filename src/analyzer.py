import pandas as pd
import numpy as np


class IndicatorEngine:
    """Technical Analysis Engine — computes indicators and generates trade signals."""

    # ── Full indicator set ──────────────────────────────────────────────

    @staticmethod
    def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Apply all indicators to DataFrame. Returns copy with new columns."""
        df = df.copy()

        # EMA (existing)
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

        # SMA — longer-term trend filters
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean()

        # RSI (existing, kept identical)
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Bollinger Bands (existing)
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

        # MACD (12, 26, 9)
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # ATR (14)
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(14).mean()

        # Daily % change
        df['pct_change'] = df['close'].pct_change() * 100

        return df

    # ── Signal generation ───────────────────────────────────────────────

    @staticmethod
    def generate_signal(df: pd.DataFrame, label: str) -> dict:
        """Multi-factor signal: combines RSI, MACD, EMA trend, Bollinger, volume."""
        if len(df) < 50:
            raise ValueError("Not enough data to generate signals")

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest

        score = 0
        reasons = []

        # 1) EMA trend
        uptrend = latest['ema_9'] > latest['ema_21']
        score += 1 if uptrend else -1
        reasons.append(f"EMA{'↑' if uptrend else '↓'}")

        # 2) SMA alignment — bull when price > sma_50 > sma_200
        if not pd.isna(latest['sma_50']) and not pd.isna(latest['sma_200']):
            sma_bullish = (
                latest['close'] > latest['sma_50'] > latest['sma_200']
            )
            sma_bearish = (
                latest['close'] < latest['sma_50'] < latest['sma_200']
            )
            if sma_bullish:
                score += 1
                reasons.append("SMA50>200↑")
            elif sma_bearish:
                score -= 1
                reasons.append("SMA50<200↓")

        # 3) RSI
        if latest['rsi'] < 35:
            score += 1
            reasons.append(f"RSI{latest['rsi']:.0f}★")    # oversold tailwind
        elif latest['rsi'] > 65:
            score -= 1
            reasons.append(f"RSI{latest['rsi']:.0f}⚠")    # overbought headwind

        # 4) MACD crossover signal
        macd_bullish = (
            latest['macd'] > latest['macd_signal']
            and prev['macd'] <= prev['macd_signal']
        )
        macd_bearish = (
            latest['macd'] < latest['macd_signal']
            and prev['macd'] >= prev['macd_signal']
        )
        if macd_bullish:
            score += 1
            reasons.append("MACD↑")
        elif macd_bearish:
            score -= 1
            reasons.append("MACD↓")

        # 5) Bollinger position
        if latest['close'] <= latest['bb_lower']:
            score += 1
            reasons.append("BB低")
        elif latest['close'] >= latest['bb_upper']:
            score -= 1
            reasons.append("BB高")

        # Score to action
        if score >= 2:
            action = "BUY"
        elif score <= -2:
            action = "SELL"
        else:
            action = "HOLD"

        # Volatility tier
        atr_pct = (latest['atr'] / latest['close'] * 100) if latest['atr'] else 0
        if atr_pct < 1:
            vol_tier = "Low"
        elif atr_pct < 3:
            vol_tier = "Normal"
        else:
            vol_tier = "High"

        # Trend description
        if uptrend:
            trend_label = "Bullish"
        else:
            trend_label = "Bearish"

        return {
            "asset": label,
            "action": action,
            "price": round(latest['close'], 2),
            "pct_change": round(latest.get('pct_change', 0), 2),
            "rsi": round(latest['rsi'], 1),
            "trend": trend_label,
            "macd_signal": "Bullish" if latest['macd'] > latest['macd_signal'] else "Bearish",
            "atr_pct": round(atr_pct, 2),
            "volatility": vol_tier,
            "score": score,
            "reasons": ", ".join(reasons),
        }
