#!/usr/bin/env bash

#######################################
# CodeRabbit Team Onboarding Script
# Automates complete setup for new team members
#######################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="${SCRIPT_DIR}/install-coderabbit-cli.sh"
AUTH_SCRIPT="${SCRIPT_DIR}/auth-setup.sh"

#######################################
# Helper Functions
#######################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}STEP $1${NC}"
    echo -e "${MAGENTA}========================================${NC}"
}

print_banner() {
    cat <<'EOF'
╔═══════════════════════════════════════════════════╗
║                                                   ║
║     CodeRabbit CLI - Team Onboarding Setup       ║
║                                                   ║
║     Welcome to KellerAI Development Team!        ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    # Check for required tools
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        missing_tools+=("curl or wget")
    fi

    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo "Please install these tools and run the script again."
        return 1
    fi

    log_success "All prerequisites met"
    return 0
}

run_installation() {
    log_step "1: Installing CodeRabbit CLI"

    if [[ ! -f "$INSTALL_SCRIPT" ]]; then
        log_error "Installation script not found: $INSTALL_SCRIPT"
        return 1
    fi

    if ! bash "$INSTALL_SCRIPT"; then
        log_error "Installation failed"
        return 1
    fi

    log_success "CLI installation complete"
    return 0
}

run_authentication() {
    log_step "2: Setting Up Authentication"

    if [[ ! -f "$AUTH_SCRIPT" ]]; then
        log_error "Authentication script not found: $AUTH_SCRIPT"
        return 1
    fi

    if ! bash "$AUTH_SCRIPT" setup; then
        log_error "Authentication setup failed"
        return 1
    fi

    log_success "Authentication setup complete"
    return 0
}

configure_git_integration() {
    log_step "3: Configuring Git Integration"

    echo ""
    read -p "Do you want to set up git hooks for automatic reviews? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping git hooks setup"
        return 0
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        log_warning "Not in a git repository. You can run 'coderabbit hooks install' later from your repo."
        return 0
    fi

    log_info "Installing git hooks..."

    if command -v coderabbit &> /dev/null; then
        if coderabbit hooks install; then
            log_success "Git hooks installed successfully"
        else
            log_warning "Failed to install git hooks. You can try again later with: coderabbit hooks install"
        fi
    else
        log_warning "CodeRabbit CLI not in PATH yet. Restart your shell and run: coderabbit hooks install"
    fi

    return 0
}

setup_editor_integration() {
    log_step "4: Editor Integration Setup"

    cat <<EOF

${CYAN}Editor Integration Options:${NC}

${BLUE}VS Code:${NC}
  Install the CodeRabbit extension from the marketplace:
  https://marketplace.visualstudio.com/items?itemName=coderabbit.coderabbit

${BLUE}Claude Code:${NC}
  Integration templates are available in the project docs.
  See: ${SCRIPT_DIR}/docs/claude-integration.md

${BLUE}Other Editors:${NC}
  Use the CLI directly or via git hooks for editor-agnostic reviews.

EOF

    read -p "Press Enter to continue..."
    return 0
}

verify_setup() {
    log_step "5: Verifying Setup"

    local verification_passed=true

    # Check CLI installation
    if command -v coderabbit &> /dev/null; then
        local version
        version=$(coderabbit --version 2>/dev/null || echo "unknown")
        log_success "CLI installed: version $version"
    else
        log_error "CLI not found in PATH"
        verification_passed=false
    fi

    # Check authentication
    if [[ -f "$AUTH_SCRIPT" ]]; then
        if bash "$AUTH_SCRIPT" status &> /dev/null; then
            log_success "Authentication configured"
        else
            log_warning "Authentication may not be configured correctly"
            verification_passed=false
        fi
    fi

    if [[ "$verification_passed" == "true" ]]; then
        log_success "All verifications passed!"
        return 0
    else
        log_warning "Some verifications failed. Please review the errors above."
        return 1
    fi
}

