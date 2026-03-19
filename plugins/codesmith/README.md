# CodeSmith

A development workflow that enforces spec refinement, TDD, and simplicity at every step. Triggers automatically when you start any dev work.

## How it works

Just start working: "build the login page", "fix the timeout bug", "implement KAN-42". The skill takes over and drives the full lifecycle:

1. **Understand** - Pulls task context from what you said, from Jira (if available), or from `.claude/current-task.md`
2. **Design** - Explores the codebase, proposes approaches, gets your approval
3. **Plan** - Writes a concrete implementation plan with TDD steps
4. **Implement** - Builds test-first with subagent-driven development
5. **Review** - Dispatches parallel security and logic review agents
6. **Ship** - Creates a clean PR, updates Jira if configured, notifies Discord if available

Each phase has a hard gate. Your approval is required before advancing.

## Principles

- **Spec refinement first** - no code until requirements are clear
- **TDD by default** - no production code without a failing test first
- **KISS** - simplest thing that works, no premature abstractions
- **Evidence over claims** - never say "should work", prove it with test output

## Jira integration (optional)

Works automatically when the Atlassian MCP is available. No setup commands needed. The skill detects the MCP tools and uses them to fetch tickets, transition statuses, and add comments as part of the flow. If Jira isn't available, the workflow is identical, just without ticket management.

## Agents

| Agent | Role |
|-------|------|
| **implementer** | Executes a single plan task with TDD |
| **spec-reviewer** | Verifies implementation matches requirements |
| **code-reviewer** | Reviews quality, security, architecture |

## Reference Docs

- [TDD](skills/codesmith/references/tdd.md) - Red-green-refactor, testing anti-patterns
- [Debugging](skills/codesmith/references/debugging.md) - Systematic root cause investigation
- [Verification](skills/codesmith/references/verification.md) - Evidence before claims
- [Code Review](skills/codesmith/references/code-review.md) - Requesting and receiving review
- [Commits](skills/codesmith/references/commits.md) - Conventional Commits standard
- [Pull Requests](skills/codesmith/references/pull-requests.md) - PR structure and hygiene

## Installation

```
/plugin install codesmith@ne-claude-plugins
```

## License

MIT
