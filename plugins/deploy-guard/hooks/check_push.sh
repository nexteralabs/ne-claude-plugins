#!/usr/bin/env bash
#
# Pre-tool hook for Bash commands.
# If the command is a git push, run basic safety checks first.
#

TOOL_INPUT=$(cat)
COMMAND=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null)

# Only intercept git push commands
if ! echo "$COMMAND" | grep -qE '^\s*git\s+push'; then
    exit 0
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "⚠️  deploy-guard: You have uncommitted changes. Commit or stash before pushing." >&2
    exit 2
fi

# Check for force push to main/master
if echo "$COMMAND" | grep -qE '(--force|-f)\b' && echo "$COMMAND" | grep -qE '\b(main|master)\b'; then
    echo "🛑 deploy-guard: Force push to main/master blocked." >&2
    exit 2
fi

exit 0