show_quick_start_guide() {
    log_step "6: Quick Start Guide"

    cat <<EOF

${GREEN}Congratulations! You're all set up!${NC}

${CYAN}Common Commands:${NC}

${BLUE}1. Review uncommitted changes:${NC}
   coderabbit review

${BLUE}2. Review a specific commit:${NC}
   coderabbit review --commit=HEAD

${BLUE}3. Review with specific configuration:${NC}
   coderabbit review --config=path/to/.coderabbit.yaml

${BLUE}4. Check authentication status:${NC}
   coderabbit auth status

${BLUE}5. Get help:${NC}
   coderabbit --help

${CYAN}Integration with Claude Code:${NC}

See documentation at: ${SCRIPT_DIR}/docs/claude-integration.md

${CYAN}Troubleshooting:${NC}

If you encounter issues:
1. Check authentication: bash ${AUTH_SCRIPT} status
2. Verify CLI version: coderabbit --version
3. See troubleshooting guide: ${SCRIPT_DIR}/docs/troubleshooting.md
4. Contact team lead or check internal wiki

${CYAN}Next Steps:${NC}

1. Navigate to a project repository
2. Run your first review: coderabbit review
3. Explore the configuration options in .coderabbit.yaml
4. Set up your preferred editor integration

${GREEN}Happy coding! 🚀${NC}

EOF
}

show_troubleshooting_help() {
    cat <<EOF

${RED}Setup Failed${NC}

${YELLOW}Common Issues and Solutions:${NC}

${BLUE}1. CLI not found after installation:${NC}
   - Restart your terminal or shell
   - Run: source ~/.bashrc (or ~/.zshrc)
   - Verify PATH: echo \$PATH | grep -i ".local/bin"

${BLUE}2. Authentication failed:${NC}
   - Verify you have a valid API token from https://app.coderabbit.ai
   - Re-run: bash ${AUTH_SCRIPT} setup
   - Check token permissions in CodeRabbit web interface

${BLUE}3. Permission denied errors:${NC}
   - Ensure scripts are executable: chmod +x ${INSTALL_SCRIPT} ${AUTH_SCRIPT}
   - Check directory permissions: ls -la ${SCRIPT_DIR}

${BLUE}4. Network/download errors:${NC}
   - Check internet connection
   - Try alternative download method (curl vs wget)
   - Check corporate proxy settings

${CYAN}For additional help:${NC}
   - See full documentation: ${SCRIPT_DIR}/docs/
   - Contact team lead
   - Create internal support ticket

EOF
}

cleanup_on_failure() {
    log_warning "Cleaning up partial installation..."
    # Add cleanup logic if needed
    log_info "You can retry the setup by running this script again."
}

#######################################
# Main Onboarding Flow
#######################################

main() {
    print_banner

    echo ""
    log_info "This script will guide you through setting up CodeRabbit CLI for the team."
    echo ""
    read -p "Press Enter to begin, or Ctrl+C to cancel..."

    # Step 1: Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    # Step 2: Run installation
    if ! run_installation; then
        log_error "Installation failed"
        show_troubleshooting_help
        cleanup_on_failure
        exit 1
    fi

    # Step 3: Set up authentication
    if ! run_authentication; then
        log_error "Authentication setup failed"
        show_troubleshooting_help
        cleanup_on_failure
        exit 1
    fi

    # Step 4: Configure git integration (optional)
    configure_git_integration || true

    # Step 5: Show editor integration options
    setup_editor_integration || true

    # Step 6: Verify setup
    verify_setup || true

    # Step 7: Show quick start guide
    show_quick_start_guide

    log_success "Onboarding complete! Welcome to the team! 🎉"
    exit 0
}

# Handle script interruption
trap 'echo ""; log_warning "Setup interrupted by user"; cleanup_on_failure; exit 130' INT TERM

# Run main function
main "$@"
