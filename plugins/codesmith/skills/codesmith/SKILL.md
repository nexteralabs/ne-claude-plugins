---
name: codesmith
description: "Development workflow that enforces spec refinement, TDD, and KISS at every step. Use this skill whenever the user is about to start coding: building a feature, fixing a bug, implementing something, working on a ticket, or any development task beyond a one-liner. Triggers on: 'let's build', 'implement', 'fix this bug', 'work on', 'start coding', 'let's work', 'build feature', 'add support for', 'create the', 'refactor', ticket references like KAN-123, or any request that will result in writing production code. Also use when the user says 'codesmith', 'dev workflow', or 'full workflow'. Do NOT trigger for questions about code, reading files, running commands, or non-coding tasks."
version: 2.0.0
---

# CodeSmith

A development workflow that enforces spec refinement, TDD, and simplicity at every step. It exists because fast code that breaks costs more than thoughtful code that ships clean.

Three rules govern everything:

1. **Refine before you write.** Understand the problem fully. Clarify ambiguity. Surface edge cases. No code until you know exactly what you're building and why.
2. **Test before you implement.** Write a failing test first. Then make it pass. Then refactor. No production code exists without a test that demanded it.
3. **Simplest thing that works.** Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations. The right amount of code is the minimum that solves the problem.

---

## How it works

When this skill triggers, drive the following flow automatically. Don't ask the user to pick phases or type subcommands. Just move through the flow, pausing only at gates that need human input.

### 1. Understand the task

Figure out what the user wants to build or fix. This context can come from:

- **What they just said** — "implement user authentication", "fix the timeout bug"
- **A Jira ticket** — if the user mentions a ticket ID (KAN-123) and the Atlassian MCP is available (`mcp__atlassian__*` tools), pull the ticket details automatically. If Jira isn't available, don't ask about it. Just work with what the user gave you.
- **A current task file** — check `.claude/current-task.md` if it exists for ongoing work context.

If the task is unclear, ask clarifying questions, one at a time, prefer multiple choice. Stop asking once you have enough to proceed.

For trivial changes (typo, config tweak, < 10 lines with obvious intent), skip straight to implementation with a test.

### 2. Design the approach

Explore the codebase. Understand existing patterns, conventions, and architecture. Check recent commits for context.

For non-trivial work, propose 2-3 approaches. For each approach, explain:
- What changes and where
- The tradeoff: what you gain, what you lose
- Complexity: how many moving parts

Common approach patterns to consider:

**Extend vs. extract.** Can you add to an existing module, or does this need its own? Extending is simpler but risks bloating. Extracting is cleaner but adds indirection. Default to extending unless the module is already doing too much.

**Inline vs. abstracted.** Should you write the logic directly where it's needed, or create a reusable function/class? If it's used once, inline it. If it's used twice, still probably inline it. Three times, extract. Premature abstraction is worse than duplication.

**Sync vs. async.** Can this run synchronously, or does it need to be async (queues, events, background jobs)? Sync is simpler to test and debug. Only go async when you have a real reason: long-running operations, decoupling systems, handling load.

**Build vs. use a library.** Is there an existing library that solves this? If so, is it maintained, small, and well-tested? A 5-line function you write beats a 50KB dependency you don't control. But don't reinvent cryptography.

**Modify in place vs. migrate.** Can you change the existing code, or do you need a migration strategy (dual writes, feature flags, phased rollout)? Modify in place when the change is backward compatible. Migrate when it's not.

**Top-down vs. bottom-up.** Start from the API/UI and work inward, or start from the data layer and build up? Top-down gives faster user feedback. Bottom-up gives a more solid foundation. Pick based on what's riskier: the interface or the plumbing.

Be ruthless about YAGNI. Remove anything not strictly required. Follow existing patterns in the codebase, don't invent new ones.

Present the approach and get user approval before moving on. This is a hard gate. No code until the design is approved.

### 3. Set up the workspace

Create a feature branch and start clean:

```bash
git checkout main && git pull origin main
git checkout -b {branch-name}
```

Branch naming: if there's a Jira ticket, use `{TICKET-KEY}-short-description`. Otherwise, use `short-description` derived from the task.

