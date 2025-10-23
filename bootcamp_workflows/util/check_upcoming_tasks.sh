#!/bin/bash

# check_upcoming_tasks.sh
# Shows tasks that are backlog or in_progress with due dates within the next 3 days

# Paths relative to bootcamp2510 root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTCAMP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
USER_TASKS="$BOOTCAMP_ROOT/your_workspace/logs/sprint_tasks.csv"

# Check if task file exists
if [[ ! -f "$USER_TASKS" ]]; then
  echo "Error: Task file not found at $USER_TASKS"
  echo "Run sync_tasks.sh first to create your task list."
  exit 1
fi

# Get current date and date 3 days from now (in YYYY-MM-DD format)
TODAY=$(date +%Y-%m-%d)
THREE_DAYS_OUT=$(date -d "+3 days" +%Y-%m-%d 2>/dev/null || date -v+3d +%Y-%m-%d 2>/dev/null)

# Convert date to seconds since epoch for comparison
today_epoch=$(date -d "$TODAY" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$TODAY" +%s 2>/dev/null)
three_days_epoch=$(date -d "$THREE_DAYS_OUT" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$THREE_DAYS_OUT" +%s 2>/dev/null)

echo "Upcoming Tasks (due within next 3 days)"
echo "========================================"
echo ""

# Counter for tasks found
count=0

# Read task file line by line (skip header)
while IFS=',' read -r task_id sprint task status due_date source expected_artifact date_added notes; do
  # Skip if status is not backlog or in_progress
  if [[ "$status" != "backlog" && "$status" != "in_progress" ]]; then
    continue
  fi

  # Convert due_date to epoch for comparison
  due_epoch=$(date -d "$due_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$due_date" +%s 2>/dev/null)

  # Check if due_date is within the next 3 days
  if [[ $due_epoch -le $three_days_epoch ]]; then
    # Calculate days until due
    days_diff=$(( (due_epoch - today_epoch) / 86400 ))

    # Format status indicator
    if [[ "$status" == "in_progress" ]]; then
      status_icon="🔵"
    else
      status_icon="⬜"
    fi

    # Format urgency
    if [[ $days_diff -lt 0 ]]; then
      urgency="⚠️  OVERDUE (${days_diff#-} days ago)"
    elif [[ $days_diff -eq 0 ]]; then
      urgency="🔴 DUE TODAY"
    elif [[ $days_diff -eq 1 ]]; then
      urgency="🟡 Due tomorrow"
    else
      urgency="   Due in $days_diff days"
    fi

    echo "$status_icon [$due_date] $urgency"
    echo "   $task"
    echo ""

    ((count++))
  fi
done < <(tail -n +2 "$USER_TASKS")

if [[ $count -eq 0 ]]; then
  echo "No upcoming tasks found."
  echo "All tasks are either completed or due more than 3 days out."
else
  echo "========================================"
  echo "Total: $count task(s) need attention"
fi
