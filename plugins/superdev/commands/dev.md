---
description: Superdev — supercharged dev workflow from ticket to PR with TDD, subagents, and code review
argument-hint: [start|plan|code|review|pr|status]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Dev Command

Supercharged development workflow. Invoke the `superdev` skill and execute the requested phase.

## Arguments

The user invoked this command with: $ARGUMENTS

## Phase Routing

Parse the first argument to determine which phase to run:

### `/dev` or `/dev start`
Run Phase 1 (Pick Up Task) + Phase 2 (Design).
- Detect tracking source from CLAUDE.md
- List available tasks, let user pick
- Create branch, update status, write current-task.md
- Explore codebase and design the approach
- Get user approval on design

### `/dev plan`
Run Phase 3 (Plan).
- Requires: active task in `.claude/current-task.md`
- Write implementation plan with TDD steps
- Get user approval on plan

### `/dev code`
Run Phase 4 (Implement).
- Requires: approved plan
- Execute tasks via subagent-driven development (or directly for simple tasks)
- TDD: test first, implement, verify, commit

### `/dev review`
Run Phase 5 (Review).
- Dispatch code-reviewer agent for all changes since branch creation
- Present findings, fix critical/important issues

### `/dev pr`
Run Phase 6 (PR + Ship).
- Commit pending changes, sync with main
- Build PR body, preview for user
- Create GitHub PR, update task status, notify Discord

### `/dev status`
Show current workflow state:
- Active task (from `.claude/current-task.md`)
- Current branch and commit count
- Plan location (if exists)
- Test suite status

## Full Flow

If no argument is provided, run the full workflow from Phase 1 through Phase 6, pausing at each gate for user approval.
