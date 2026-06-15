#!/usr/bin/env python3
"""Build-time tool: fetch real public daily close data from the TWSE open API.

Source: Taiwan Stock Exchange (臺灣證券交易所) STOCK_DAY endpoint — official,
public market data. Output is a fixed CSV committed under assets/tw/csvs/ so the
benchmark is fully deterministic and tests never hit the network.

This script is run ONCE by a maintainer to (re)build the fixture; the benchmark
itself does NOT call it. ROC dates (民國年) are converted to YYYY-MM-DD.

Usage:
  python scripts/fetch_twse_stock.py --stock 2330 --year 2024 \
      --out assets/tw/csvs/tw_stock_2330_2024.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from urllib import request

API = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date={ym}01&stockNo={stock}"


def fetch_month(stock: str, year: int, month: int) -> list[tuple[str, float]]:
    url = API.format(ym=f"{year}{month:02d}", stock=stock)
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("big5", errors="replace")
    rows: list[tuple[str, float]] = []
    for line in csv.reader(raw.splitlines()):
        if not line or len(line) < 7:
            continue
        d = line[0].strip().strip('"')
        # data rows look like 113/01/02
        if "/" not in d:
            continue
        parts = d.split("/")
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        roc_y, mm, dd = parts
        iso = f"{int(roc_y) + 1911}-{int(mm):02d}-{int(dd):02d}"
        close_raw = line[6].strip().strip('"').replace(",", "")
        try:
            close = float(close_raw)
        except ValueError:
            continue
        rows.append((iso, close))
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Fetch TWSE daily close into a fixed CSV.")
    p.add_argument("--stock", default="2330")
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--sleep", type=float, default=1.5)
    args = p.parse_args(argv)

    all_rows: list[tuple[str, float]] = []
    for month in range(1, 13):
        try:
            rows = fetch_month(args.stock, args.year, month)
        except Exception as exc:  # noqa: BLE001
            print(f"month {month}: ERROR {exc}", file=sys.stderr)
            rows = []
        print(f"{args.year}-{month:02d}: {len(rows)} rows")
        all_rows.extend(rows)
        time.sleep(args.sleep)

    all_rows.sort(key=lambda r: r[0])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        for d, c in all_rows:
            w.writerow([d, f"{c:.2f}"])
    print(f"wrote {len(all_rows)} trading days -> {args.out}")
    return 0 if all_rows else 1


if __name__ == "__main__":
    sys.exit(main())
