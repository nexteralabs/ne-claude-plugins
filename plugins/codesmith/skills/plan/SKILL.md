---
name: plan
description: "Write concrete implementation plans with TDD steps, file paths, and dependency ordering. Use when you have an approved spec and need to break it into executable tasks. Triggers on: 'write a plan', 'plan this', 'break this down', or automatically as part of the codesmith workflow."
version: 3.0.0
---

# Plan

Write a concrete, executable implementation plan. Not vague bullets — actual steps with file paths, test names, and code intent.

## When to use

- After a spec has been approved (from brainstorm phase or user-provided)
- When a task has 3+ steps and needs sequencing
- Automatically as part of the codesmith workflow after workspace setup

## Process

### 1. Enter Plan Mode

Use Claude's plan mode for the planning phase. This keeps planning separate from execution and lets you think through the full scope before committing to action.

### 2. Analyze the Spec

Read the approved spec (from the brainstorm output or the current conversation context). Identify:

- **Units of behavior** — each distinct piece of functionality
- **Dependencies** — what must exist before what
- **Risk areas** — where bugs are most likely, where the design is least certain
- **Existing code to modify** — use subagents to explore if needed

### 3. Write the Plan

Each task in the plan follows this structure:

```markdown
### Task {N}: {descriptive name}

**Files:** {exact file paths to create or modify}
**Test:** {test file and test name}
**Behavior:** {what this task adds — one sentence}
**Depends on:** {task numbers this depends on, or "none"}

**Steps:**
1. Write test: {describe the test — what it asserts}
2. Run test → expect RED (fails because {reason})
3. Implement: {describe the minimal code}
4. Run test → expect GREEN
5. Commit: `{type}({scope}): {message}`
```

### 4. Task Sizing

Tasks should be **bite-sized** — each one is a single unit of behavior:

- One test, one implementation, one commit
- If a task needs more than ~50 lines of production code, split it
- If you can't describe the behavior in one sentence, split it
- Order by dependency: foundations first, features on top

### 5. Ticket References

If a ticket system is configured (check CLAUDE.md) and a ticket ID is available, include the ticket key in commit messages:

```
feat(auth): add JWT validation

Refs: KAN-123
```

### 6. Save the Plan

Save to `docs/plans/{branch-name}.md` or use Claude's built-in plan mode. Include a header:

```markdown
# Plan: {task title}

**Branch:** {branch-name}
**Ticket:** {ticket key or "N/A"}
**Spec:** {one-line summary of approved spec}

## Tasks

{tasks here}
```

### 7. Get Approval

Present the plan to the user. This is a **hard gate**. No implementation until the plan is approved.

If the user wants changes, revise and re-present. Don't start coding "while we figure it out."

## When Things Go Wrong

If during implementation something invalidates the plan:

1. **STOP immediately** — don't keep pushing
2. **Re-enter plan mode** — reassess with new information
3. **Revise the plan** — update remaining tasks
4. **Get approval** — if the change is significant, check with the user
5. **Resume** — continue with the updated plan

Plans are living documents. Rigidly following a broken plan is worse than pausing to fix it.

## Rules

- Every task must have a failing test as step 1
- No task should depend on something that hasn't been planned yet
- Plans are concrete — file paths, test names, commit messages. Not "implement the thing"
- Use subagents for codebase exploration during planning — keep context clean
- For trivial changes (< 3 steps, obvious intent), skip formal planning — just list the steps briefly
