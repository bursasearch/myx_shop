#!/bin/bash
# ============================================
# Fix history dates and log changes (Audit-Safe)
# ============================================

set -e

DATE_TAG=$(date +%Y%m%d)
AUDIT_LOG="audit_logs/${DATE_TAG}_fix_history.json"

echo "🗂 Fixing history dates..."

# Example: normalize JSON history files
for f in history/*.json web/history/*.json; do
  if [ -f "$f" ]; then
    echo "  ➡️ Processing $f"
    # Run your date-fixing logic here
    # For example, using jq to ensure valid date fields:
    tmpfile=$(mktemp)
    jq '(.date |= (if . == null or . == "" then "unknown" else . end))' "$f" > "$tmpfile" && mv "$tmpfile" "$f"

    # Log the update
    echo "{ \"file\": \"$f\", \"fixed_at\": \"$(date --iso-8601=seconds)\" }" >> "$AUDIT_LOG"
  fi
done

echo "✅ History dates fixed. Audit log written to $AUDIT_LOG"
