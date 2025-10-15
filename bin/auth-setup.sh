#!/usr/bin/env bash

#######################################
# CodeRabbit CLI Authentication Setup
# Features: Token generation, secure storage, validation
#######################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
CONFIG_DIR="${HOME}/.config/coderabbit"
TOKEN_FILE="${CONFIG_DIR}/token"
CONFIG_FILE="${CONFIG_DIR}/config.json"
CODERABBIT_WEB_URL="https://app.coderabbit.ai"
CODERABBIT_API_URL="https://api.coderabbit.ai"

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
    echo -e "${CYAN}[STEP]${NC} $1"
}

ensure_config_dir() {
    if [[ ! -d "$CONFIG_DIR" ]]; then
        log_info "Creating configuration directory: $CONFIG_DIR"
        mkdir -p "$CONFIG_DIR"
        chmod 700 "$CONFIG_DIR"
    fi
}

check_keychain_availability() {
    # Check if we can use system keychain (macOS)
    if [[ "$(uname)" == "Darwin" ]]; then
        return 0
    fi
    # Check for secret-tool (GNOME Keyring on Linux)
    if command -v secret-tool &> /dev/null; then
        return 0
    fi
    return 1
}

store_token_keychain_macos() {
    local token="$1"
    security add-generic-password \
        -a "$USER" \
        -s "coderabbit-cli" \
        -w "$token" \
        -U 2>/dev/null || \
    security add-generic-password \
        -a "$USER" \
        -s "coderabbit-cli" \
        -w "$token"
}

retrieve_token_keychain_macos() {
    security find-generic-password \
        -a "$USER" \
        -s "coderabbit-cli" \
        -w 2>/dev/null || echo ""
}

store_token_keychain_linux() {
    local token="$1"
    echo -n "$token" | secret-tool store \
        --label="CodeRabbit CLI Token" \
        application coderabbit \
        user "$USER"
}

retrieve_token_keychain_linux() {
    secret-tool lookup \
        application coderabbit \
        user "$USER" 2>/dev/null || echo ""
}

store_token_secure() {
    local token="$1"

    if check_keychain_availability; then
        log_info "Storing token in system keychain..."
        if [[ "$(uname)" == "Darwin" ]]; then
            if store_token_keychain_macos "$token"; then
                log_success "Token stored securely in macOS Keychain"
                return 0
            fi
        else
            if store_token_keychain_linux "$token"; then
                log_success "Token stored securely in GNOME Keyring"
                return 0
            fi
        fi
    fi

    # Fallback to file storage with restricted permissions
    log_warning "Keychain not available, using file storage"
    echo "$token" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    log_success "Token stored in: $TOKEN_FILE (with restricted permissions)"
}

retrieve_token() {
    local token=""

    # Try keychain first
    if check_keychain_availability; then
        if [[ "$(uname)" == "Darwin" ]]; then
            token=$(retrieve_token_keychain_macos)
        else
            token=$(retrieve_token_keychain_linux)
        fi
    fi

    # Fallback to file storage
    if [[ -z "$token" ]] && [[ -f "$TOKEN_FILE" ]]; then
        token=$(cat "$TOKEN_FILE")
    fi

    echo "$token"
}