If the user already has a branch, skip this. Don't force a new one.

Track the task in `.claude/current-task.md`:
```markdown
id: {ticket key or short identifier}
title: {what we're building}
branch: {branch-name}
started: {ISO timestamp}
```

If Jira is available and the ticket isn't already "In Progress", transition it.

### 4. Plan the implementation

Write a concrete plan. Not vague bullets. Actual steps with file paths, test names, and code intent. Save it using Claude's plan mode or to `docs/plans/{branch-name}.md`.

Every task in the plan follows the TDD cycle:
1. Write the failing test (what behavior are we adding?)
2. Run it. Confirm it fails for the right reason
3. Write minimal code to pass
4. Run it. Confirm it passes
5. Refactor if needed (keep tests green)
6. Commit

Tasks should be small and focused. One unit of behavior each, ordered by dependency.

Present the plan. Get approval. Another hard gate.

### 5. Implement

Follow the plan. For each task:

**Write the test first.** This is non-negotiable. The test describes the behavior you're about to build. Run it. Watch it fail. If it doesn't fail, the test is wrong or the behavior already exists.

**Write the minimum code to pass.** Not the "complete" code. Not the "robust" code. The minimum. If the test only checks one case, only handle that case. The next test will drive the next behavior.

**Run the full suite after each change.** No regressions. If something breaks, stop and fix it before moving on.

**Commit after each passing task.** Small, atomic commits following Conventional Commits (see `references/commits.md`).

For larger implementations with independent units of work, use subagent-driven development:
- Dispatch an implementer agent (see `agents/implementer.md`) with full task context
- When it reports back, dispatch spec and code review agents to verify
- Only mark the task done after review passes

When stuck, read `references/debugging.md`. If 3+ attempts fail on the same issue, question the approach, don't keep retrying. If blocked on requirements, ask the user.

### 6. Review

After all tasks are complete:

1. Run the full test suite. Everything must pass
2. Dispatch the code-reviewer agent for the entire implementation (see `agents/code-reviewer.md`)
3. Fix critical and important findings. Push back on nits with reasoning if appropriate.

Before claiming anything is done, follow the verification protocol in `references/verification.md`: identify the command that proves the claim, run it, read the full output, confirm it matches. Never say "should work" or "probably passes."

### 7. Ship

Commit any remaining changes. Sync with main:

```bash
git fetch origin main && git merge origin/main
```

If conflicts: stop and tell the user. Don't auto-resolve ambiguous conflicts.

Build the PR:

```markdown
## Initial State
[The problem or gap before this change.]

## Modifications Done
[What changed and why. Reference specific files.]

## Test Results
[What was tested and the outcome.]

## QA Testing Guide
### Steps to Test
1. [Step]
2. [Expected result]
```

If there's a Jira ticket, prepend a ticket link section and update the ticket status to "Ready for QA" with a comment containing the PR link and QA steps.

If Discord is configured (`~/.claude/bin/discord` exists), notify the pull-requests channel.

Present the PR preview to the user for confirmation before creating it.

---

## Jira integration (optional)

This skill works with or without Jira. Here's how to detect and adapt:

- **Jira is available** if the Atlassian MCP tools exist (`mcp__atlassian__*`). When available, use them to fetch tickets, transition statuses, add comments, and log work. All automatically as part of the flow.
- **Jira is not available**. That's fine. The workflow is the same, just without ticket management. The user provides context directly.

Don't ask "do you use Jira?" Just check for the MCP tools and act accordingly. If the user mentions a ticket ID and Jira isn't available, tell them once that Jira MCP isn't configured and move on with the information they gave you verbally.

Remember the user's setup across conversations. If they don't use Jira, don't keep checking.

---

## Reference files

These are loaded on demand. Read them when the relevant situation comes up:

- `references/tdd.md` — TDD cycle details, testing anti-patterns, why test-first matters
- `references/debugging.md` — Systematic root cause investigation, when to stop retrying
- `references/verification.md` — Evidence-before-claims protocol, red flags for unverified claims
- `references/code-review.md` — How to request and respond to code review findings
- `references/commits.md` — Conventional Commits standard, types, breaking changes, squashing
