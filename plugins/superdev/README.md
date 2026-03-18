# Superdev

Supercharged development workflow — from ticket to PR with TDD, subagent-driven implementation, multi-agent code review, and task tracking.

## Usage

```
/dev              # Start full workflow (pick task → design → plan → code → review → PR)
/dev start        # Pick up a task and design the approach
/dev plan         # Write implementation plan
/dev code         # Implement with TDD + subagents
/dev review       # Run code review on all changes
/dev pr           # Create PR, update task, notify Discord
/dev status       # Show current workflow state
```

## The Workflow

```
1. Pick Up Task  →  2. Design  →  3. Plan  →  4. Implement  →  5. Review  →  6. PR + Ship
```

Each phase has a hard gate — user approval required before advancing.

## Features

- **Task tracking** — Jira and Obsidian integration for picking up tasks and updating status
- **Design-first** — No code before approach is approved
- **TDD enforced** — No production code without a failing test first
- **Subagent-driven** — Fresh agent per task with two-stage review (spec compliance + code quality)
- **Systematic debugging** — Root cause investigation before any fix attempt
- **Verification** — Evidence-based claims, no "should work"
- **Professional PRs** — Structured PR body with QA guide, task status updates, Discord notifications

## Agents

| Agent | Role |
|-------|------|
| **implementer** | Executes a single plan task with TDD |
| **spec-reviewer** | Verifies implementation matches requirements |
| **code-reviewer** | Reviews quality, security, architecture |

## Reference Docs

- [TDD](skills/superdev/references/tdd.md) — Red-green-refactor, testing anti-patterns
- [Debugging](skills/superdev/references/debugging.md) — Systematic root cause investigation
- [Verification](skills/superdev/references/verification.md) — Evidence before claims
- [Code Review](skills/superdev/references/code-review.md) — Requesting and receiving review

## Setup

Add task tracking config to your project's `CLAUDE.md`:

```markdown
## Task Tracking
- source: jira
- base-url: https://company.atlassian.net
- project-key: PROJ
```

or:

```markdown
## Task Tracking
- source: obsidian
- vault-path: /path/to/vault
- project-folder: 1. Projects/MyProject
```

## License

MIT
