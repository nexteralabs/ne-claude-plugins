# code-audit

Multi-agent code review that dispatches parallel security and logic reviewers with confidence-scored findings. Triggers automatically when you ask to review code, audit a PR, or check for security issues.

## How it works

Just say "review my code", "check this PR", or "is this safe?" The skill:

1. Figures out what to review — a PR, your current changes, or specific files
2. Dispatches parallel review agents (security + logic) that work independently
3. Aggregates findings with confidence scores: critical, important, suggestions, nits
4. Delivers a structured verdict: approve, request changes, or needs discussion

## Agents

| Agent | Focus |
|-------|-------|
| **security-reviewer** | Secrets, injection, auth, data exposure, dependencies, crypto, input validation |
| **logic-reviewer** | Edge cases, error handling, race conditions, resource management, data integrity |

## Installation

```
/plugin install code-audit@ne-claude-plugins
```

## License

MIT
