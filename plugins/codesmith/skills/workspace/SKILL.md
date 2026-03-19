---
name: workspace
description: "Set up an isolated workspace for development — creates feature branches, optional git worktrees, and task tracking. Use when starting implementation work that needs a clean environment. Triggers on: 'set up workspace', 'create branch', 'start working on', or automatically as part of the codesmith workflow."
version: 3.1.0
---

# Workspace

Set up a clean, isolated workspace for development. Handles branching, optional worktrees, and task tracking.

## When to use

- Before starting implementation on any feature or fix
- When you need an isolated workspace for subagent-driven development
- Automatically as part of the codesmith workflow after brainstorm/design approval

## Process

### 1. Stale Branch Check

Before creating a branch, verify the current branch isn't stale:

```bash
git branch --show-current
git ls-remote --heads origin $(git branch --show-current)
gh pr list --head $(git branch --show-current) --state merged --json number --jq '.[0]'
```

A branch is **stale** if:
- It has been deleted on the remote (no result from `git ls-remote`)
- It has a merged PR associated with it

**If stale or on `main`:** Switch to main and create a fresh branch.
**If current and relevant to the task:** Keep it.

When called from the codesmith orchestrator, Phase 0 has already detected staleness and gathered the ticket ID — use that context directly.

### 2. Create Feature Branch

```bash
git checkout main && git pull origin main
git checkout -b {branch-name}
```

**Branch naming:**
- If a ticket system is configured (check CLAUDE.md for `ticket-system`) and a ticket ID is available: `{TICKET-KEY}-short-description` (e.g., `KAN-123-add-auth`)
- GitHub Issues: `issue-{number}-short-description` (e.g., `issue-43-fix-login`)
- Otherwise: `short-description` derived from the task

### 3. Commit Scaffolded Files

If init-project generated new files (CLAUDE.md, `.claude/tasks/todo.md`, `.gitignore` changes), commit them now as the first commit on the new branch:

```bash
git add CLAUDE.md .claude/tasks/todo.md .gitignore 2>/dev/null
git diff --cached --quiet || git commit -m "chore: scaffold codesmith project config"
```

This keeps project setup tracked from the start. The `git diff --cached --quiet` check avoids an empty commit if there's nothing new to add.

### 4. Git Worktree (for subagent isolation)

When the implementation will use subagent-driven development and the tasks are independent:

```bash
# Create a worktree for isolated work
git worktree add ../{repo-name}-{branch-name} {branch-name}
```

**When to use worktrees:**
- Multiple subagents working on independent tasks simultaneously
- Risky changes where you want easy rollback
- User explicitly requests isolation

**When to skip worktrees:**
- Simple, sequential changes
- Single-file modifications
- User is already working in the right branch

**Setup detection:** After creating a worktree, detect and run project setup:
- `package.json` → `npm install` or `bun install`
- `Cargo.toml` → `cargo build`
- `requirements.txt` / `pyproject.toml` → `pip install` / `poetry install`
- `go.mod` → `go mod download`

### 5. Ticket Context from Branch Name

The branch name is the single source of truth for ticket context:

- `KAN-123-add-auth` → ticket ID is `KAN-123`
- `add-auth` → no ticket

Extract the ticket ID by matching the prefix pattern for the configured ticket system (e.g., `[A-Z]+-\d+` for Jira). No separate task tracking file needed.

### 6. Ticket System Integration

If a ticket system is configured in CLAUDE.md:

- **Jira** (`ticket-system: jira`): If the Atlassian MCP tools are available (`mcp__atlassian__*`), transition the ticket to "In Progress" if it isn't already. Ticket ID is extracted from the branch name.
- **Other systems**: Check for the relevant MCP tools and transition accordingly.
- **No ticket system**: Skip this step entirely. No warnings, no prompts.

## Worktree Cleanup

When work is complete (after ship phase or on user request):

```bash
# From the main repo directory
git worktree remove ../{repo-name}-{branch-name}
```

Only clean up after the branch has been merged or the user confirms abandonment.

## Rules

- Always check for stale branches before starting new work — never reuse a branch from a previous PR
- Always pull latest main before branching
- Worktrees are optional — default to simple branching unless there's a reason for isolation
- Ticket context is derived from the branch name — no separate tracking file needed
