import yfinance as yf
import pandas as pd
from typing import Optional

class DataCollector:
    """Professional Data Collection Engine for Alpha Radar."""
    
    @staticmethod
    def fetch_market_data(ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical data from Yahoo Finance."""
        print(f"[Collector] Fetching {ticker}...")
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(period=period, interval=interval)
            
            if df.empty:
                return None
                
            df.reset_index(inplace=True)
            df.rename(columns={
                "Date": "timestamp", 
                "Datetime": "timestamp", 
                "Open": "open", 
                "High": "high", 
                "Low": "low", 
                "Close": "close", 
                "Volume": "volume"
            }, inplace=True)
            
            return df[["timestamp", "open", "high", "low", "close", "volume"]]
        except Exception as e:
            print(f"[Error] Failed to fetch {ticker}: {e}")
            return None
