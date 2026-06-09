# lentera

A daily market intelligence pipeline. Fetches market data, processes technical indicators, and stores everything as version-controlled Parquet files.

This repository is fully automated and designed to be read by both humans and machines.

---

## How It Works

1. A scheduled GitHub Actions workflow runs daily at 01:00 UTC (08:00 WIB).
2. `DataCollector` fetches OHLCV data from Yahoo Finance for Gold (XAU/USD), Bitcoin, and Ethereum.
3. `IndicatorEngine` computes RSI (14), EMA (9/21), Bollinger Bands, and generates a trading signal.
4. `ReportGenerator` writes the live signal table below and commits the updated README back to the repository.

## Live Signals

*Updated: {timestamp}*

| Asset | Price | Signal | RSI | Trend |
|-------|-------|--------|-----|-------|
{signal_rows}

*This table is regenerated on every pipeline run.*

## Project Structure

```
src/
├── collector.py         # Data ingestion layer
├── analyzer.py          # Technical indicator engine
├── report_generator.py  # Renders README and exports signals
└── main.py              # Entry point

tests/
└── test_analyzer.py     # Unit tests for indicator logic

data/                    # Historical data (Parquet format)
.github/workflows/       # CI/CD definitions
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

Lentera was built to solve a simple problem: I wanted a clean, accessible record of daily market signals that I could query programmatically without relying on any always-on server. By storing data as Parquet inside the repository itself, every run adds to a growing time series that anyone can clone and use.

---

*Maintained by [Moli](https://t.me/davevy).*
