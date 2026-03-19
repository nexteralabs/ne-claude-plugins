# CodeSmith

A modular development workflow that enforces spec refinement, TDD, and simplicity at every step. Triggers automatically when you start any dev work and drives the full lifecycle — you never have to remember which phase comes next.

## How it works

Just start working: "build the login page", "fix the timeout bug", "implement KAN-42". The skill takes over and drives through each phase, gating at key moments for your approval:

1. **Init** — Detects project config, scaffolds CLAUDE.md if needed, detects ticket system
2. **Brainstorm** — Explores intent, proposes 2-3 approaches, runs a spec review loop
3. **Workspace** — Creates feature branch (with ticket ID if configured), optional worktree isolation
4. **Plan** — Writes concrete TDD tasks with file paths, test names, and commit messages
5. **Implement** — Builds test-first with subagent-driven development for parallel work
6. **Review** — Two-stage: spec compliance then code quality via dedicated agents
7. **Ship** — Creates PR, updates ticket system, notifies team

Each phase has a hard gate. Your approval is required before advancing.

## Modular Architecture

The orchestrator (`codesmith`) drives the flow automatically, but each phase is also a standalone skill you can invoke directly:

| Skill | What it does | Standalone trigger |
|-------|-------------|-------------------|
| `init-project` | Scaffold CLAUDE.md, detect ticket system | "init project", "scaffold claude.md" |
| `brainstorm` | Explore approaches, refine spec | "brainstorm", "design this" |
| `workspace` | Branch + worktree setup | "set up workspace", "create branch" |
| `plan` | Break spec into TDD tasks | "write a plan", "break this down" |
| `implement` | TDD execution + subagents | "implement", "start coding" |
| `review` | Spec + code quality review | "review this", "check my work" |
| `ship` | PR, ticket update, notifications | "ship it", "create PR" |

## Principles

- **Spec refinement first** — no code until requirements are clear
- **TDD by default** — no production code without a failing test first
- **KISS** — simplest thing that works, no premature abstractions
- **Evidence over claims** — never say "should work", prove it with test output
- **Plan mode for non-trivial work** — 3+ steps or architectural decisions → plan first
- **Subagents for clean context** — offload research and parallel work to subagents
- **Memory-driven learning** — corrections are offered as persistent memories for future sessions

## Ticket System Integration

Codesmith has a **pluggable ticket system** architecture. On first run, `init-project` asks which system you use and saves it to CLAUDE.md. After that, the workflow adapts automatically:

| System | Status | Integration |
|--------|--------|-------------|
| **Jira** | Supported | Via Atlassian MCP — fetch tickets, transition status, add comments |
| **Linear** | Planned | Via Linear MCP (when available) |
| **GitHub Issues** | Planned | Via `gh` CLI |
| **None** | Supported | All ticket steps silently skipped |

The ticket system choice is stored in CLAUDE.md as `ticket-system: {value}`. When configured:
- Ticket IDs appear in branch names (`KAN-123-add-auth`)
- Commit footers include `Refs: KAN-123`
- PR titles are prefixed with the ticket key
- Ticket status is transitioned automatically through the workflow

**Adding a new ticket system** requires implementing three operations (fetch, transition, comment) with the relevant MCP tools or CLI. The core workflow doesn't change — only the integration layer. See the `init-project` skill for architecture details.

## CLAUDE.md Scaffolding

When `init-project` runs on a new project, it generates a CLAUDE.md with:

- **Project config** — auto-detected language, framework, test runner, build commands
- **Core principles** — plan mode, subagent strategy, verification, elegance, autonomous bug fixing
- **Task management** — `.claude/tasks/todo.md` for tracking, auto-memory for persistent lessons
- **Ticket system config** — saved once, used throughout the workflow

This is a project-level file that you fully own. Drop, modify, or extend any principle to fit your project.

## Agents

| Agent | Role |
|-------|------|
| **implementer** | Executes a single plan task with strict TDD |
| **spec-reviewer** | Verifies implementation matches requirements exactly |
| **code-reviewer** | Reviews quality, security, architecture with KISS-first mindset |

## Reference Docs

- [TDD](skills/codesmith/references/tdd.md) — Red-green-refactor, testing anti-patterns, test strategy
- [Debugging](skills/codesmith/references/debugging.md) — Systematic root cause investigation
- [Verification](skills/codesmith/references/verification.md) — Evidence before claims
- [Code Review](skills/codesmith/references/code-review.md) — Requesting and receiving review
- [Commits](skills/codesmith/references/commits.md) — Conventional Commits standard
- [Pull Requests](skills/codesmith/references/pull-requests.md) — PR structure and hygiene

## Installation

```
/plugin install codesmith@ne-claude-plugins
```

## License

MIT
