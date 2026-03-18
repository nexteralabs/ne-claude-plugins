---
name: superdev
description: Use this skill for any feature development, bug fix, or implementation task. Supercharged workflow covering the full lifecycle — picking up a ticket, designing the solution, planning implementation, TDD-driven coding with subagents, multi-agent code review, and PR creation with task tracking updates. Triggers on "let's work", "start task", "build feature", "implement", "fix bug", "start coding", "work on ticket", "dev workflow", "superdev".
version: 1.0.0
---

# Superdev Workflow

Supercharged development lifecycle — from ticket to merged PR with rigorous process and task tracking integration (Jira/Obsidian).

## The Workflow

```
1. Pick Up Task  →  2. Design  →  3. Plan  →  4. Implement (TDD + Subagents)  →  5. Review  →  6. PR + Ship
```

Each phase has a hard gate — do not advance until the current phase is complete and approved.

---

## Phase 1: Pick Up Task

### Detect tracking source

Read project `CLAUDE.md` for a `## Task Tracking` section. Extract `source` and config fields.

Supported sources:
- **jira** — needs `base-url`, `project-key`
- **obsidian** — needs `vault-path`, `project-folder`

If no section found, ask the user which system they use and write the config to CLAUDE.md.

### List and select task

**Jira:** Query via MCP — `assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC`. Present as numbered list.

**Obsidian:** Read `{vault-path}/{project-folder}/tasks.md`. Parse the Active Tasks table. Present as numbered list.

If user already specified a ticket (e.g., "work on KAN-42"), skip the listing.

### Set up workspace

After user selects a task:

```bash
git checkout main && git pull origin main
git checkout -b {branch-name}
git push -u origin {branch-name}
```

Branch naming:
- **Jira:** `{TICKET-KEY}-short-description` (e.g., `KAN-42-fix-login-timeout`)
- **Obsidian:** `short-description` from task title (e.g., `fix-discord-listener`)

Update task status to "In Progress" in the tracking source.

Write `.claude/current-task.md`:
```markdown
source: {jira|obsidian}
id: {ticket key or task title}
title: {full title}
url: {ticket URL if jira}
branch: {branch-name}
started: {ISO timestamp}
```

---

## Phase 2: Design

**HARD GATE:** Do NOT write code, scaffold, or take implementation action until design is approved.

### Explore and understand

1. Read the full ticket/task description, acceptance criteria, comments
2. Explore the codebase — find relevant files, patterns, conventions
3. Check recent commits for context

### Clarify requirements

Ask questions **one at a time**. Prefer multiple choice. Stop when requirements are clear enough to implement.

If the task is trivial (typo fix, config change, < 10 lines), skip design and go directly to Phase 4.

### Propose approaches

For non-trivial work:
1. Present 2-3 approaches with tradeoffs
2. Include: what changes, where, estimated complexity
3. Apply YAGNI ruthlessly — remove anything not strictly required
4. Follow existing patterns in the codebase

Get user approval before proceeding.

---

## Phase 3: Plan

### Write the implementation plan

Create `docs/plans/{branch-name}.md` (or `.claude/tasks/{branch-name}.md` if no docs/ dir).

Every plan MUST follow this structure:

```markdown
# {Feature Name} Implementation Plan

**Goal:** {One sentence}
**Approach:** {2-3 sentences}
**Files involved:** {Key files/components}

## Tasks

### Task 1: {Component/Feature Name}

**Files:**
- Create: `exact/path/to/file.ext`
- Modify: `exact/path/to/existing.ext`
- Test: `tests/path/to/test.ext`

- [ ] Step 1: Write failing test
      [Full code or clear specification]

- [ ] Step 2: Run test — verify it fails
      `npm test path/to/test -- --grep "test name"`

- [ ] Step 3: Write minimal implementation
      [Complete code, not "add validation here"]

- [ ] Step 4: Run test — verify it passes
      `npm test path/to/test`

- [ ] Step 5: Commit
      `git commit -m "feat(scope): description"`
```

### Plan rules

- Each task is ONE focused unit of work (2-5 minutes)
- Every task follows RED-GREEN-REFACTOR (see references/tdd.md)
- Steps include actual code or exact commands — never vague ("add logic here")
- Files section lists exact paths with line ranges for modifications
- Tasks are ordered by dependency — each builds on the last

### Review the plan

Present the plan to the user. Get explicit approval before implementation.

---

