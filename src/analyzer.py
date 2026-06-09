import pandas as pd

class IndicatorEngine:
    """Technical Analysis Engine mapping market data to actionable signals."""
    
    @staticmethod
    def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Apply EMA, RSI, and Bollinger Bands to DataFrame."""
        df = df.copy()
        
        # EMA
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        
        return df

    @staticmethod
    def generate_signal(df: pd.DataFrame, label: str) -> dict:
        """Parse applied indicators to generate deterministic trading signals."""
        if len(df) < 50:
            raise ValueError("Not enough data to generate signals")
            
        latest = df.iloc[-1]
        
        # Scoring logic
        score = 0
        uptrend = latest['ema_9'] > latest['ema_21']
        rsi_buy = latest['rsi'] < 35
        rsi_sell = latest['rsi'] > 65
        
        if uptrend and rsi_buy:
            score += 2
        elif not uptrend and rsi_sell:
            score -= 2
            
        if score >= 2:
            action = "BUY"
        elif score <= -2:
            action = "SELL"
        else:
            action = "HOLD"
            
        return {
            "asset": label,
            "action": action,
            "price": round(latest['close'], 2),
            "rsi": round(latest['rsi'], 1),
            "trend": "Bullish" if uptrend else "Bearish"
        }
