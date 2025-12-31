#!/bin/bash
# ============================================
# Bursa EOD Pipeline Runner (Audit-Safe + Menu)
# ============================================

# Usage:
#   run_pipeline.sh /full/path/to/YYYYMMDD.csv
#   run_pipeline.sh --menu   # interactive file picker

set -e  # stop on first error

choose_file_menu() {
  echo "📂 Available CSV files:"
  local files=(*.csv)
  if [ ${#files[@]} -eq 0 ]; then
    echo "❌ No CSV files found in current directory."
    exit 1
  fi

  local i=1
  for f in "${files[@]}"; do
    echo "  [$i] $f"
    ((i++))
  done

  read -p "👉 Select a file number: " choice
  RAW_FILE="${files[$((choice-1))]}"
}

# --- Main logic ---
if [ "$1" == "--menu" ]; then
  choose_file_menu
else
  RAW_FILE="$1"
fi

if [ -z "$RAW_FILE" ]; then
  echo "❌ No EOD file provided."
  echo "Usage: run_pipeline.sh /full/path/to/YYYYMMDD.csv OR run_pipeline.sh --menu"
  exit 1
fi

if [ ! -f "$RAW_FILE" ]; then
  echo "❌ File not found: $RAW_FILE"
  exit 1
fi

RAW_DIR="$(dirname "$RAW_FILE")"
RAW_NAME="$(basename "$RAW_FILE")"
DATE_TAG="${RAW_NAME%.*}"   # strip .csv

echo "📂 Checking directory: $RAW_DIR"
ls -lh "$RAW_DIR"

echo "📥 Using EOD file: $RAW_FILE"

# Step 1: Normalize EOD data
echo "🔧 Normalizing EOD data..."
python3 scripts/normalize_eod.py "$RAW_FILE" "normalized_output/${DATE_TAG}_normalized.csv" "scripts/config/eod_config.json" "audit_logs/${DATE_TAG}_audit.json"

# Step 2: Generate JSON exports
echo "📊 Generating JSON exports..."
python3 scripts/generate_json_from_eod_fixed_v2.py "normalized_output/${DATE_TAG}_normalized.csv"

# Step 3: Fix history dates
echo "🗂 Fixing history dates..."
bash fix_history_dates.sh

# Step 4: Archive raw CSV
echo "📦 Archiving raw file..."
mkdir -p backups
cp "$RAW_FILE" "backups/${DATE_TAG}_$(date +%Y%m%d_%H%M%S).csv"

# Step 5: Commit and push to GitHub Pages
echo "⬆️ Committing and pushing changes..."
git add .
git commit -m "Add EOD data for $DATE_TAG"
git push origin main

echo "✅ Pipeline completed successfully!"

echo "🌐 Dashboard updated with EOD $DATE_TAG"
