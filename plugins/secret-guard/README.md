# Secret Guard Plugin

Hook-based plugin that scans staged files for leaked secrets before committing.

## Features

- **Secret scanning on commit** — Scans `git diff --cached` for API keys, tokens, passwords, private keys, and cloud credentials before any `git commit`

## How It Works

Uses a Claude Code `PreToolUse` hook on `Bash` commands. When it detects a `git commit`, it scans the staged diff for secret patterns and blocks the commit if anything is found. All other commands pass through with zero overhead.

## License

MIT
