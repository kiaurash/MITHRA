#!/bin/bash

# get_task_stats.sh
# Returns task completion statistics without loading entire CSV into context

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTCAMP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
USER_TASKS="$BOOTCAMP_ROOT/your_workspace/logs/sprint_tasks.csv"

# Check if task file exists
if [[ ! -f "$USER_TASKS" ]]; then
  echo "Error: Task file not found at $USER_TASKS"
  exit 1
fi

# Count tasks by status
done_count=$(grep -c ",done," "$USER_TASKS" 2>/dev/null || echo 0)
in_progress_count=$(grep -c ",in_progress," "$USER_TASKS" 2>/dev/null || echo 0)
backlog_count=$(grep -c ",backlog," "$USER_TASKS" 2>/dev/null || echo 0)

# Calculate total (excluding header)
total_count=$((done_count + in_progress_count + backlog_count))

# Calculate completion percentage
if [[ $total_count -gt 0 ]]; then
  completion=$((done_count * 100 / total_count))
else
  completion=0
fi

# Output structured data
echo "TASK_STATS:"
echo "done: $done_count"
echo "in_progress: $in_progress_count"
echo "backlog: $backlog_count"
echo "total: $total_count"
echo "completion: ${completion}%"
