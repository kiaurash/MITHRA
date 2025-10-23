# Commit State Protocol

## Execution Steps

### 1. Check for uncommitted changes

Run from bootcamp root:
```bash
./bootcamp_workflows/util/check_state.sh
```

If script shows no changes, stop.

### 2. Commit the changes

Based on changes shown, craft a meaningful commit message and run:
```bash
./bootcamp_workflows/util/commit_state.sh "Your meaningful message here"
```

Use imperative mood (e.g., "Complete workflow" not "Completed workflow").

### 3. Confirm to user

After successful commit, inform user: "Workspace state committed"
