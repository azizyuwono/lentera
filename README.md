# lentera

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

*Updated: 2026-06-10 17:23 UTC+7*

| Asset | Price | Signal | RSI | Trend | MACD | Volatility (ATR) | Factors |
|-------|-------|--------|-----|-------|------|------------------|---------|
| XAU/USD | $4,183.90 (-1.79%) | ⚪ **HOLD** | 25.1 | Bearish | 📉 Bearish | Normal (1.99%) | `EMA↓, RSI25★, BB低` |
 BTC/USD | $61,190.12 (-0.74%) | ⚪ **HOLD** | 14.8 | Bearish | 📉 Bearish | High (4.26%) | `EMA↓, SMA50<200↓, RSI15★` |
 ETH/USD | $1,620.68 (-1.04%) | ⚪ **HOLD** | 20.0 | Bearish | 📉 Bearish | High (5.74%) | `EMA↓, SMA50<200↓, RSI20★` |


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
