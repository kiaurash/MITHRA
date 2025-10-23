#!/bin/bash
# Commit State - Commit your workspace changes with a meaningful message
# Usage: ./commit_state.sh "Your commit message"

set -e

# Check if commit message was provided
if [ -z "$1" ]; then
    echo "Error: Commit message required"
    echo "Usage: ./commit_state.sh \"Your meaningful commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

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

# Check if there are any changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✓ No changes to commit, workspace already clean"
    exit 0
fi

# Stage all changes
git add .

# Check if there are staged changes (after .gitignore filtering)
if git diff --quiet --cached; then
    echo "✓ No staged changes to commit (files may be ignored by .gitignore)"
    exit 0
fi

# Show what will be committed
echo "=== Changes to be committed ==="
echo ""
git status --short --cached
echo ""

# Commit the changes
if git commit -m "$COMMIT_MESSAGE"; then
    echo ""
    echo "✓ Successfully committed workspace state"
    echo "  Message: $COMMIT_MESSAGE"
else
    echo ""
    echo "✗ Failed to commit changes"
    exit 1
fi
