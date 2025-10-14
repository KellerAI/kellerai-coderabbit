#!/bin/bash

# RepoPrompt PyCharm Integration Helper
# Usage: open-repoprompt.sh <project_directory> <workspace_name> [options]

set -e

PROJECT_DIR="${1:-}"
WORKSPACE_NAME="${2:-}"

# Validate inputs
if [[ -z "$PROJECT_DIR" ]]; then
    echo "Error: Project directory not provided"
    echo "Usage: open-repoprompt.sh <project_directory> <workspace_name>"
    exit 1
fi

if [[ -z "$WORKSPACE_NAME" ]]; then
    echo "Error: Workspace name not provided"
    echo "Usage: open-repoprompt.sh <project_directory> <workspace_name>"
    exit 1
fi

# Expand tilde if present (though RepoPrompt does this too)
PROJECT_DIR="${PROJECT_DIR/#\~/$HOME}"

# Build RepoPrompt URL
REPOPROMPT_URL="repoprompt://open/${PROJECT_DIR}?workspace=${WORKSPACE_NAME}&focus=true"

# Optional: Add specific files to auto-select
# Uncomment and customize as needed:
# REPOPROMPT_URL="${REPOPROMPT_URL}&files=CLAUDE.md,.taskmaster/CLAUDE.md"

# Log what we're doing (optional - comment out if not needed)
echo "Opening RepoPrompt..."
echo "  Project: $PROJECT_DIR"
echo "  Workspace: $WORKSPACE_NAME"
echo "  URL: $REPOPROMPT_URL"

# Open RepoPrompt
open "$REPOPROMPT_URL"

exit 0
