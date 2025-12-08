#!/data/data/com.termux/files/usr/bin/bash

BASE="/data/data/com.termux/files/home/storage/shared/bursasearch/myx_shop/js"
BACKUP_DIR="$BASE/backups"
LOGFILE="$BASE/manager.log"
CONF="$BASE/shops.conf"

shops=( $(grep -oP '^\[\K[^\]]+' "$CONF") )

log_action() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") | [$shop] $1" >> "$LOGFILE"
}

choose_shop() {
  echo "Available shops:"
  for i in "${!shops[@]}"; do
    echo "$((i+1))) ${shops[$i]}"
  done
  read -p "Choose shop (1-${#shops[@]}): " choice
  shop=${shops[$((choice-1))]}

  SRC="$BASE/${shop}_lists.json"
  DEST_ADMIN="$BASE/Admin/${shop}_lists.json"
  DEST_STAFF="$BASE/Staff/${shop}_lists.json"
  SHOP_BACKUP="$BACKUP_DIR/$shop"
  mkdir -p "$SHOP_BACKUP"

  csv_default=$(grep -A2 "\[$shop\]" "$CONF" | grep csv_default | cut -d= -f2)
  expected_keys=$(grep -A2 "\[$shop\]" "$CONF" | grep expected_keys | cut -d= -f2 | tr ',' ' ')
  echo "🔄 Current shop set to: $shop (default CSV: $csv_default)"
  log_action "Switched to shop: $shop"
}

menu() {
  echo "=== Shops Manager ($shop) ==="
  echo "1) Import JSON → CSV"
  echo "2) Export CSV → JSON (with backup)"
  echo "3) Validate JSON"
  echo "4) Copy JSON → Admin & Staff"
  echo "5) Run Full Cycle (Export → Validate → Copy)"
  echo "6) Restore from Backup"
  echo "7) View Log (last 20 entries)"
  echo "8) Switch Shop"
  echo "0) Exit"
  echo "=============================="
}

import_json() {
  input=$1
  output=$2

  if [ ! -f "$input" ]; then
    echo "❌ JSON file not found: $input"
    log_action "Import failed: missing $input"
    return
  fi

  if ! jq -e 'length > 0' "$input" >/dev/null; then
    echo "⚠️ JSON file is empty: $input"
    log_action "Import failed: empty JSON"
    return
  fi

  keys=$(jq -r '.[0] | keys_unsorted | @csv' "$input")
  if [ -z "$keys" ]; then
    echo "⚠️ No keys found in first object of $input"
    log_action "Import failed: no keys in JSON"
    return
  fi

echo "📂 Importing from: $input"

 jq -r '
(.products[0] | keys_unsorted) as $keys |
$keys,
map(.products[] | [.[ $keys[] ]])[] |
@csv
' "$input" > "$output"

  echo "✅ Imported $input → $output"
  log_action "Imported $input → $output"
}

export_json() {
  input=$1
  output=$2

  if [ ! -f "$input" ]; then
    echo "❌ CSV file not found: $input"
    log_action "Export failed: missing $input"
    return
  fi

  jq -Rn '
    (input | split(",") ) as $keys |
    [ inputs
      | split(",")
      | [ $keys, . ]
      | transpose
      | map({(.[0]): .[1]})
      | add
    ]
  ' "$input" > "$output"

  echo "✅ Exported $input → $output"
  log_action "Exported $input → $output"

  timestamp=$(date +"%Y%m%d_%H%M%S")
  backup_file="$SHOP_BACKUP/${shop}_lists_$timestamp.json"
  cp "$output" "$backup_file"
  echo "📦 Backup created: $backup_file"
  log_action "Backup created: $backup_file"

  backups=( $(ls -t "$SHOP_BACKUP"/${shop}_lists_*.json 2>/dev/null) )
  if [ ${#backups[@]} -gt 3 ]; then
    old_backups=( "${backups[@]:3}" )
    for f in "${old_backups[@]}"; do
      rm "$f"
      echo "🗑️ Removed old backup: $f"
      log_action "Removed old backup: $f"
    done
  fi
}

validate_json() {
  file=$1
  if ! jq empty "$file" >/dev/null 2>&1; then
    echo "❌ $file is NOT valid JSON"
    log_action "Validated $file: FAILED"
    exit 1
  fi

  echo "✅ $file is valid JSON"
  log_action "Validated $file: OK"

  for key in $expected_keys; do
    if ! jq -e ".[0] | has(\"$key\")" "$file" >/dev/null; then
      echo "⚠️ Missing key: $key"
      log_action "Validation warning: missing key $key"
    else
      echo "✔️ Found key: $key"
    fi
  done
  echo "Validation complete."
}

copy_json() {
  if [ ! -f "$SRC" ]; then
    echo "❌ Source file not found: $SRC"
    log_action "Copy failed: source missing"
    exit 1
  fi
  cp "$SRC" "$DEST_ADMIN" && echo "✅ Copied to Admin"
  cp "$SRC" "$DEST_STAFF" && echo "✅ Copied to Staff"
  echo "🎯 Done: ${shop}_lists.json propagated"
  log_action "Copied $SRC → Admin & Staff"
}

restore_backup() {
  backups=( $(ls -t "$SHOP_BACKUP"/${shop}_lists_*.json 2>/dev/null) )
  if [ ${#backups[@]} -eq 0 ]; then
    echo "❌ No backups available"
    log_action "Restore failed: no backups"
    return
  fi

  echo "Available backups for $shop:"
  for i in "${!backups[@]}"; do
    echo "$((i+1))) ${backups[$i]}"
  done

  read -p "Choose backup to restore (1-${#backups[@]}): " choice
  if [[ $choice -ge 1 && $choice -le ${#backups[@]} ]]; then
    cp "${backups[$((choice-1))]}" "$SRC"
    echo "✅ Restored ${backups[$((choice-1))]} → $SRC"
    log_action "Restored backup: ${backups[$((choice-1))]}"
    copy_json
  else
    echo "❌ Invalid choice"
    log_action "Restore failed: invalid choice"
  fi
}

view_log() {
  echo "=== Last 20 log entries ==="
  tail -n 20 "$LOGFILE"
}

full_cycle() {
  read -p "Input CSV filename (inside js folder) [default: $csv_default]: " csvfile
  csvfile=${csvfile:-$csv_default}
  export_json "$BASE/$csvfile" "$SRC"
  validate_json "$SRC"
  copy_json
  log_action "Full cycle completed with $csvfile"
}

# --- Main Loop ---
choose_shop
while true; do
  menu
  read -p "Choose option: " choice
  case $choice in
    1) import_json "$SRC" "$BASE/$csv_default";;
    2) read -p "Input CSV filename (inside js folder) [default: $csv_default]: " i; i=${i:-$csv_default}; read -p "Output JSON: " o; export_json "$BASE/$i" "$o";;
    3) read -p "File to validate: " f; validate_json "$f";;
    4) copy_json;;
    5) full_cycle;;
    6) restore_backup;;
    7) view_log;;
    8) choose_shop;;
    0) echo "👋 Exiting"; log_action "Exited Shops Manager"; exit 0;;
    *) echo "❌ Invalid choice";;
  esac
done