validate_token_format() {
    local token="$1"

    # Basic validation - CodeRabbit tokens should be non-empty
    if [[ -z "$token" ]]; then
        return 1
    fi

    # Check for minimum length (adjust based on actual token format)
    if [[ ${#token} -lt 20 ]]; then
        return 1
    fi

    return 0
}

validate_token_api() {
    local token="$1"

    log_info "Validating token with CodeRabbit API..."

    # Test API call to validate token
    local response
    local http_code

    if command -v curl &> /dev/null; then
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            "${CODERABBIT_API_URL}/v1/user" 2>/dev/null || echo "000")
        http_code=$(echo "$response" | tail -n1)
    else
        log_error "curl is required for API validation"
        return 1
    fi

    if [[ "$http_code" == "200" ]]; then
        log_success "Token validated successfully"
        return 0
    elif [[ "$http_code" == "401" ]]; then
        log_error "Token validation failed: Unauthorized"
        return 1
    else
        log_warning "Could not validate token (HTTP $http_code)"
        log_info "Token format appears valid, continuing..."
        return 0
    fi
}

generate_token_instructions() {
    echo ""
    echo "=========================================="
    echo "How to Generate a CodeRabbit API Token"
    echo "=========================================="
    echo ""
    echo "1. Open your browser and navigate to:"
    echo "   ${CYAN}${CODERABBIT_WEB_URL}/settings/api-tokens${NC}"
    echo ""
    echo "2. Log in to your CodeRabbit account"
    echo ""
    echo "3. Click 'Generate New Token' button"
    echo ""
    echo "4. Give your token a descriptive name (e.g., 'Development Machine')"
    echo ""
    echo "5. Copy the generated token (you won't see it again!)"
    echo ""
    echo "6. Return to this terminal and paste the token when prompted"
    echo ""
    echo "=========================================="
}

prompt_for_token() {
    echo ""
    read -s -p "Enter your CodeRabbit API token: " -r token
    echo ""

    if [[ -z "$token" ]]; then
        log_error "Token cannot be empty"
        return 1
    fi

    echo "$token"
}

save_config() {
    local token="$1"

    cat > "$CONFIG_FILE" <<EOF
{
  "api_url": "${CODERABBIT_API_URL}",
  "web_url": "${CODERABBIT_WEB_URL}",
  "token_storage": "$(check_keychain_availability && echo 'keychain' || echo 'file')",
  "configured_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "user": "$USER"
}
EOF
    chmod 600 "$CONFIG_FILE"
}

show_status() {
    echo ""
    echo "=========================================="
    echo "CodeRabbit CLI Authentication Status"
    echo "=========================================="

    if [[ -f "$CONFIG_FILE" ]]; then
        log_success "Configuration file exists: $CONFIG_FILE"
    else
        log_warning "Configuration file not found"
    fi

    local token
    token=$(retrieve_token)

    if [[ -n "$token" ]]; then
        log_success "API token found"
        local token_preview="${token:0:8}...${token: -4}"
        echo "   Token preview: $token_preview"

        if validate_token_format "$token"; then
            log_success "Token format is valid"
        else
            log_error "Token format appears invalid"
        fi
    else
        log_error "No API token found"
        echo "   Run: $0 setup"
    fi

    echo "=========================================="
}

setup_authentication() {
    log_step "Starting CodeRabbit CLI authentication setup"

    # Check if token already exists
    local existing_token
    existing_token=$(retrieve_token)

    if [[ -n "$existing_token" ]]; then
        log_warning "Existing authentication found"
        read -p "Do you want to reconfigure? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Setup cancelled"
            return 0
        fi
    fi

    # Show instructions
    generate_token_instructions

    # Prompt for token
    local token
    if ! token=$(prompt_for_token); then
        log_error "Token input failed"
        return 1
    fi

    # Validate token format
    if ! validate_token_format "$token"; then
        log_error "Token format appears invalid"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi

    # Store token
    if ! store_token_secure "$token"; then
        log_error "Failed to store token"
        return 1
    fi

    # Validate with API (optional)
    validate_token_api "$token" || true

    # Save configuration
    save_config "$token"

    log_success "Authentication setup complete!"

    # Show next steps
    show_next_steps
}

revoke_authentication() {
    log_step "Revoking CodeRabbit CLI authentication"

    read -p "Are you sure you want to remove authentication? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Revocation cancelled"
        return 0
    fi

    # Remove from keychain
    if [[ "$(uname)" == "Darwin" ]]; then
        security delete-generic-password \
            -a "$USER" \
            -s "coderabbit-cli" 2>/dev/null || true
    elif command -v secret-tool &> /dev/null; then
        secret-tool clear \
            application coderabbit \
            user "$USER" 2>/dev/null || true
    fi

    # Remove files
    rm -f "$TOKEN_FILE"
    rm -f "$CONFIG_FILE"

    log_success "Authentication removed"
    log_info "To set up again, run: $0 setup"
}

show_next_steps() {
    echo ""
    echo "=========================================="
    echo "Next Steps:"
    echo "=========================================="
    echo "1. Verify your setup:"
    echo "   coderabbit auth status"
    echo ""
    echo "2. Initialize in your repository:"
    echo "   cd /path/to/your/repo"
    echo "   coderabbit init"
    echo ""
    echo "3. Run a code review:"
    echo "   coderabbit review"
    echo ""
    echo "4. Or use with git hooks:"
    echo "   coderabbit hooks install"
    echo "=========================================="
}

show_usage() {
    cat <<EOF
Usage: $0 <command>

Commands:
  setup     Set up CodeRabbit CLI authentication
  status    Show current authentication status
  revoke    Remove authentication credentials
  test      Test API connection
  help      Show this help message

Examples:
  $0 setup      # First-time setup or reconfigure
  $0 status     # Check if authentication is working
  $0 revoke     # Remove stored credentials

EOF
}

#######################################
# Main Function
#######################################

main() {
    ensure_config_dir

    local command="${1:-help}"

    case "$command" in
        setup)
            setup_authentication
            ;;
        status)
            show_status
            ;;
        revoke)
            revoke_authentication
            ;;
        test)
            local token
            token=$(retrieve_token)
            if [[ -n "$token" ]]; then
                validate_token_api "$token"
            else
                log_error "No token found. Run: $0 setup"
                exit 1
            fi
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
