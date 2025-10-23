#!/bin/bash

# get_participant_info.sh
# Extracts key participant info without loading entire profile

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTCAMP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROFILE="$BOOTCAMP_ROOT/your_workspace/profile/participant_profile.md"

# Check if profile exists
if [[ ! -f "$PROFILE" ]]; then
  echo "Error: Profile not found at $PROFILE"
  exit 1
fi

# Extract background/technical level from "Technical Approach" section
background=$(grep -A 1 "^**Technical Approach:**" "$PROFILE" | tail -n 1 | sed 's/^[[:space:]]*//')

# Extract all sprint goals for context
sprint1_goal=$(grep -A 1 "^**Sprint 1 (Weeks" "$PROFILE" | tail -n 1 | sed 's/^[[:space:]]*//')
sprint2_goal=$(grep -A 1 "^**Sprint 2 (Weeks" "$PROFILE" | tail -n 1 | sed 's/^[[:space:]]*//')
sprint3_goal=$(grep -A 1 "^**Sprint 3 (Weeks" "$PROFILE" | tail -n 1 | sed 's/^[[:space:]]*//')

# Determine current sprint based on current date
cohort_start="2025-10-20"
today=$(date +%Y-%m-%d)

# Calculate week number
start_epoch=$(date -d "$cohort_start" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$cohort_start" +%s 2>/dev/null)
today_epoch=$(date -d "$today" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$today" +%s 2>/dev/null)
days_diff=$(( (today_epoch - start_epoch) / 86400 ))
week_num=$(( (days_diff / 7) + 1 ))

# Determine sprint (Sprint 1: weeks 1-2, Sprint 2: weeks 3-4, Sprint 3: weeks 5-6, Final: week 7)
if [[ $week_num -le 2 ]]; then
  current_sprint=1
elif [[ $week_num -le 4 ]]; then
  current_sprint=2
elif [[ $week_num -le 6 ]]; then
  current_sprint=3
else
  current_sprint="final"
fi

# Output structured data
echo "PARTICIPANT_INFO:"
echo "background: ${background:-Not specified}"
echo "current_week: $week_num"
echo "current_sprint: $current_sprint"
echo "sprint1_goal: ${sprint1_goal:-Not set}"
echo "sprint2_goal: ${sprint2_goal:-Not set}"
echo "sprint3_goal: ${sprint3_goal:-Not set}"
