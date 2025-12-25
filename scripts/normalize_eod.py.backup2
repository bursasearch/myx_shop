#!/usr/bin/env python3
import sys, csv, json, os
from datetime import datetime, timezone

def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_delimiter(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        sample = f.read(4096)
    if "\t" in sample and sample.count("\t") >= sample.count(","):
        return "\t"
    return ","

def normalize_header(header, aliases):
    normalized = []
    for col in header:
        c = col.strip()
        normalized.append(aliases.get(c, c))
    return normalized

def main():
    if len(sys.argv) < 4:
        print("Usage: normalize_eod.py input.csv output.csv eod_config.json [audit.json]")
        sys.exit(1)

    infile, outfile, configfile = sys.argv[1], sys.argv[2], sys.argv[3]
    auditfile = sys.argv[4] if len(sys.argv) > 4 else None

    config = load_config(configfile)
    schema = config["schema"]
    aliases = config.get("map", {})
    defaults = config.get("fill", {})
    sector_lookup = config.get("sector_lookup", {})

    delim = detect_delimiter(infile)

    with open(infile, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delim)
        rows = list(reader)

    if not rows:
        print("Empty input.")
        sys.exit(1)

    raw_header = rows[0]
    header = normalize_header(raw_header, aliases)

    # Map original column index to canonical name
    idx_to_name = {}
    for i, name in enumerate(header):
        if name in schema:
            idx_to_name[i] = name

    out_rows = []
    missing_columns = [c for c in schema if c not in header]
    missing_sector_codes = set()

    for r in rows[1:]:
        record = {c: None for c in schema}
        for i, cell in enumerate(r):
            canon = idx_to_name.get(i)
            if not canon:
                continue
            val = cell.strip()
            record[canon] = val if val != "" else None

        # Fill defaults
        for c in schema:
            if record[c] is None:
                record[c] = defaults.get(c, "-")

        # Replace sector codes with names
        sector_code = record["Sector"]
        if sector_code in sector_lookup:
            record["Sector"] = sector_lookup[sector_code]
        else:
            if sector_code not in ("", None, "-", "Unknown"):
                missing_sector_codes.add(sector_code)
            record["Sector"] = "Unknown"

        out_rows.append([record[c] for c in schema])

    # Write normalized CSV
    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(schema)
        w.writerows(out_rows)

    # Audit log
    if auditfile:
        audit = {
            "source_file": os.path.basename(infile),
            "output_file": os.path.basename(outfile),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "delimiter_detected": "tab" if delim == "\t" else "comma",
            "present_columns": header,
            "missing_columns_filled": missing_columns,
            "rows_in": max(0, len(rows)-1),
            "rows_out": len(out_rows),
            "new_sector_codes": sorted(list(missing_sector_codes))
        }
        os.makedirs(os.path.dirname(auditfile) or ".", exist_ok=True)
        with open(auditfile, "w", encoding="utf-8") as af:
            json.dump(audit, af, indent=2)

    # Log missing sector codes separately
    if missing_sector_codes:
        log_path = "sector_missing.json"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []
        for code in sorted(missing_sector_codes):
            if code not in existing:
                existing.append(code)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

    print(f"Normalized: {outfile}")

if __name__ == "__main__":
    main()