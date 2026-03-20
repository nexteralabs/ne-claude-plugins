---
name: codesmith
description: "Development workflow that enforces spec refinement, TDD, and KISS at every step. Use this skill whenever the user presents work to be done — regardless of phrasing. If it implies something needs to change in the codebase, trigger this skill. BLOCKING RULE: Do NOT bypass this skill to do ad-hoc research, exploration, or agent-based investigation when the user's message implies work to be done. The brainstorm phase handles all research, exploration, and 'how should we build this' questions — that is its purpose. If the message contains BOTH research language AND feature/build intent, ALWAYS trigger this skill. Categories of work that ALWAYS trigger: (1) Features — build, implement, add, create, support, integrate, new feature, I want, I'd like, we need, we should, (2) Bugs — fix, investigate, debug, broken, not working, error, issue, regression, (3) Refactors — refactor, clean up, migrate, upgrade, deprecate, rename, restructure, (4) Performance — slow, optimize, latency, bottleneck, speed up, (5) Tech debt — clean up, modernize, consolidate, remove dead code, (6) Config/infra — add env var, set up CI, deployment, pipeline, (7) Pasted context — user pastes a Slack message, error log, Jira description, or any external context describing work to do, (8) Task transitions — next, another, moving on, ok next, something else, let's work, (9) Ticket references — KAN-123, PROJ-456, issue #42, or any ticket system identifier, (10) Research-with-intent — 'how could we build', 'best practice for building', 'search on this and build', 'figure out how to implement' — these combine research with build intent and MUST trigger this skill because brainstorm handles the research phase. Also trigger on: 'codesmith', 'dev workflow', 'full workflow'. When uncertain whether the user wants a full workflow or just a quick answer, ASK: 'Want me to start the codesmith workflow for this?' CRITICAL — workflow resume: before starting a new workflow, check .claude/tasks/todo.md. If there is pending work with unchecked items, the user may be continuing an existing workflow — ask before overwriting. Do NOT trigger for: pure questions about code ('how does X work?', 'what does this do?', 'explain'), reading files, running commands, or non-coding conversations."
version: 3.2.0
---

# CodeSmith

A development workflow that enforces spec refinement, TDD, and simplicity at every step. It exists because fast code that breaks costs more than thoughtful code that ships clean.

Three rules govern everything:

1. **Refine before you write.** Understand the problem fully. Clarify ambiguity. Surface edge cases. No code until you know exactly what you're building and why.
2. **Test before you implement.** Write a failing test first. Then make it pass. Then refactor. No production code exists without a test that demanded it.
3. **Simplest thing that works.** Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations. The right amount of code is the minimum that solves the problem.

---

## How it works

When this skill triggers, drive the following flow **automatically**. Don't ask the user to pick phases or type subcommands. Just move through the flow, pausing only at gates that need human input.

At each phase transition, briefly state what phase you're entering and what comes next. The user should always know where they are in the flow.

### Phase 0: Init, Resume Detection, and New Task Detection

**Step 1 — Project init check:**

- **No CLAUDE.md found**: Read the `init-project` skill and run it first. This sets up CLAUDE.md with core principles, detects the ticket system, and creates supporting directories.
- **CLAUDE.md exists**: Read it. Note the `ticket-system` value and any project-specific configuration.

Auto-memory (feedback type) will already be loaded into context with lessons from previous sessions — no manual review needed.

**Step 2 — Check for in-progress workflow:**

Before starting anything new, check if there's an existing workflow to resume:

```bash
cat .claude/tasks/todo.md 2>/dev/null
ls docs/plans/*.md 2>/dev/null
```

If `todo.md` exists and has **unchecked items** (`- [ ]`), a workflow is already in progress. The `**Phase:**` line tells you where it left off. If `todo.md` is empty but a plan file exists in `docs/plans/`, the plan was written but progress wasn't tracked — treat it as an in-progress workflow starting at Phase 4.

- **If the user's message relates to the pending work** (same feature/bug/task): Resume the workflow at the current phase. Briefly state where you're picking up: _"Resuming — you're in Phase {N} ({phase name}). Next up: {next unchecked item}."_
- **If the user's message is clearly NEW work** (different feature/bug): Inform the user: _"There's an in-progress task in todo.md: '{task summary}'. Want me to continue that, or start fresh on this new task?"_ Wait for confirmation before overwriting.
- **If the user went off-script** (asked questions, made corrections, explored code) and is now signaling forward progress ("ok continue", "let's keep going", "what's next"): Resume the workflow at the last incomplete phase. No need to ask — they're clearly coming back to the task.

**Step 3 — Detect new task intent:**

Only reach this step if Step 2 found no in-progress workflow, or the user confirmed they want to start fresh.

Check the current branch state:

```bash
git branch --show-current
git ls-remote --heads origin $(git branch --show-current)
gh pr list --head $(git branch --show-current) --state merged --json number --jq '.[0]'
```

If the current branch is stale (deleted on remote, has a merged PR, or is not `main` while the user signals new work), the user is starting a new task. Confirm and gather context:

> "Looks like you're starting a new task. Branch `{name}` is stale (previous PR was merged). What are you working on?"

If a ticket system is configured in CLAUDE.md:
> "Do you have a ticket number?"

Capture the task description and ticket ID (if any). These flow into Phase 1 (brainstorm context) and Phase 2 (branch naming).

