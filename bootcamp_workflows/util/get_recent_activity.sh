#!/bin/bash

# get_recent_activity.sh
# Returns recent activity summary without loading entire activity log

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTCAMP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ACTIVITY_LOG="$BOOTCAMP_ROOT/your_workspace/logs/activity_log.csv"

# Check if activity log exists
if [[ ! -f "$ACTIVITY_LOG" ]]; then
  echo "Error: Activity log not found at $ACTIVITY_LOG"
  exit 1
fi

# Get last entry (excluding header)
last_entry=$(tail -n 1 "$ACTIVITY_LOG")

# Parse last entry
last_timestamp=$(echo "$last_entry" | cut -d',' -f1)

# Calculate days ago
if [[ -n "$last_timestamp" ]]; then
  last_epoch=$(date -d "$last_timestamp" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$last_timestamp" +%s 2>/dev/null)
  now_epoch=$(date +%s)
  days_ago=$(( (now_epoch - last_epoch) / 86400 ))
else
  days_ago="unknown"
fi

# Get last 3 workflow entries (complete/progress_check/session_complete)
recent_workflows=$(grep -E ",(complete|progress_check|session_complete)," "$ACTIVITY_LOG" | tail -n 3 | while IFS=',' read -r timestamp workflow action notes; do
  date_only=$(echo "$timestamp" | cut -d' ' -f1)
  echo "- $workflow ($action, $date_only)"
done)

# Output structured data
echo "RECENT_ACTIVITY:"
echo "last_checkin: $last_timestamp"
echo "days_ago: $days_ago"
echo "recent_workflows:"
if [[ -z "$recent_workflows" ]]; then
  echo "- No recent workflows"
else
  echo "$recent_workflows"
fi
