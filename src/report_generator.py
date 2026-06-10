import json
import os
from datetime import datetime
from typing import List, Dict

from src.collector import DataCollector
from src.analyzer import IndicatorEngine

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


class ReportGenerator:
    """Generate market intelligence reports and sync to README."""

    ASSETS = [
        ("GC=F", "XAU/USD"),
        ("BTC-USD", "BTC/USD"),
        ("ETH-USD", "ETH/USD"),
    ]

    @staticmethod
    def run_full_pipeline() -> List[Dict]:
        """Orchestrate data collection, analysis, and reporting."""
        results = []

        for ticker, label in ReportGenerator.ASSETS:
            df = DataCollector.fetch_market_data(ticker)
            if df is None:
                print(f"[WARNING] No data for {label}")
                continue

            df_with_ind = IndicatorEngine.apply_indicators(df)
            signal = IndicatorEngine.generate_signal(df_with_ind, label)
            results.append(signal)

            fname = f"{ticker.replace('-', '_').lower()}.parquet"
            filepath = os.path.join(DATA_DIR, fname)
            df_with_ind.to_parquet(filepath, index=False)

        signals_path = os.path.join(DATA_DIR, "signals.json")
        with open(signals_path, "w") as f:
            json.dump(results, f, indent=2)

        return results

    @staticmethod
    def generate_readme(signals: List[Dict]) -> str:
        """Render README.md with live market data."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M UTC+7")

        signal_rows = ""
        for s in signals:
            emoji = "🟢" if s['action'] == "BUY" else ("🔴" if s['action'] == "SELL" else "⚪")
            chg_sign = "+" if s['pct_change'] > 0 else ""
            chg_str = f"({chg_sign}{s['pct_change']}%)"
            macd_emoji = "📈" if s['macd_signal'] == "Bullish" else "📉"

            signal_rows += (
                f" {s['asset']} | ${s['price']:,.2f} {chg_str} | {emoji} **{s['action']}** "
                f"| {s['rsi']} | {s['trend']} | {macd_emoji} {s['macd_signal']} "
                f"| {s['volatility']} ({s['atr_pct']}%) | `{s['reasons']}` |\n"
            )

        return f"""# lentera

A daily market intelligence pipeline. Fetches market data, processes technical indicators, and stores everything as version-controlled Parquet files.

---

## How It Works

1. A scheduled GitHub Actions workflow runs daily at 01:00 UTC (08:00 WIB).
2. `DataCollector` fetches OHLCV data from Yahoo Finance for Gold (XAU/USD), Bitcoin, and Ethereum.
3. `IndicatorEngine` computes:
   - **Trend**: EMA (9/21) & SMA (50/200) crossover/alignment.
   - **Momentum**: RSI (14) & MACD (12, 26, 9) crossovers.
   - **Volatility**: Bollinger Bands & ATR-based volatility profiling.
4. `ReportGenerator` writes the live signal table below and commits the updated README back to the repository.

## Live Signals

*Updated: {now}*

| Asset | Price | Signal | RSI | Trend | MACD | Volatility (ATR) | Factors |
|-------|-------|--------|-----|-------|------|------------------|---------|
|{signal_rows}

*This table is regenerated on every pipeline run.*

## Project Structure

```
src/
├── collector.py         # Data ingestion layer
├── analyzer.py          # Technical indicator engine
├── report_generator.py  # Renders README and exports signals
└── main.py              # Entry point

tests/
└── test_analyzer.py     # Unit tests
```

## Local Development

```bash
git clone git@github.com:azizyuwono/lentera.git
cd lentera
pip install -r requirements.txt
python -m pytest tests/
python -m src.main
```

## Motivation

Lentera was built to solve a simple problem: having a clean, accessible record of daily market signals that can be queried programmatically without relying on any always-on server. By storing data as Parquet inside the repository itself, every run contributes to a growing time series.

---

*Maintained by [Moli](https://t.me/davevy).*
"""


if __name__ == "__main__":
    signals = ReportGenerator.run_full_pipeline()
    readme = ReportGenerator.generate_readme(signals)

    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "w") as f:
        f.write(readme)

    print("Done. README synced.")
