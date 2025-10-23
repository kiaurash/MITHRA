# Master Orchestrator Workflow

> **New to the bootcamp?** Start with `/bootcamp2510/START_HERE.md` for onboarding and overview.

## Purpose

The Master Orchestrator is your adaptive navigation and coaching system for the bootcamp. It:

- Assesses your current progress and status (on track, ahead, behind, stuck)
- Routes you to the right workflows and resources based on your needs
- Tracks your activity and provides context-aware guidance
- Helps you stay oriented throughout your 7-week journey

Think of it as your personal GPS for the bootcamp—always knows where you are and helps you get where you need to go.

## Workflow Architecture

### Step 1: Check Initialization
- Determines if this is first run or returning user
- Routes to orientation workflow if needed (see `../bootcamp_workflows/logistics/orientation/`)
- For returning users, proceeds to progress assessment

### Step 2: Orientation Redirect (First Time Only)
- Launches orientation workflow for initial setup
- Creates workspace structure (`your_workspace/profile/`, `logs/`, `reports/`, `data/`)
- Captures participant profile and goals
- Helps define project idea
- Returns to main menu after completion

### Step 3: Progress Assessment (Returning Users)
- Reads activity log and workspace files
- Calculates current week, sprint, and time since last check-in
- Assesses status: on track / ahead / behind / stuck
- Builds context for personalized guidance

### Step 4: Menu and Routing
- Presents options based on current status and needs:
  - View program information
  - Access building workflows (phases 1-10)
  - Get help (logistics, technical, mentorship)
  - Review/update goals
  - Plan catch-up strategy (if behind)
- Routes to selected workflow or resource
- Logs activity for next session

## How to Execute

**Command:**
```bash
Execute workflow: workflows/bootcamp2510/master_orchestrator/master_orchestrator_workflow.md
```

**Entry Point:** `master_orchestrator_workflow.md`

**Execution Time:**
- First run: ~30-45 minutes (includes orientation)
- Return visits: ~60-90 minutes (includes progress check + working through building workflows)

**Recommended Frequency:**
- Ideal: 2-3 times per week (Monday, mid-week, weekend)
- Minimum: Once per week (Mondays)
- Critical: Start of sprints, before demos, when stuck

## Workspace Structure Created

On first run, this workflow creates:

```
your_workspace/
├── profile/
│   └── participant_profile.md        # Profile, goals, project definition
├── logs/
│   └── activity_log.csv              # All workflow activity with timestamps
├── reports/                          # Sprint reports from building workflows
├── data/                             # Generated data files
└── your_workflows/                   # Your custom workflows
```

## Activity Logging

**Log location:** `your_workspace/logs/activity_log.csv`

**Fields tracked:**
- Timestamp
- Workflow name
- Status (on-track/ahead/behind/stuck)
- Current week/sprint
- Actions taken
- Files created/modified
- Notes/observations

**Purpose:** Provides continuity between sessions, enables context-aware guidance, tracks progress over time.

## Routing Logic

The workflow adapts its menu and recommendations based on:

**Status Assessment:**
- **On track:** Offers next building phase, goal review, or exploration
- **Ahead:** Suggests advanced topics, helping others, refinement work
- **Behind:** Prioritizes catch-up planning, identifies blockers, suggests focus areas
- **Stuck:** Offers immediate help resources, mentor booking, problem diagnosis

**Context Factors:**
- Current week and sprint
- Time since last check-in
- Recent activity patterns
- Upcoming deliverables
- Completion status of building phases

## Integration with Other Workflows

**Orientation workflow:** `../bootcamp_workflows/logistics/orientation/`
- Called automatically on first run
- Can be re-run if workspace needs reset

**Building workflows:** `../bootcamp_workflows/building/1_ideation/` through `/10_cost_optimization/`
- Linked from menu based on current phase
- Progress tracked in activity log

**Logistics resources:** `../bootcamp_workflows/logistics/`
- Program information
- Sprint deliverables
- Getting help

## Design Principles

**Adaptive, not static:** Responds to participant's current situation and needs

**Conversational, not interrogative:** Natural dialogue, not form-filling

**Context-aware:** Remembers history, understands timeline, knows what's coming

**Judgment-based:** Makes recommendations, not rigid rules

**Human-in-loop:** Guides and suggests, never forces or automates away control

## Troubleshooting

**Workflow not finding workspace:**
- Ensure you're in a stable working directory
- Check that `your_workspace/` folder exists (created on first run)
- Verify activity_log.csv is being created and updated

**Orientation not triggering:**
- Delete `your_workspace/profile/participant_profile.md` to force re-initialization
- Or manually run orientation: `../bootcamp_workflows/logistics/orientation/orientation_workflow.md`

**Activity log issues:**
- Check CSV format and permissions
- Ensure logs directory exists: `your_workspace/logs/`
- Verify timestamps are being written correctly

## Support

**For workflow issues:**
- Slack: #agents-bootcamp-2510
- Email: bootcamp@ai.science
- Tag: @amir

**For improvement ideas:**
- Share in Slack—workflows evolve based on feedback
- Usage patterns inform future enhancements

---

**For user onboarding and high-level overview:** See `../START_HERE.md`
