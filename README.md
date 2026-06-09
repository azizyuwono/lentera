# lentera

> Penerang harian di tengah pasar yang riuh.

Repo ini jalan sendiri setiap hari. Ia menarik data pasar (emas, bitcoin, ether), mengolahnya dengan beberapa indikator teknikal, lalu menyimpannya ke file Parquet.

Hasilnya, setiap pagi laporan harian muncul di sini — siapa saja boleh lihat, siapa saja boleh ambil datanya untuk dipelajari lebih lanjut.

## Bagaimana Ia Bekerja

1. GitHub Actions memicu pipeline setiap jam 08:00 WIB.
2. Script Python menarik data dari Yahoo Finance.
3. Data itu diperkaya dengan indikator seperti RSI, EMA, dan Bollinger Bands.
4. Laporan dibuat, tabel di bawah ini diperbarui, dan perubahan dikirim kembali ke repo ini.

## Sinyal Hari Ini

_Updated: {{ timestamp }}_

| Asset | Harga | Sinyal | RSI (14) | Trend |
|-------|-------|--------|----------|-------|
| XAU/USD | $4,309.80 | ⚪ HOLD | 33.5 | Downtrend |
| BTC/USD | $74,225.10 | ⚪ HOLD | 48.2 | Sideways |
| ETH/USD | $3,890.40 | 🟢 BUY | 28.7 | Uptrend |

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