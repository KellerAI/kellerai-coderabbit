#!/usr/bin/env bash

#######################################
# CodeRabbit CLI Installation Script
# Supports: macOS, Linux (Ubuntu/Debian, RHEL/CentOS/Fedora)
# Features: Idempotent, OS detection, PATH configuration
#######################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${HOME}/.local/bin"
CLI_NAME="coderabbit"
DOWNLOAD_BASE_URL="https://github.com/coderabbitai/coderabbit-cli/releases/latest/download"
BACKUP_DOWNLOAD_METHOD="wget"

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

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unsupported"
    fi
}

detect_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
        x86_64|amd64)
            echo "x64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        *)
            echo "unsupported"
            ;;
    esac
}

check_existing_installation() {
    if command -v coderabbit &> /dev/null; then
        local version
        version=$(coderabbit --version 2>/dev/null || echo "unknown")
        log_warning "CodeRabbit CLI is already installed (version: ${version})"
        read -p "Do you want to reinstall? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled by user"
            exit 0
        fi
        return 0
    fi
    return 1
}

ensure_install_dir() {
    if [[ ! -d "$INSTALL_DIR" ]]; then
        log_info "Creating installation directory: $INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
    fi
}

download_cli() {
    local os="$1"
    local arch="$2"
    local temp_file
    temp_file=$(mktemp)

    # Determine the correct binary name based on OS and architecture
    local binary_name
    if [[ "$os" == "macos" ]]; then
        if [[ "$arch" == "arm64" ]]; then
            binary_name="coderabbit-macos-arm64"
        else
            binary_name="coderabbit-macos-x64"
        fi
    elif [[ "$os" == "linux" ]]; then
        if [[ "$arch" == "arm64" ]]; then
            binary_name="coderabbit-linux-arm64"
        else
            binary_name="coderabbit-linux-x64"
        fi
    fi

    local download_url="${DOWNLOAD_BASE_URL}/${binary_name}"

    log_info "Downloading CodeRabbit CLI from: $download_url"

    # Try curl first, fallback to wget
    if command -v curl &> /dev/null; then
        if ! curl -fsSL -o "$temp_file" "$download_url"; then
            log_error "Download failed with curl"
            rm -f "$temp_file"
            return 1
        fi
    elif command -v wget &> /dev/null; then
        if ! wget -q -O "$temp_file" "$download_url"; then
            log_error "Download failed with wget"
            rm -f "$temp_file"
            return 1
        fi
    else
        log_error "Neither curl nor wget found. Please install one of them."
        rm -f "$temp_file"
        return 1
    fi

    echo "$temp_file"
}

install_binary() {
    local temp_file="$1"
    local install_path="${INSTALL_DIR}/${CLI_NAME}"

    log_info "Installing binary to: $install_path"

    # Backup existing installation if present
    if [[ -f "$install_path" ]]; then
        local backup_path="${install_path}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "Backing up existing installation to: $backup_path"
        mv "$install_path" "$backup_path"
    fi

    # Move and make executable
    mv "$temp_file" "$install_path"
    chmod +x "$install_path"

    log_success "Binary installed successfully"
}

configure_path() {
    local shell_config

    # Detect shell configuration file
    if [[ -n "${BASH_VERSION:-}" ]]; then
        if [[ -f "${HOME}/.bashrc" ]]; then
            shell_config="${HOME}/.bashrc"
        elif [[ -f "${HOME}/.bash_profile" ]]; then
            shell_config="${HOME}/.bash_profile"
        fi
    elif [[ -n "${ZSH_VERSION:-}" ]]; then
        shell_config="${HOME}/.zshrc"
    elif [[ -f "${HOME}/.profile" ]]; then
        shell_config="${HOME}/.profile"
    fi

    if [[ -z "${shell_config:-}" ]]; then
        log_warning "Could not detect shell configuration file"
        log_info "Please add the following to your shell configuration manually:"
        echo "    export PATH=\"\$PATH:${INSTALL_DIR}\""
        return 1
    fi

    # Check if PATH is already configured
    if grep -qE "^\s*export PATH=.*${INSTALL_DIR}" "$shell_config" 2>/dev/null; then
        log_info "PATH already configured in $shell_config"
        return 0
    fi

    # Add PATH configuration
    log_info "Adding ${INSTALL_DIR} to PATH in $shell_config"
    echo "" >> "$shell_config"
    echo "# CodeRabbit CLI" >> "$shell_config"
    echo "export PATH=\"\$PATH:${INSTALL_DIR}\"" >> "$shell_config"

    log_success "PATH configured successfully"
    log_warning "Please restart your shell or run: source $shell_config"
}

verify_installation() {
    log_info "Verifying installation..."

    # Add to current PATH for verification
    export PATH="$PATH:${INSTALL_DIR}"

    if ! command -v coderabbit &> /dev/null; then
        log_error "Installation verification failed - coderabbit command not found"
        log_info "You may need to restart your shell or run: export PATH=\"\$PATH:${INSTALL_DIR}\""
        return 1
    fi

    local version
    version=$(coderabbit --version 2>/dev/null || echo "unknown")
    log_success "CodeRabbit CLI installed successfully (version: ${version})"

    return 0
}

show_next_steps() {
    echo ""
    echo "=========================================="
    echo "Next Steps:"
    echo "=========================================="
    echo "1. Restart your shell or run:"
    echo "   source ~/.bashrc  (or ~/.zshrc, ~/.bash_profile)"
    echo ""
    echo "2. Set up authentication:"
    echo "   coderabbit auth login"
    echo ""
    echo "3. Configure your repository:"
    echo "   cd /path/to/your/repo"
    echo "   coderabbit init"
    echo ""
    echo "4. Run your first review:"
    echo "   coderabbit review"
    echo ""
    echo "5. See all available commands:"
    echo "   coderabbit --help"
    echo "=========================================="
}

#######################################
# Main Installation Flow
#######################################

main() {
    log_info "Starting CodeRabbit CLI installation..."

    # Detect OS and architecture
    local os
    os=$(detect_os)
    if [[ "$os" == "unsupported" ]]; then
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    log_info "Detected OS: $os"

    local arch
    arch=$(detect_arch)
    if [[ "$arch" == "unsupported" ]]; then
        log_error "Unsupported architecture: $(uname -m)"
        exit 1
    fi
    log_info "Detected architecture: $arch"

    # Check for existing installation
    check_existing_installation || true

    # Ensure installation directory exists
    ensure_install_dir

    # Download CLI binary
    local temp_file
    if ! temp_file=$(download_cli "$os" "$arch"); then
        log_error "Failed to download CodeRabbit CLI"
        exit 1
    fi

    # Install binary
    if ! install_binary "$temp_file"; then
        log_error "Failed to install CodeRabbit CLI"
        exit 1
    fi

    # Configure PATH
    configure_path || true

    # Verify installation
    if verify_installation; then
        show_next_steps
        exit 0
    else
        log_warning "Installation completed but verification failed"
        log_info "Please check your PATH configuration"
        exit 1
    fi
}

# Run main function
main "$@"