## Phase 4: Implement

Use **subagent-driven development** for tasks with 2+ independent units. For single-task work, implement directly.

### Subagent-driven implementation (recommended)

For each task in the plan:

**1. Dispatch implementer subagent** (see agents/implementer.md)
- Provide: full task text, codebase context, working directory
- Subagent implements, tests, commits, self-reviews
- Subagent reports back: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT

**2. Dispatch spec compliance reviewer** (see agents/spec-reviewer.md)
- Verify: did they build exactly what was requested? Nothing more, nothing less?
- If issues found → implementer fixes → re-review

**3. Dispatch code quality reviewer** (see agents/code-reviewer.md)
- Only AFTER spec compliance passes
- Check: clean code, tests, maintainability, patterns
- If issues found → implementer fixes → re-review

**4. Mark task complete** and move to next task.

### Direct implementation (simple tasks)

Follow the plan step by step. For each task:
1. Write the failing test first (RED)
2. Run it — confirm it fails for the right reason
3. Write minimal code to pass (GREEN)
4. Run it — confirm it passes
5. Refactor if needed (keep tests green)
6. Commit

**THE IRON LAW:** No production code without a failing test first. See references/tdd.md.

### When stuck

If implementation hits a wall:
1. Stop and investigate root cause (see references/debugging.md)
2. If >= 3 attempts failed on the same issue — question the approach, don't keep retrying
3. If blocked on requirements — ask the user, don't guess

---

## Phase 5: Review

After all tasks are complete:

1. Run the full test suite — all tests must pass
2. Dispatch the code-reviewer agent for the entire implementation
3. Address findings:
   - **Critical** — fix immediately
   - **Important** — fix before PR
   - **Minor** — note for later or push back with reasoning

### Verification before claiming done

**MANDATORY** — see references/verification.md

Before claiming any status:
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the full command
3. READ: Full output, check exit code
4. VERIFY: Does output confirm the claim?

Never use "should", "probably", or "seems to". Evidence or silence.

---

## Phase 6: PR + Ship

### Handle uncommitted changes

```bash
git status --short
```

If changes exist, stage and commit with a meaningful message. Do not use `--no-verify`.

### Sync with main

```bash
git fetch origin main
git merge origin/main
```

If conflicts: stop and tell user. Do not auto-resolve ambiguous conflicts.

### Build the PR

Construct the PR body — professional, no AI mentions, no emojis:

```markdown
## Initial State
[The problem or gap before this change. Be specific.]

## Modifications Done
[What changed and why. Reference specific files. Bullets for multiple changes.]

## Test Results
[What was tested and the outcome.]

## QA Testing Guide

### Areas of Focus
[Features or flows QA should verify.]

### Steps to Test
1. [Step]
2. [Step]
3. [Expected result]
```

**Jira:** Prepend `## Jira Ticket\n[{TICKET-KEY}]({url})` at the top.
**Obsidian:** No ticket link section.

PR title: `[{TICKET-KEY}] Short imperative description` (Jira) or `Short imperative description` (Obsidian).

### Present and confirm

```
Ready to submit. Actions:
  1. Create GitHub PR: "{title}"
  2. Update task status to Ready for QA in {source}
  3. Notify #pull-requests on Discord (if configured)

PR preview:
---
{full body}
---

Proceed? (yes / no / edit)
```

### Apply (only after confirmation)

```bash
git push
gh pr create --title "..." --body "..." --base main
```

**Update task status:**
- **Jira:** Transition to "Ready for QA" or "Ready for Review". Add comment with PR link + summary + QA steps.
- **Obsidian:** Update tasks.md — replace "(In Progress)" with "(Ready for QA)". Add PR link below table.

**Discord notification** (if `~/.claude/discord.env` or `~/.claude/bin/discord` exists):
```bash
~/.claude/bin/discord "pull-requests" "{TICKET-KEY} — {title} — {PR_URL}"
```

Report: PR URL, task status, Discord notification status.

---

## Quick Reference

| Phase | Gate | Output |
|-------|------|--------|
| 1. Pick Up | Task selected + branch created | `.claude/current-task.md` |
| 2. Design | User approves approach | Design decision |
| 3. Plan | User approves plan | `docs/plans/{branch}.md` |
| 4. Implement | All tests pass | Committed code |
| 5. Review | No critical/important issues | Clean codebase |
| 6. PR + Ship | User confirms | PR + task updated |
