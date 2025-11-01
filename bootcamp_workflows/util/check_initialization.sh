#!/bin/bash

# check_initialization.sh
# Self-contained script that:
# 1. Finds bootcamp2510 root directory (looks for your_workspace marker)
# 2. Checks if .workflow_initialized lock file exists
# 3. Outputs status: INITIALIZED or NOT_INITIALIZED
# 4. Provides helpful error messages if bootcamp root can't be found

set -e

find_bootcamp_root() {
    local current_dir="$PWD"

    # Check current directory first
    if [[ -d "$current_dir/your_workspace" && -d "$current_dir/bootcamp_workflows" ]]; then
        echo "$current_dir"
        return 0
    fi

    # Search upward
    while [[ "$current_dir" != "/" ]]; do
        if [[ -d "$current_dir/your_workspace" && -d "$current_dir/bootcamp_workflows" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir=$(dirname "$current_dir")
    done

    # Could not find root
    return 1
}

# Main execution
BOOTCAMP_ROOT=$(find_bootcamp_root)

if [[ -z "$BOOTCAMP_ROOT" ]]; then
    echo "ERROR: Could not find bootcamp2510 root directory."
    echo ""
    echo "If you launched the CLI tool from a subfolder, exit and relaunch from the root folder so I can access all relevant files."
    echo ""
    echo "Expected directory structure:"
    echo "  bootcamp2510/"
    echo "  ├── your_workspace/"
    echo "  └── bootcamp_workflows/"
    exit 1
fi

# Check for lock file
LOCK_FILE="$BOOTCAMP_ROOT/your_workspace/.workflow_initialized"

if [[ -f "$LOCK_FILE" ]]; then
    echo "INITIALIZED"
    echo "Lock file found at: $LOCK_FILE"
    exit 0
else
    echo "NOT_INITIALIZED"
    echo "Lock file not found at: $LOCK_FILE"
    exit 0
fi
