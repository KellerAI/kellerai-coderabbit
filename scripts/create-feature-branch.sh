#!/opt/homebrew/bin/bash
# KellerAI Feature Branch Creator
# Usage: ./scripts/create-feature-branch.sh [type] [name] [project-name]
#        (Interactive mode if no arguments provided)

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Branch types
VALID_TYPES=("feat" "bug" "hotfix" "chore" "docs" "refactor")

# Default project name (will be replaced during setup)
DEFAULT_PROJECT_NAME="2024-taxes"

# Interactive prompt function
prompt_for_input() {
	local prompt_text="$1"
	local default_value="$2"
	local user_input

	if [[ -n "$default_value" ]]; then
		echo -ne "${BLUE}${prompt_text} [${default_value}]: ${NC}"
	else
		echo -ne "${BLUE}${prompt_text}: ${NC}"
	fi

	read -r user_input

	if [[ -z "$user_input" ]] && [[ -n "$default_value" ]]; then
		echo "$default_value"
	else
		echo "$user_input"
	fi
}

# Interactive mode: prompts if no arguments provided
if [[ $# -eq 0 ]]; then
	echo -e "${YELLOW}=== KellerAI Feature Branch Creator (Interactive Mode) ===${NC}"
	echo ""

	# Prompt for branch type
	echo -e "${BLUE}Available branch types:${NC}"
	for i in "${!VALID_TYPES[@]}"; do
		echo "  $((i+1)). ${VALID_TYPES[$i]}"
	done
	echo ""

	BRANCH_TYPE=$(prompt_for_input "Select branch type (1-${#VALID_TYPES[@]} or name)")

	# If user entered a number, convert to type name
	if [[ "$BRANCH_TYPE" =~ ^[0-9]+$ ]] && [[ "$BRANCH_TYPE" -ge 1 ]] && [[ "$BRANCH_TYPE" -le "${#VALID_TYPES[@]}" ]]; then
		BRANCH_TYPE="${VALID_TYPES[$((BRANCH_TYPE-1))]}"
	fi

	# Prompt for branch name
	BRANCH_NAME=$(prompt_for_input "Enter branch name (e.g., 'add-login-feature')")

	# Prompt for project name
	PROJECT_NAME=$(prompt_for_input "Enter project name" "$DEFAULT_PROJECT_NAME")

	echo ""
else
	# Command-line mode: use arguments
	BRANCH_TYPE="$1"
	BRANCH_NAME="$2"
	PROJECT_NAME="${3:-$DEFAULT_PROJECT_NAME}"
fi

# Validate inputs
if [[ -z "$BRANCH_TYPE" ]] || [[ -z "$BRANCH_NAME" ]]; then
	echo -e "${RED}Error: Branch type and name are required${NC}"
	echo "Usage: $0 [type] [name] [project-name]"
	echo "Types: ${VALID_TYPES[*]}"
	exit 1
fi

# Validate branch type
if [[ ! " ${VALID_TYPES[*]} " =~ " ${BRANCH_TYPE} " ]]; then
	echo -e "${RED}Invalid branch type: $BRANCH_TYPE${NC}"
	echo "Valid types: ${VALID_TYPES[*]}"
	exit 1
fi

# Validate project name
if [[ -z "$PROJECT_NAME" ]]; then
	echo -e "${RED}Error: Project name is required${NC}"
	exit 1
fi

# Determine project type (KellerAI or Personal) based on dev location
KELLERAI_DEV_PATH="$HOME/_kellerai-dev/$PROJECT_NAME"
PERSONAL_DEV_PATH="$HOME/_personal-dev/$PROJECT_NAME"

if [[ -d "$KELLERAI_DEV_PATH" ]]; then
	DEV_PATH="$KELLERAI_DEV_PATH"
	WORKTREE_BASE="$HOME/_kellerai-worktrees/$PROJECT_NAME"
elif [[ -d "$PERSONAL_DEV_PATH" ]]; then
	DEV_PATH="$PERSONAL_DEV_PATH"
	WORKTREE_BASE="$HOME/_personal-worktrees/$PROJECT_NAME"
else
	echo -e "${RED}Dev worktree not found for project: $PROJECT_NAME${NC}"
	echo "Tried:"
	echo "  - $KELLERAI_DEV_PATH"
	echo "  - $PERSONAL_DEV_PATH"
	exit 1
fi

BRANCH_FULL_NAME="$BRANCH_TYPE/$BRANCH_NAME"
WORKTREE_PATH="$WORKTREE_BASE/$BRANCH_FULL_NAME"

# Summary
echo -e "${YELLOW}=== Creating Feature Branch ===${NC}"
echo -e "${BLUE}Project:${NC}     $PROJECT_NAME"
echo -e "${BLUE}Branch Type:${NC} $BRANCH_TYPE"
echo -e "${BLUE}Branch Name:${NC} $BRANCH_NAME"
echo -e "${BLUE}Full Branch:${NC} $BRANCH_FULL_NAME"
echo -e "${BLUE}Location:${NC}    $WORKTREE_PATH"
echo ""

# Confirm before proceeding (interactive mode only)
if [[ $# -eq 0 ]]; then
	echo -ne "${YELLOW}Proceed with branch creation? (y/N): ${NC}"
	read -r confirm
	if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
		echo -e "${RED}Cancelled${NC}"
		exit 0
	fi
	echo ""
fi

# Create worktree directory structure
mkdir -p "$WORKTREE_BASE/$BRANCH_TYPE"

# Create worktree
echo -e "${BLUE}Creating feature branch worktree...${NC}"
cd "$DEV_PATH"
git worktree add -b "$BRANCH_FULL_NAME" "$WORKTREE_PATH" dev

# Create symlinks for .serena, .taskmaster, and .venv
echo -e "${BLUE}Creating symlinks to dev branch...${NC}"
cd "$WORKTREE_PATH"
# Remove existing directories/symlinks if they exist (git may have checked them out)
rm -rf .serena .taskmaster .venv
ln -s "$DEV_PATH/.serena" .serena
ln -s "$DEV_PATH/.taskmaster" .taskmaster
ln -s "$DEV_PATH/.venv" .venv

# Create empty initial commit for the feature branch
# Note: .serena, .taskmaster, and .venv symlinks are NOT committed (they're in .gitignore)
echo -e "${BLUE}Creating initial commit...${NC}"
git commit --allow-empty -m "Initialize $BRANCH_FULL_NAME from dev"

# Push branch to GitHub
echo -e "${BLUE}Pushing branch to GitHub...${NC}"
git push -u origin "$BRANCH_FULL_NAME"

echo ""
echo -e "${GREEN}✓ Feature branch created and pushed successfully!${NC}"
echo ""
echo -e "${BLUE}Branch:${NC}   $BRANCH_FULL_NAME"
echo -e "${BLUE}Location:${NC} $WORKTREE_PATH"
echo -e "${BLUE}GitHub:${NC}   https://github.com/$(git config remote.origin.url | sed 's/.*://;s/\.git$//')/tree/$BRANCH_FULL_NAME"
echo ""
echo -e "${YELLOW}Note:${NC} .serena, .taskmaster, and .venv are symlinked to dev branch"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  cd $WORKTREE_PATH"
echo "  # Make your changes"
echo "  git add ."
echo "  git commit -m \"your message\""
echo "  git push"
echo ""
