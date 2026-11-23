# Secret Guard Plugin

Hook-based plugin that scans staged files for leaked secrets before committing.

## Features

- **Secret scanning on commit** — Scans what a `git commit` would hold for API keys, tokens, passwords, private keys, and cloud credentials

## How It Works

Uses a Claude Code `PreToolUse` hook on `Bash` commands. When a command contains a `git commit` — alone, after `cd …`, or after `git add … &&` on the same line — it scans the lines the commit would add and blocks it if anything matches. With a `git add` or `commit -a` on the line, unstaged and untracked changes are scanned too. Removing a secret is never blocked. All other commands pass through with zero overhead.

If the hook cannot read its input or crashes, it blocks the command rather than letting it run unchecked.

## False positives

A test fixture or a placeholder can match. Once you have checked it is not a real secret, commit with the escape hatch in front of the command:

```bash
ALLOW_SECRET=1 git commit -m "test: add login fixture"
```

## Tests

```bash
python3 -m unittest discover -s plugins/secret-guard/tests
```

## License

MIT
