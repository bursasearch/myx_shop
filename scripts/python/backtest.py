#!/usr/bin/env python3
import csv, json, sys
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 3:
        print("Usage: backtest.py <picks.json> <normalized_eod.csv>")
        sys.exit(1)

    picksfile = sys.argv[1]
    eodfile = sys.argv[2]
    outfile = "backtest_report.json"

    with open(picksfile, "r", encoding="utf-8") as f:
        picks = json.load(f)

    # Load latest EOD
    latest = {}
    with open(eodfile, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            latest[row["Code"]] = float(row.get("Last", 0))

    results = []
    basket_perf = 0
    count = 0
    for p in picks["picks"]:
        code = p["Code"]
        pick_price = float(p.get("Last", 0))
        current_price = latest.get(code, pick_price)
        perf_pct = ((current_price - pick_price) / pick_price * 100) if pick_price else 0
        results.append({"Code": code, "Stock": p["Stock"], "PerfPct": round(perf_pct, 2)})
        basket_perf += perf_pct
        count += 1

    basket_perf = basket_perf / count if count else 0

    report = {
        "snapshot_date": picks.get("date"),
        "report_date": datetime.now(timezone.utc).isoformat(),
        "days_forward": 5,  # adjust as needed
        "basket_perf_pct": round(basket_perf, 2),
        "per_stock": results
    }

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()