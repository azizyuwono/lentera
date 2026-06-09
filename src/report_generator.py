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
        ("GC=F", "XAU/USD (Gold)"),
        ("BTC-USD", "BTC/USD (Bitcoin)"),
        ("ETH-USD", "ETH/USD (Ethereum)"),
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
            
            # Save raw data as parquet
            fname = f"{ticker.replace('-', '_').lower()}.parquet"
            filepath = os.path.join(DATA_DIR, fname)
            df_with_ind.to_parquet(filepath, index=False)
        
        # Save signals as JSON
        signals_path = os.path.join(DATA_DIR, "signals.json")
        with open(signals_path, "w") as f:
            json.dump(results, f, indent=2)
        
        return results

    @staticmethod
    def generate_readme(signals: List[Dict]) -> str:
        """Render README.md with live market data and calm aesthetic."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M UTC+7")
        
        signal_rows = ""
        for s in signals:
            emoji = "🟢" if s['action'] == "BUY" else ("🔴" if s['action'] == "SELL" else "⚪")
            signal_rows += (
                f"| {s['asset']} | ${s['price']:,.2f} | {emoji} **{s['action']}** "
                f"| {s['rsi']} | {s['trend']} |\n"
            )
        
        return f"""# lentera

> Penerang harian di tengah pasar yang riuh.

Repo ini jalan sendiri setiap hari. Ia menarik data pasar (emas, bitcoin, ether), mengolahnya dengan beberapa indikator teknikal, lalu menyimpannya ke file Parquet.

Hasilnya, setiap pagi laporan harian muncul di sini — siapa saja boleh lihat, siapa saja boleh ambil datanya untuk dipelajari lebih lanjut.

## Bagaimana Ia Bekerja

1. GitHub Actions memicu pipeline setiap jam 08:00 WIB.
2. Script Python menarik data dari Yahoo Finance.
3. Data itu diperkaya dengan indikator seperti RSI, EMA, dan Bollinger Bands.
4. Laporan dibuat, tabel di bawah ini diperbarui, dan perubahan dikirim kembali ke repo ini.

## Sinyal Hari Ini

_Last updated: {now}_

| Asset | Harga | Sinyal | RSI (14) | Trend |
|-------|-------|--------|----------|-------|
{signal_rows}

> Tabel di atas selalu otomatis diperbarui setiap hari.

## Kalau Ingin Jalanin di Komputer Sendiri

```bash
git clone git@github.com:azizyuwono/lentera.git
cd lentera
pip install -r requirements.txt
python -m src.main
```

Semua data akan tersimpan di folder `data/` dengan format Parquet.

---

_dikelola oleh [Moli](https://t.me/davevy) — teman teknis di balik layar_
"""

if __name__ == "__main__":
    signals = ReportGenerator.run_full_pipeline()
    readme = ReportGenerator.generate_readme(signals)
    
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "w") as f:
        f.write(readme)
    
    print("[Done] README.md synced with live signals.")
