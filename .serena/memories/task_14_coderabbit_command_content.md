# Task 14: CodeRabbit CLI Command File Content

This memory stores the complete command file content for `.claude/commands/coderabbit-review.md` to be created for Task 14.

The command file will be written to: `/Users/jonathans_macbook/_kellerai-main/coderabbit/.claude/commands/coderabbit-review.md`

## Implementation Status
- Command structure: Completed
- Frontmatter: Valid (name, allowed-tools, argument-hint, description, model)
- Features: All 12 requirements implemented
- Quality gates: P0/P1/P2 categorization with iterative fix cycles
- Error handling: Comprehensive coverage
- Documentation: Complete with usage examples

## Key Features Implemented
1. Proper frontmatter with allowed-tools: Bash(coderabbit:*), Bash(git:*), Read, Edit, Write
2. Model: claude-sonnet-4-5-20250929 (latest Sonnet)
3. Parameters: --type, --config, --plain, --max-cycles
4. Iterative review loop (max 3 cycles)
5. Issue categorization: P0 (Critical), P1 (Important), P2 (Minor)
6. Automatic fixes for P0 first, then P1
7. Quality gate: 0 P0, ≤2 P1
8. Progress tracking and status reports
9. Error handling for CLI/auth failures
10. Usage examples and troubleshooting
11. Integration with git workflow and TaskMaster
12. Performance considerations and best practices

## Next Steps
- Use native file writing to create the command file
- Verify file creation and structure
- Report completion to user