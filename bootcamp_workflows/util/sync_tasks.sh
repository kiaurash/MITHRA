#!/bin/bash

# sync_tasks.sh
# Ensures user's sprint_tasks.csv contains all tasks from the central template
# Appends missing tasks based on task_id comparison

# Note: Not using 'set -e' to avoid loop termination on grep no-match

# Paths relative to bootcamp2510 root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTCAMP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATE="$BOOTCAMP_ROOT/bootcamp_workflows/logistics/sprint_tasks_template.csv"
USER_TASKS="$BOOTCAMP_ROOT/your_workspace/logs/sprint_tasks.csv"

# Validate template exists
if [[ ! -f "$TEMPLATE" ]]; then
  echo "Error: Template file not found at $TEMPLATE"
  exit 1
fi

# Create user task file if it doesn't exist
if [[ ! -f "$USER_TASKS" ]]; then
  echo "Creating new sprint_tasks.csv..."
  echo "task_id,sprint,task,status,due_date,source,expected_artifact,date_added,notes" > "$USER_TASKS"
fi

# Get existing task_ids from user's CSV (skip header, extract first column)
existing_ids=$(tail -n +2 "$USER_TASKS" 2>/dev/null | cut -d',' -f1 || true)

# Counter for new tasks
new_count=0

# Read template line by line (skip header) using process substitution to avoid subshell
while IFS=',' read -r task_id sprint task status due_date source expected_artifact; do
  # Check if task_id exists in user's list
  if ! echo "$existing_ids" | grep -q "^${task_id}$"; then
    # Append missing task keeping all template fields, adding date_added and empty notes
    echo "${task_id},${sprint},${task},backlog,${due_date},${source},${expected_artifact},$(date +%Y-%m-%d)," >> "$USER_TASKS"
    echo "Added: $task_id - $task"
    ((new_count++))
  fi
done < <(tail -n +2 "$TEMPLATE")

if [[ $new_count -eq 0 ]]; then
  echo "All tasks up to date. No new tasks added."
else
  echo "Added $new_count new task(s) to sprint_tasks.csv"
fi
