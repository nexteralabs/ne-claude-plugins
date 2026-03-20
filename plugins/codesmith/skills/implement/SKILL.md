---
name: implement
description: "Execute implementation plans using TDD and subagent-driven development. Follows red-green-refactor strictly. Use when you have an approved plan and are ready to write code. Triggers on: 'implement', 'start coding', 'execute the plan', or automatically as part of the codesmith workflow."
version: 3.2.0
---

# Implement

Execute the plan. Write tests first, make them pass, commit, repeat. Use subagents for parallel independent work.

## When to use

- After a plan has been approved
- When you're ready to write actual code
- Automatically as part of the codesmith workflow after plan approval

## Process

### 1. Load the Plan

Read the approved plan from `docs/plans/{branch-name}.md` or from the current conversation context. Verify you have:

- Clear task list with ordering
- File paths and test names for each task
- Dependencies between tasks understood

### 2. Execute Each Task (TDD Cycle)

For each task in order:

#### RED — Write the Failing Test

```
1. Write the test exactly as planned
2. Run it
3. Verify it FAILS for the right reason
   - Missing function/class/method → correct
   - Import error or typo → fix that first, not the real code
   - Test passes immediately → test is wrong or behavior already exists
```

#### GREEN — Minimal Implementation

```
1. Write the MINIMUM code to make the test pass
2. Not the "complete" code. Not the "robust" code. The minimum.
3. If the test only checks one case, only handle that case
4. Run the test — verify it passes
5. Run the FULL test suite — no regressions
```

#### REFACTOR — Clean Up (only after green)

```
1. Remove duplication
2. Improve names
3. Extract helpers only if there's actual repetition (3+ uses)
4. Keep ALL tests green throughout
```

#### COMMIT

```bash
git add {specific files}
git commit -m "{type}({scope}): {description}"
```

If a ticket is configured, add `Refs: {TICKET-KEY}` in the commit footer.

### 3. Subagent-Driven Development

For larger implementations with **independent** units of work:

1. **Dispatch implementer agents** (see `agents/implementer.md`) — one task per agent, with full context:
   - The task description and requirements
   - Relevant file paths and existing code patterns
   - The test to write and behavior to implement
   - Working directory path

2. **When an agent reports back:**
   - Read the report — note what they claim
   - Dispatch spec-reviewer agent to verify compliance
   - Dispatch code-reviewer agent for quality check
   - Only mark the task done after both reviews pass

3. **One task per subagent** — focused execution, no context bleed

4. **Parallel when possible** — if tasks are independent (no shared files, no dependency), dispatch multiple agents simultaneously

### 4. When Stuck

Read `references/debugging.md` for systematic debugging.

Escalation ladder:
1. **1st failure** — re-read the error, check assumptions
2. **2nd failure** — add diagnostic instrumentation, trace data flow
3. **3rd failure** — STOP. Question the approach. Re-enter plan mode.
4. **Still stuck** — ask the user. Don't keep retrying.

### 5. Progress Tracking

After each completed task:
- Mark it done in `.claude/tasks/todo.md` (change `- [ ]` to `- [x]`)
- Update the `**Phase:**` line in `todo.md` to reflect current progress (e.g., `implementing (3/7)`)
- Report progress: "Task 3/7 complete: added JWT validation middleware"
- If the plan needs revision based on what you learned, pause and update it (see plan skill)

`todo.md` is the single source of truth for workflow resume. If it's not updated, the workflow can't be resumed in a new conversation.

## Reference Files

Load on demand when the situation calls for it:

- `references/tdd.md` — TDD cycle details, testing anti-patterns, test strategy
- `references/debugging.md` — Systematic root cause investigation
- `references/verification.md` — Evidence-before-claims protocol

## Rules

- **TDD is non-negotiable** — no production code without a failing test first
- **Commit after each passing task** — small, atomic commits
- **Run the full suite after every change** — no regressions
- **Never modify files outside the task scope** — stay focused
- **If 3+ attempts fail on the same issue, stop and re-plan** — don't brute force
- **Use subagents to keep context clean** — offload exploration and parallel work
