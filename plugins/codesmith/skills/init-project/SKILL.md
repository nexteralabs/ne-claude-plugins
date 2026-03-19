---
name: init-project
description: "Scaffold a project's CLAUDE.md with battle-tested development principles, detect ticket system, and configure project defaults. Use when starting a new project, onboarding to a codebase, or when the user says 'init project', 'set up claude', 'scaffold claude.md', 'configure project'. Also triggered when codesmith detects no CLAUDE.md exists in the project root."
version: 3.0.0
---

# Init Project

Scaffold a project's CLAUDE.md with core development principles and detect the project's ticket tracking system. This runs once per project and configures everything the codesmith workflow needs.

## When to use

- Starting work on a new project that has no CLAUDE.md
- User explicitly asks to set up or scaffold CLAUDE.md
- User says "init project" or "configure project"
- Codesmith orchestrator detects no CLAUDE.md in the project root

## Process

### 1. Detect Existing Configuration

Check if CLAUDE.md already exists at the project root:

- **Exists**: Read it. Don't overwrite. Ask the user if they want to merge codesmith principles into their existing file. Append only what's missing.
- **Doesn't exist**: Create it fresh with the full template below.

### 2. Detect Ticket System

Ask the user once:

> "Does this project use a ticket tracking system (Jira, Linear, GitHub Issues, etc.)?"

Based on their answer:

- **Jira**: Set `ticket-system: jira` in CLAUDE.md. Verify Atlassian MCP tools are available (`mcp__atlassian__*`). If not, note that Jira MCP needs to be configured for full integration.
- **Linear / GitHub Issues / other**: Set `ticket-system: {system}`. Note that full integration depends on the relevant MCP being available.
- **None**: Set `ticket-system: none`. All ticket-related steps will be silently skipped throughout the workflow.

### 3. Detect Project Basics

Auto-detect from the codebase:

- **Language/framework** — check file extensions, package files, config files
- **Test runner** — `jest`, `vitest`, `pytest`, `go test`, `cargo test`, etc.
- **Package manager** — `npm`, `bun`, `yarn`, `pnpm`, `pip`, `cargo`, etc.
- **Build command** — from package.json scripts, Makefile, etc.

### 4. Generate CLAUDE.md

Write the file using the template below, filling in detected values and the user's ticket system choice.

---

## CLAUDE.md Template

```markdown
# {Project Name}

## Project Configuration

- **Language:** {detected}
- **Framework:** {detected}
- **Test runner:** {detected command, e.g., `bun test`, `pytest`}
- **Package manager:** {detected}
- **Build command:** {detected}
- **Ticket system:** {jira | linear | github-issues | none}

## Development Workflow

This project uses the codesmith workflow. Start any dev task by describing what you want to build — the workflow drives automatically through brainstorm → workspace → plan → implement → review → ship.

## Core Principles

### Plan Mode Default

Enter plan mode for any non-trivial task (3+ steps or architectural decisions). If something goes wrong, STOP and re-plan immediately — don't keep pushing. Use plan mode for verification steps, not just building. Write detailed specs upfront to reduce ambiguity.

### Subagent Strategy

Use subagents frequently to keep the main context window clean. Offload research, exploration, and parallel analysis to subagents. For complex problems, throw more compute via subagents. Assign one task per subagent for focused execution.

### Self-Improvement Loop

After any correction from the user, update `tasks/lessons.md` with the pattern. Write rules for yourself to prevent repeating the same mistake. Ruthlessly iterate on these lessons until the mistake rate drops. Review lessons at the start of each session.

### Verification Before Done

Never mark a task complete without proving it works. Diff behavior between main and your changes when relevant. Ask yourself: "Would a staff engineer approve this?" Run tests, check logs, and demonstrate correctness.

### Demand Elegance (Balanced)

For non-trivial changes, ask: "Is there a more elegant solution?" If a fix feels hacky, ask: "Knowing everything I know now, implement the elegant solution." Skip this for simple fixes — don't over-engineer. Challenge your own work before presenting it.

### Autonomous Bug Fixing

When given a bug report: just fix it. Use logs, errors, and failing tests to diagnose. Require zero context switching from the user. Fix failing CI tests automatically.

## Task Management

1. **Plan First** — Write the plan in `tasks/todo.md` with checkable items
2. **Verify Plan** — Confirm the plan before implementation
3. **Track Progress** — Mark items complete as you go
4. **Explain Changes** — Provide a high-level summary at each step
5. **Document Results** — Add a review section to `tasks/todo.md`
6. **Capture Lessons** — Update `tasks/lessons.md` after corrections

## Core Rules

### Simplicity First
Make every change as simple as possible and minimize code impact. Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations.

### No Laziness
Find root causes. Avoid temporary fixes. Maintain senior-level engineering standards. Never say "should work" — prove it.
```

---

### 5. Create Supporting Directories

```bash
mkdir -p tasks
```

Create `tasks/lessons.md` if it doesn't exist:

```markdown
# Lessons Learned

Patterns and rules discovered during development. Review at the start of each session.

## Patterns

<!-- Add entries here as corrections happen -->
<!-- Format: **Pattern:** {what happened} → **Rule:** {what to do instead} -->
```

Create `tasks/todo.md` if it doesn't exist:

```markdown
# Task Tracker

## Current

<!-- Active tasks go here -->

## Completed

<!-- Finished tasks move here -->
```

### 6. Confirm with User

Present the generated CLAUDE.md and ask the user to review. They own this file — any principle they want to drop or modify is their call.

## Ticket System Architecture

The ticket system is designed as a pluggable abstraction:

```
CLAUDE.md: ticket-system: {jira | linear | github-issues | none}
    ↓
Workflow checks this value
    ↓
If "none" → skip all ticket steps silently
If "jira" → use mcp__atlassian__* tools
If "linear" → use Linear MCP tools (when available)
If "github-issues" → use gh CLI
```

**Adding a new ticket system** requires:
1. A detection method (MCP tools or CLI)
2. Operations: fetch ticket, transition status, add comment
3. A mapping from the system's status names to the workflow's phases (In Progress, Ready for QA, Done)

This is documented so future contributors can add adapters without modifying the core workflow.

## Rules

- Never overwrite an existing CLAUDE.md without asking
- Ask about ticket system once, save the answer, never ask again
- Auto-detect everything you can — minimize questions to the user
- The generated CLAUDE.md is a starting point — users are expected to customize it
- Don't add language/framework-specific rules — keep principles universal
