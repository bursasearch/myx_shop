#!/usr/bin/env python3
import csv, json, sys
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 4:
        print("Usage: picker.py <normalized_eod.csv> <picker_config.py> <picks.json>")
        sys.exit(1)

    infile = sys.argv[1]
    configfile = sys.argv[2]
    outfile = sys.argv[3]

    # Load config (simplified example)
    import importlib.util
    spec = importlib.util.spec_from_file_location("picker_config", configfile)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)

    picks_list = []
    with open(infile, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply your selection logic here
            picks_list.append({
                "Code": row.get("Code"),
                "Stock": row.get("Stock"),
                "Sector": row.get("Sector"),
                "Score": row.get("Score"),
                "Last": row.get("Last"),
                "Chg": row.get("Chg")
            })

    snapshot = {
        "date": datetime.now(timezone.utc).isoformat(),
        "context": {
            "universe": getattr(cfg, "UNIVERSE", "All"),
            "min_price": getattr(cfg, "MIN_PRICE", 0),
            "min_vol": getattr(cfg, "MIN_VOL", 0),
            "sector_cap": getattr(cfg, "SECTOR_CAP", "All")
        },
        "picks": picks_list[:10]  # top 10
    }

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

if __name__ == "__main__":
    main()