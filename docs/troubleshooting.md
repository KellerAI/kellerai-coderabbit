# CodeRabbit CLI Troubleshooting Guide

Comprehensive guide for resolving common issues with CodeRabbit CLI installation, authentication, and usage.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [Review Command Failures](#review-command-failures)
- [Git Integration Issues](#git-integration-issues)
- [Performance Problems](#performance-problems)
- [Configuration Errors](#configuration-errors)
- [Network and API Issues](#network-and-api-issues)
- [Platform-Specific Problems](#platform-specific-problems)
- [Debug Mode](#debug-mode)

---

## Installation Issues

### Issue: CLI Not Found After Installation

**Symptoms:**
```bash
$ coderabbit --version
bash: coderabbit: command not found
```

**Causes:**
- CLI binary not in PATH
- Installation directory not accessible
- Shell configuration not reloaded

**Solutions:**

1. **Check if binary exists:**
   ```bash
   ls -la ~/.local/bin/coderabbit
   ```

2. **Add to PATH manually:**
   ```bash
   # For bash
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
   source ~/.bashrc

   # For zsh
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Verify PATH configuration:**
   ```bash
   echo $PATH | grep -i ".local/bin"
   ```

4. **Try absolute path:**
   ```bash
   ~/.local/bin/coderabbit --version
   ```

5. **Reinstall:**
   ```bash
   bash install-coderabbit-cli.sh
   ```

---

### Issue: Permission Denied During Installation

**Symptoms:**
```bash
$ bash install-coderabbit-cli.sh
bash: ./install-coderabbit-cli.sh: Permission denied
```

**Solutions:**

1. **Make script executable:**
   ```bash
   chmod +x install-coderabbit-cli.sh
   bash install-coderabbit-cli.sh
   ```

2. **Run with bash explicitly:**
   ```bash
   bash install-coderabbit-cli.sh
   ```

3. **Check directory permissions:**
   ```bash
   ls -la ~/.local/bin
   # If directory doesn't exist or has wrong permissions:
   mkdir -p ~/.local/bin
   chmod 755 ~/.local/bin
   ```

---

### Issue: Download Fails During Installation

**Symptoms:**
```bash
Failed to download CodeRabbit CLI
curl: (6) Could not resolve host
```

**Causes:**
- Network connectivity issues
- Corporate proxy blocking downloads
- GitHub rate limiting
- DNS resolution problems

**Solutions:**

1. **Check internet connectivity:**
   ```bash
   ping github.com
   curl -I https://github.com
   ```

2. **Try alternative download method:**
   ```bash
   # If curl fails, try wget
   wget https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-macos-arm64
   ```

3. **Configure proxy (if behind corporate firewall):**
   ```bash
   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="http://proxy.company.com:8080"
   bash install-coderabbit-cli.sh
   ```

4. **Manual download and install:**
   ```bash
   # Download from browser
   # Then move to correct location:
   mv ~/Downloads/coderabbit-macos-arm64 ~/.local/bin/coderabbit
   chmod +x ~/.local/bin/coderabbit
   ```

5. **Check GitHub status:**
   ```bash
   curl -s https://www.githubstatus.com/api/v2/status.json
   ```

---

### Issue: Wrong Architecture Binary

**Symptoms:**
```bash
$ coderabbit --version
-bash: /Users/user/.local/bin/coderabbit: Bad CPU type in executable
```

**Causes:**
- Installed x64 binary on ARM Mac (or vice versa)
- Wrong Linux architecture

**Solutions:**

1. **Check your system architecture:**
   ```bash
   uname -m
   # arm64/aarch64 = ARM
   # x86_64/amd64 = Intel/AMD
   ```

2. **Remove incorrect binary:**
   ```bash
   rm ~/.local/bin/coderabbit
   ```

3. **Reinstall with correct architecture:**
   ```bash
   # The installation script should detect correctly
   bash install-coderabbit-cli.sh
   ```

4. **Manual install with correct binary:**
   ```bash
   # For Apple Silicon Mac
   curl -fsSL https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-macos-arm64 -o ~/.local/bin/coderabbit

   # For Intel Mac
   curl -fsSL https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-macos-x64 -o ~/.local/bin/coderabbit

   chmod +x ~/.local/bin/coderabbit
   ```

---

## Authentication Problems

### Issue: Authentication Fails with "Invalid Token"

**Symptoms:**
```bash
$ coderabbit review
Error: Invalid API token
```

**Causes:**
- Token expired or revoked
- Incorrect token entered
- Token not properly stored
- Token corrupted in keychain

**Solutions:**

1. **Check authentication status:**
   ```bash
   bash auth-setup.sh status
   ```

2. **Regenerate token:**
   - Visit https://app.coderabbit.ai/settings/api-tokens
   - Revoke old token
   - Generate new token
   - Copy immediately

3. **Re-authenticate:**
   ```bash
   bash auth-setup.sh revoke
   bash auth-setup.sh setup
   ```

4. **Verify token format:**
   ```bash
   # Token should be 40+ characters, alphanumeric
   # Check stored token (if using file storage)
   cat ~/.config/coderabbit/token
   ```

5. **Test token directly:**
   ```bash
   bash auth-setup.sh test
   ```

---

### Issue: "No Token Found" Error

**Symptoms:**
```bash
$ coderabbit review
Error: No authentication token found
```

**Causes:**
- Authentication not set up
- Token file deleted
- Keychain access denied

**Solutions:**

1. **Run authentication setup:**
   ```bash
   bash auth-setup.sh setup
   ```

2. **Check if token file exists:**
   ```bash
   ls -la ~/.config/coderabbit/token
   ```

3. **Check keychain (macOS):**
   ```bash
   security find-generic-password -s "coderabbit-cli" -a "$USER"
   ```

4. **Grant keychain access (macOS):**
   - Open Keychain Access app
   - Search for "coderabbit-cli"
   - Right-click > Get Info
   - Access Control tab
   - Add `coderabbit` to allowed applications

5. **Use environment variable as fallback:**
   
   ⚠️ **WARNING**: Using `export` will store the token in shell history and make it visible in process listings. Use one of these secure alternatives:
   
   ```bash
   # Option 1: Prefix with space to avoid shell history (bash/zsh with HISTCONTROL=ignorespace)
    export CODERABBIT_API_TOKEN="your-token-here"
   
   # Option 2: Read from credential manager (recommended)
   export CODERABBIT_API_TOKEN=$(security find-generic-password -s "coderabbit-cli" -w)
   
   # Option 3: Read from secure file with restricted permissions
   export CODERABBIT_API_TOKEN=$(cat ~/.config/coderabbit/token)
   
   coderabbit review
   ```

---

### Issue: Keychain Access Denied (macOS)

**Symptoms:**
```bash
The operation couldn't be completed. (OSStatus error -25293.)
```

**Solutions:**

1. **Reset keychain permissions:**
   ```bash
   security delete-generic-password -s "coderabbit-cli" -a "$USER"
   bash auth-setup.sh setup
   ```

2. **Allow access when prompted:**
   - When macOS asks for keychain access, click "Always Allow"

3. **Use file-based storage instead:**
   ```bash
   # Edit auth-setup.sh or use fallback:
   mkdir -p ~/.config/coderabbit
   echo "your-token" > ~/.config/coderabbit/token
   chmod 600 ~/.config/coderabbit/token
   ```

---

### Issue: Token Works in Browser But Not CLI

**Causes:**
- Different API endpoints
- Token scopes insufficient
- CLI using cached expired token

**Solutions:**

1. **Check API endpoints:**
   ```bash
   cat ~/.config/coderabbit/config.json
   # Should show: "api_url": "https://api.coderabbit.ai"
   ```

2. **Clear cached credentials:**
   ```bash
   bash auth-setup.sh revoke
   rm -rf ~/.config/coderabbit
   bash auth-setup.sh setup
   ```

3. **Verify token scopes:**
   - In CodeRabbit web UI, check token has "CLI Access" scope
   - Regenerate with correct scopes if needed

4. **Test API directly:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.coderabbit.ai/v1/user
   ```

---

## Review Command Failures

### Issue: "No Changes to Review"

**Symptoms:**
```bash
$ coderabbit review
No changes detected
```

**Causes:**
- No uncommitted changes
- All changes already committed
- Changes in ignored files

**Solutions:**

1. **Check git status:**
   ```bash
   git status
   git diff
   ```

2. **Review specific commit:**
   ```bash
   coderabbit review --commit=HEAD
   ```

3. **Review staged changes:**
   ```bash
   git add .
   coderabbit review
   ```

4. **Check ignore patterns:**
   ```bash
   cat .coderabbit.yaml | grep -A 10 ignore
   ```

---

### Issue: Review Times Out

**Symptoms:**
```bash
$ coderabbit review
Error: Request timeout after 60 seconds
```

**Causes:**
- Large changeset
- Slow network connection
- API overload
- Complex analysis

**Solutions:**

1. **Review smaller chunks:**
   ```bash
   # Review specific files
   coderabbit review --file=src/main.py

   # Review by directory
   coderabbit review --file=src/*.py
   ```

2. **Increase timeout:**
   ```bash
   export CODERABBIT_TIMEOUT=300  # 5 minutes
   coderabbit review
   ```

3. **Use fast mode:**
   ```bash
   coderabbit review --fast
   ```

4. **Split into multiple reviews:**
   ```bash
   # Review each commit separately
   git log --pretty=format:"%H" HEAD~5..HEAD | while read commit; do
       coderabbit review --commit=$commit
   done
   ```

---

### Issue: "Failed to Parse JSON Output"

**Symptoms:**
```bash
Error: Invalid JSON response from API
```

**Solutions:**

1. **Check API status:**
   ```bash
   curl https://status.coderabbit.ai
   ```

2. **Verify token is valid:**
   ```bash
   bash auth-setup.sh test
   ```

3. **Try without JSON output:**
   ```bash
   coderabbit review --output=pretty
   ```

4. **Check for API changes:**
   ```bash
   coderabbit --version
   # Update if outdated:
   bash install-coderabbit-cli.sh
   ```

5. **Enable debug mode:**
   ```bash
   CODERABBIT_DEBUG=1 coderabbit review
   ```

---

### Issue: Review Shows Incorrect Line Numbers

**Causes:**
- File changed between review request and display
- CRLF vs LF line endings
- Review based on cached version

**Solutions:**

1. **Ensure no concurrent changes:**
   ```bash
   # Commit or stash other changes first
   git stash
   coderabbit review
   git stash pop
   ```

2. **Normalize line endings:**
   ```bash
   git config core.autocrlf input
   git add --renormalize .
   ```

3. **Clear cache and retry:**
   ```bash
   coderabbit review --no-cache
   ```

---

## Git Integration Issues

### Issue: Git Hooks Not Working

**Symptoms:**
- Commits succeed without review
- Pre-commit hook doesn't run

**Solutions:**

1. **Check if hooks are installed:**
   ```bash
   ls -la .git/hooks/
   # Should see: pre-commit, pre-push
   ```

2. **Verify hook is executable:**
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. **Test hook manually:**
   ```bash
   .git/hooks/pre-commit
   ```

4. **Reinstall hooks:**
   ```bash
   coderabbit hooks uninstall
   coderabbit hooks install
   ```

5. **Check for hook conflicts:**
   ```bash
   cat .git/hooks/pre-commit
   # Ensure CodeRabbit hook is present and not overwritten
   ```

6. **Verify PATH in hook:**
   ```bash
   # Git hooks may not have full PATH
   # Edit .git/hooks/pre-commit and add:
   export PATH="$PATH:$HOME/.local/bin"
   ```

---

### Issue: "--no-verify" Bypasses Reviews

**Not an issue** - This is intentional git behavior.

**If you want to enforce reviews:**

1. **Use server-side hooks (GitHub Actions):**
   ```yaml
   # .github/workflows/coderabbit.yml
   on: [pull_request]
   jobs:
     review:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Review
           run: |
             curl -fsSL https://install.coderabbit.ai | bash
             coderabbit review
   ```

2. **Protect branches:**
   - GitHub Settings > Branches
   - Enable "Require status checks"
   - Add CodeRabbit check

---

### Issue: Hook Fails in GUI Git Clients

**Causes:**
- GUI clients use limited environment
- PATH not set correctly
- Different shell environment

**Solutions:**

1. **Use absolute paths in hooks:**
   ```bash
   #!/bin/bash
   # .git/hooks/pre-commit

   export PATH="$PATH:$HOME/.local/bin"

   if [ -x "$HOME/.local/bin/coderabbit" ]; then
       "$HOME/.local/bin/coderabbit" review
   else
       echo "CodeRabbit CLI not found"
       exit 1
   fi
   ```

2. **Test with GUI client:**
   - Make a test commit in GUI
   - Check terminal for error messages

3. **Use SourceTree/Tower specific configs:**
   - Check GUI client's hook configuration
   - May need to specify interpreter

---

## Performance Problems

### Issue: Reviews Are Very Slow

**Symptoms:**
- Reviews take 2+ minutes
- CLI appears to hang

**Solutions:**

1. **Review smaller changesets:**
   ```bash
   # Instead of reviewing all changes
   coderabbit review --file=src/specific-file.py
   ```

2. **Use fast mode:**
   ```bash
   coderabbit review --fast
   ```

3. **Skip expensive checks:**
   ```bash
   coderabbit review --skip=complexity,performance
   ```

4. **Check network latency:**
   ```bash
   ping api.coderabbit.ai
   # If high latency, consider:
   # - VPN if behind restrictive firewall
   # - Different network connection
   ```

5. **Parallelize multiple file reviews:**
   ```bash
   # Review files in parallel
   for file in src/*.py; do
       coderabbit review --file="$file" &
   done
   wait
   ```

---

### Issue: High Memory Usage

**Solutions:**

1. **Review in chunks:**
   ```bash
   # Limit files per review
   git diff --name-only | split -l 10 - files_to_review_
   for chunk in files_to_review_*; do
       cat $chunk | xargs coderabbit review --file
   done
   ```

2. **Clear cache:**
   ```bash
   rm -rf ~/.cache/coderabbit
   ```

3. **Update CLI:**
   ```bash
   bash install-coderabbit-cli.sh
   ```

---

## Configuration Errors

### Issue: "Invalid Configuration File"

**Symptoms:**
```bash
Error: Failed to parse .coderabbit.yaml
```

**Solutions:**

1. **Validate YAML syntax:**
   ```bash
   # Install yamllint if needed
   yamllint .coderabbit.yaml
   ```

2. **Check for common YAML errors:**
   - Inconsistent indentation (use spaces, not tabs)
   - Missing colons
   - Incorrect list formatting

3. **Use online YAML validator:**
   - Copy content to https://www.yamllint.com/

4. **Start with minimal config:**
   ```yaml
   profile: chill
   auto_review: true
   ```

5. **Use CLI to validate:**
   ```bash
   coderabbit config validate
   ```

---

### Issue: Configuration Not Applied

**Symptoms:**
- Changed config but reviews unchanged
- Custom rules ignored

**Solutions:**

1. **Verify config location:**
   ```bash
   # Should be in repository root
   ls -la .coderabbit.yaml
   ```

2. **Check config loading:**
   ```bash
   coderabbit config show
   # Should show your custom settings
   ```

3. **Force config reload:**
   ```bash
   coderabbit review --config=.coderabbit.yaml
   ```

4. **Clear cache:**
   ```bash
   rm -rf ~/.cache/coderabbit/config
   ```

5. **Check for typos in config:**
   ```bash
   # Compare with example config
   cat .coderabbit.yaml
   ```

---

### Issue: Ignore Patterns Not Working

**Solutions:**

1. **Verify ignore syntax:**
   ```yaml
   ignore:
     - "*.min.js"        # Correct
     - "dist/**"         # Correct
     - "node_modules/**" # Correct
     # NOT: ignore: "*.min.js"  (Incorrect - should be list)
   ```

2. **Test ignore patterns:**
   ```bash
   # Check which files are being reviewed
   coderabbit review --verbose | grep "Reviewing:"
   ```

3. **Use .coderabbitignore file:**
   ```bash
   # Create .coderabbitignore (like .gitignore)
   echo "dist/" >> .coderabbitignore
   echo "*.min.js" >> .coderabbitignore
   ```

---

## Network and API Issues

### Issue: "Connection Refused"

**Solutions:**

1. **Check API endpoint:**
   ```bash
   curl https://api.coderabbit.ai/health
   ```

2. **Check firewall:**
   ```bash
   # Try with explicit proxy
   export HTTPS_PROXY="http://proxy:port"
   coderabbit review
   ```

3. **Check DNS resolution:**
   ```bash
   nslookup api.coderabbit.ai
   # Should resolve to valid IP
   ```

4. **Try alternative network:**
   - Mobile hotspot
   - Different WiFi
   - VPN

---

### Issue: SSL Certificate Errors

**Symptoms:**
```bash
Error: SSL certificate verification failed
```

**Solutions:**

1. **Update CA certificates:**
   ```bash
   # macOS
   brew install ca-certificates

   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install ca-certificates

   # RHEL/CentOS
   sudo yum install ca-certificates
   ```

2. **Temporary bypass (NOT RECOMMENDED for production):**
   ```bash
   export CODERABBIT_SKIP_SSL_VERIFY=1
   coderabbit review
   ```

3. **Check system time:**
   ```bash
   date
   # Incorrect system time causes SSL errors
   ```

4. **Use corporate CA bundle:**
   ```bash
   export REQUESTS_CA_BUNDLE=/path/to/corporate-ca-bundle.crt
   ```

---

### Issue: Rate Limiting

**Symptoms:**
```bash
Error: Rate limit exceeded. Retry after 60 seconds
```

**Solutions:**

1. **Wait and retry:**
   ```bash
   sleep 60
   coderabbit review
   ```

2. **Reduce review frequency:**
   - Review less often
   - Batch changes before reviewing

3. **Contact support for higher limits:**
   - If you have enterprise plan
   - Provide usage justification

4. **Use caching:**
   ```bash
   # CLI should cache results automatically
   coderabbit review --use-cache
   ```

---

## Platform-Specific Problems

### macOS: "App Can't Be Opened Because It Is From an Unidentified Developer"

**Solutions:**

1. **Allow the app:**
   ```bash
   xattr -d com.apple.quarantine ~/.local/bin/coderabbit
   ```

2. **System Settings approach:**
   - Open System Settings
   - Security & Privacy
   - Click "Allow" for coderabbit

3. **Alternative:**
   ```bash
   # Remove extended attributes
   xattr -c ~/.local/bin/coderabbit
   ```

---

### Linux: "Cannot Execute Binary File"

**Solutions:**

1. **Check if you have x86_64 binary on ARM system:**
   ```bash
   file ~/.local/bin/coderabbit
   # Should match your architecture
   ```

2. **Reinstall correct binary:**
   ```bash
   rm ~/.local/bin/coderabbit
   bash install-coderabbit-cli.sh
   ```

3. **Install missing libraries:**
   ```bash
   # Check for missing dependencies
   ldd ~/.local/bin/coderabbit

   # Install missing libraries
   sudo apt-get install libc6
   ```

---

### Windows WSL: Path Issues

**Solutions:**

1. **Use Linux-style paths:**
   ```bash
   # Not: C:\Users\...
   # Use: /mnt/c/Users/...
   ```

2. **Set PATH in WSL:**
   ```bash
   echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bashrc
   ```

3. **Use WSL-compatible tools:**
   ```bash
   # Ensure git is WSL version, not Windows version
   which git
   # Should show: /usr/bin/git (not /mnt/c/...)
   ```

---

## Debug Mode

### Enable Comprehensive Debugging

```bash
# Enable all debug output
export CODERABBIT_DEBUG=1
export CODERABBIT_VERBOSE=1

# Run command
coderabbit review

# Save debug output
coderabbit review 2>&1 | tee debug.log
```

### Check Versions

```bash
coderabbit --version
bash --version
git --version
curl --version
python --version  # If using Python tools
```

### Generate Support Bundle

⚠️ **WARNING**: Support bundles may contain sensitive information including API tokens, repository paths, and configuration details. Always review and redact sensitive data before sharing with support or posting publicly.

```bash
#!/bin/bash
# Create support bundle

cat > coderabbit-support-bundle.txt <<EOF
CodeRabbit CLI Version:
$(coderabbit --version)

System Information:
OS: $(uname -s)
Architecture: $(uname -m)
Kernel: $(uname -r)

Git Information:
$(git --version)

Installation Path:
$(which coderabbit)

Configuration:
$(coderabbit config show 2>&1)

Recent Logs:
$(tail -n 50 ~/.config/coderabbit/logs/latest.log 2>&1)
EOF

echo "Support bundle created: coderabbit-support-bundle.txt"
```

---

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 1 | General error | Check error message details |
| 2 | Authentication failed | Re-authenticate: `bash auth-setup.sh setup` |
| 3 | Network error | Check connectivity and firewall |
| 4 | Configuration error | Validate config: `coderabbit config validate` |
| 5 | File not found | Check file paths and permissions |
| 6 | Invalid input | Check command syntax |
| 7 | API error | Check API status and token |
| 8 | Timeout | Increase timeout or reduce scope |
| 9 | Rate limited | Wait and retry |
| 10 | Invalid token | Regenerate token |

---

## Getting Additional Help

### 1. Check Documentation

- [CLI Usage Guide](./CLI_USAGE_GUIDE.md)
- [Claude Integration](./claude-integration.md)
- [Prompt Templates](./prompt-templates.md)

### 2. Enable Verbose Output

```bash
coderabbit review --verbose
```

### 3. Check Logs

```bash
# View recent logs
tail -f ~/.config/coderabbit/logs/latest.log

# Search for errors
grep -i error ~/.config/coderabbit/logs/*.log
```

### 4. Test API Connection

```bash
bash auth-setup.sh test
```

### 5. Verify Installation

```bash
# Run full verification
coderabbit --version
coderabbit auth status
coderabbit config show
```

### 6. Contact Support

When contacting support, include:

1. CLI version: `coderabbit --version`
2. Operating system: `uname -a`
3. Error message (full text)
4. Steps to reproduce
5. Debug logs: `CODERABBIT_DEBUG=1 coderabbit review 2>&1 | tee debug.log`
6. Configuration (sanitized): `coderabbit config show`

### 7. Community Resources

- GitHub Issues: Report bugs and feature requests
- Team Slack: Internal support channel
- Documentation: Check for updates and new guides

---

## Prevention Tips

### Regular Maintenance

```bash
# Update CLI regularly
bash install-coderabbit-cli.sh

# Clear old cache
rm -rf ~/.cache/coderabbit/old

# Verify configuration
coderabbit config validate

# Test authentication
bash auth-setup.sh status
```

### Best Practices

1. **Keep CLI updated** - Check for updates monthly
2. **Use version control for config** - Track .coderabbit.yaml changes
3. **Monitor API status** - Subscribe to status updates
4. **Regular authentication checks** - Verify tokens haven't expired
5. **Document custom workflows** - Team-specific procedures
6. **Test in CI/CD** - Catch issues before they affect team

---

**Last Updated**: 2025-10-14
**Version**: 1.0.0
