# Deploy Guard Plugin

Hook-based plugin that validates code before writing and blocks unsafe deployments.

## Features

- **Secret scanning** — Blocks writes containing API keys, tokens, passwords, and private keys
- **Push protection** — Warns on uncommitted changes, blocks force-push to main/master

## How It Works

Uses Claude Code hooks to intercept tool calls:
- `PreToolUse` on `Edit|Write|MultiEdit` — scans for secrets
- `PreToolUse` on `Bash` — validates git push commands

## License

MIT
