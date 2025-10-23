#!/bin/bash
# Check State - Show uncommitted changes in your workspace
# Usage: ./check_state.sh

set -e

# Navigate to your_workspace directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$SCRIPT_DIR/../../your_workspace"

cd "$WORKSPACE_DIR"

# Check if this is a git repo, initialize if not
if [ ! -d .git ]; then
    echo "Initializing git repository in your_workspace..."
    git init
    echo ""
fi

echo "=== Git Status in your_workspace ==="
echo ""

# Check for changes
changes=$(git status --porcelain)

if [ -z "$changes" ]; then
    echo "✓ No pending changes, workspace clean"
    exit 0
fi

echo "Uncommitted changes found:"
echo ""
git status --short
echo ""
echo "=== Change Statistics ==="
echo ""
git diff --stat
echo ""
echo "To commit these changes, use: commit_state.sh \"your meaningful message here\""