If the branch is current and the user is clearly continuing existing work, skip this step.

**Step 4 — Ambiguity check:**

If the user's message could be interpreted as either a question or a task (e.g., "this API is slow" — could mean "tell me why" or "fix it"), ask:

> "Want me to start the codesmith workflow for this, or just investigate/answer?"

### Phase 1: Brainstorm

Read the `brainstorm` skill and follow its process:

1. Gather context (user request, ticket if applicable, codebase exploration)
2. Ask clarifying questions if needed
3. Propose 2-3 approaches for non-trivial work
4. Run the spec review loop until the user approves

**Gate:** Approved spec before proceeding.

**Skip condition:** For trivial changes (typo, config tweak, < 10 lines with obvious intent), skip to Phase 3 with a brief note on what you'll do.

### Phase 2: Workspace

Read the `workspace` skill and follow its process, passing along the task description and ticket ID gathered in Phase 0:

1. Create feature branch from main (using ticket ID from Phase 0 in the branch name if available)
2. Set up worktree if the implementation needs isolation
3. Transition ticket to "In Progress" if applicable

**Skip condition:** Only skip if Phase 0 determined the user is continuing existing work on a current branch.

### Phase 3: Plan

Read the `plan` skill and follow its process:

1. Enter plan mode
2. Break the approved spec into concrete TDD tasks
3. Include file paths, test names, commit messages
4. Order by dependency
5. Present for approval

**Gate:** Approved plan before proceeding.

**Skip condition:** For trivial changes (1-2 steps, obvious), list the steps briefly without formal plan mode.

### Phase 4: Implement

Read the `implement` skill and follow its process:

1. Execute each task following red-green-refactor
2. Use subagent-driven development for independent parallel work
3. Commit after each passing task
4. Report progress at milestones
5. If the plan breaks, stop and re-plan (go back to Phase 3)

**No gate here** — implementation flows continuously. But if something fundamental changes, pause and check with the user.

### Phase 5: Review

Read the `review` skill and follow its process:

1. Run full test suite — must pass before review
2. Dispatch spec-reviewer agent → fix any FAIL findings
3. Dispatch code-reviewer agent → fix critical/important findings
4. Follow verification protocol — prove everything works

**Gate:** All findings addressed and verified before proceeding.

### Phase 6: Ship

Read the `ship` skill and follow its process:

1. Sync with main
2. Build PR with full context
3. Present PR preview for confirmation
4. Create PR, update ticket, notify team

**Gate:** User confirms PR before creation.

---

## Ticket System Integration

The ticket system is **pluggable** and configured per-project in CLAUDE.md:

```
ticket-system: jira | linear | github-issues | none
```

- If `none` or not set: **all ticket-related steps are silently skipped**. No warnings, no prompts about tickets.
- If set to a system: use the relevant MCP tools or CLI to fetch tickets, transition statuses, add comments, and include ticket IDs in branches/commits/PRs.
- The workflow behavior is identical regardless of ticket system — only the integration layer changes.

**Currently supported:** Jira (via Atlassian MCP). Other systems can be added by implementing the fetch/transition/comment operations with the relevant tools.

Don't ask "do you use Jira?" mid-flow. The init-project skill handles detection once. After that, read from CLAUDE.md.

---

## Sub-Skills

Each phase delegates to a focused skill. These can also be invoked independently:

| Skill | Phase | Standalone Trigger |
|-------|-------|--------------------|
| `init-project` | 0 | "init project", "scaffold claude.md" |
| `brainstorm` | 1 | "brainstorm", "how should we", "design this" |
| `workspace` | 2 | "set up workspace", "create branch" |
| `plan` | 3 | "write a plan", "break this down" |
| `implement` | 4 | "implement", "start coding" |
| `review` | 5 | "review this", "check my work" |
| `ship` | 6 | "ship it", "create PR" |

## Agents

Dispatched during implementation and review phases:

| Agent | Role |
|-------|------|
| **implementer** | Executes a single plan task with TDD |
| **spec-reviewer** | Verifies implementation matches requirements |
| **code-reviewer** | Reviews quality, security, architecture |

## Reference Files

Loaded on demand by sub-skills when the situation calls for it:

- `references/tdd.md` — TDD cycle, testing anti-patterns, test strategy
- `references/debugging.md` — Systematic root cause investigation
- `references/verification.md` — Evidence-before-claims protocol
- `references/code-review.md` — Requesting and receiving review
- `references/commits.md` — Conventional Commits standard
- `references/pull-requests.md` — PR structure and hygiene

## Memory-Driven Learning

Throughout the workflow, when the user corrects your approach, evaluate whether the lesson is **general enough to help across multiple projects**. Only offer to save if it passes that filter.

Memories are for **general patterns** — lessons about tools, techniques, best practices, or workflow preferences that transfer across any codebase. They represent how the user wants you to think and work, regardless of what project you're in.

Project-specific fixes are **not memories** — if a correction resulted in a code change, the fix already lives in the code. Saving it as a memory would duplicate what the codebase already captures and clutter future conversations with irrelevant context.

When the lesson is general, ask:

> "I noticed something we could improve in our workflow. Want me to save this as a memory for future sessions?"

If they agree, save it as a `feedback` type memory. Never save without asking first.
