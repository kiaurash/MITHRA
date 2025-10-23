# Bootcamp2510 - Claude Code Configuration

## Project Structure

```
bootcamp2510/
├── bootcamp_workflows/
│   ├── building/           # 10-phase building workflows
│   ├── logistics/          # Reference info (program, deliverables, help)
│   │   └── sprint_tasks_template.csv  # Central task manifest
│   └── util/              # Utility scripts (use these!)
│       ├── sync_tasks.sh              # Sync task list from template
│       ├── check_upcoming_tasks.sh    # Show tasks due in 3 days + workflows
│       ├── get_task_stats.sh          # Task completion statistics
│       ├── get_recent_activity.sh     # Recent workflow activity
│       └── get_participant_info.sh    # Background, sprint, goals
├── master_orchestrator/   # Main navigation/progress workflow
└── your_workspace/        # Participant workspace (created at runtime)
    ├── logs/
    │   ├── activity_log.csv      # All workflow activity
    │   └── sprint_tasks.csv      # User's task list (synced from template)
    ├── profile/
    │   └── participant_profile.md
    ├── reports/
    ├── data/
    └── your_workflows/    # User-generated workflows
```

## Context Reduction Pattern

**Check for utility scripts first. If script exists, use it. If not, load the full file.**

Available utility scripts:

```bash
./bootcamp_workflows/util/sync_tasks.sh              # Sync tasks from template
./bootcamp_workflows/util/get_task_stats.sh          # done/in_progress/backlog counts
./bootcamp_workflows/util/check_upcoming_tasks.sh    # Tasks due in 3 days + workflows
./bootcamp_workflows/util/get_recent_activity.sh     # Last check-in, recent workflows
./bootcamp_workflows/util/get_participant_info.sh    # Background, week, sprint, goals
./bootcamp_workflows/util/check_state.sh             # Check for uncommitted changes
./bootcamp_workflows/util/commit_state.sh            # Commit workspace changes
```

Scripts output structured data (~100-400 tokens) instead of loading full CSV/MD files (~1000+ tokens).

## Workflow Execution Protocol

When executing workflows:

1. Parse YAML frontmatter for structure
2. Read step prompt files sequentially
3. Auto-log to activity_log.csv
4. Create expected artifacts per workflow spec

## Task Management System

**Template:** `bootcamp_workflows/logistics/sprint_tasks_template.csv` (source of truth)
**User list:** `your_workspace/logs/sprint_tasks.csv` (synced, user-managed)

**CSV columns:** task_id, sprint, task, status, due_date, source, expected_artifact

**Valid status values:**

- `backlog` - Not started
- `in_progress` - Currently working on
- `done` - Completed

**Adding entries:**

- Edit template CSV to add new tasks
- Run `sync_tasks.sh` to propagate to user lists
- Users can manually edit their sprint_tasks.csv (add custom tasks, update status)

**Activity logging:**
All workflows log to `your_workspace/logs/activity_log.csv`:

```csv
timestamp,workflow_name,action,notes
2025-10-22 14:30:00,ideation_workflow,complete,Generated YAML workflow
```

## Commit State Protocol

When user requests to commit their workspace state, follow protocol in `bootcamp_workflows/logistics/commit_instructions/commit_state_instructions.md`.

## Cohort Dates

- Start: Oct 20, 2025
- Sprint 1: weeks 1-2 (demo Oct 27)
- Sprint 2: weeks 3-4 (demo Nov 10)
- Sprint 3: weeks 5-6 (demo Nov 24)
- Final: week 7 (demo Dec 5)

# IMPORTANT

Follow KISS and YANGI

KISS ("Keep It Simple, Stupid") and YAGNI ("You Aren't Gonna Need It") are software development principles that prioritize simplicity and practicality. KISS focuses on making code and designs as simple and straightforward as possible, while YAGNI advises against adding features or code that aren't immediately necessary to avoid complexity and wasted effort. When used together, they promote cleaner, more maintainable, and efficient code
