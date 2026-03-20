---
name: ship
description: "Ship reviewed code — sync with main, create PR, update ticket system, notify team. Use after review is complete. Triggers on: 'ship it', 'create PR', 'make pr', 'do pr', 'do a pr', 'make a pr', 'send pr', 'push pr', 'raise a pr', 'pr this', 'pr it', 'ready to merge', 'let's pr', 'put up a pr', or automatically as the final phase of the codesmith workflow."
version: 3.2.0
---

# Ship

Ship the reviewed code. Sync with main, build the PR, update the ticket system, and notify the team.

## When to use

- After review phase is complete (all findings addressed)
- When you're ready to create a pull request
- Automatically as the final phase of the codesmith workflow

## Process

### 1. Final Sync

```bash
git fetch origin main && git merge origin/main
```

If conflicts arise: **STOP and tell the user.** Don't auto-resolve ambiguous conflicts. Show what conflicts exist and let them decide.

### 2. Final Verification

Run the full test suite one more time after the merge. If anything breaks, fix it before proceeding.

### 3. Build the PR

Follow `references/pull-requests.md` for structure. The PR body must contain:

**Problem** — what was wrong or missing (the "why")
**Approach** — design decision and alternatives considered
**Key Changes** — important files, where reviewers should focus
**Testing** — what was tested, QA testing guide
**Deployment Notes** — migrations, env vars, feature flags (if applicable)

#### Ticket Integration

Check CLAUDE.md for `ticket-system` configuration:

- **Jira** (`ticket-system: jira`): Prepend `{TICKET-KEY}` to the PR title. Add a ticket link section to the PR body.
- **Other systems**: Follow the same pattern with the relevant ticket ID format.
- **No ticket system**: Skip ticket references entirely.

#### PR Title Format

```
{TICKET-KEY} feat(scope): short description    # with ticket
feat(scope): short description                  # without ticket
```

### 4. Present for Confirmation

Show the user the PR preview:
- Title
- Body (full)
- Target branch
- Files changed summary

**This is a hard gate.** Don't create the PR until the user confirms.

### 5. Create the PR

```bash
gh pr create --title "{title}" --body "{body}"
```

### 6. Post-PR Actions

#### Ticket System Update

If a ticket system is configured:

- **Jira**: Transition to "Ready for QA" (or equivalent). Add a comment with the PR link and QA testing steps.
- **Other systems**: Update status accordingly.

#### Team Notification

If Discord is configured (`~/.claude/bin/discord` exists), notify the pull-requests channel with:
- PR title and link
- Brief summary of what changed
- QA instructions if applicable

### 7. Cleanup

- Clear `.claude/tasks/todo.md` — the workflow is complete. Write a brief completion summary:
  ```markdown
  # Completed: {task title}

  **PR:** #{pr-number}
  **Branch:** {branch-name}
  **Phase:** shipped
  ```
  This prevents stale tasks from triggering false resume detection in the next workflow.

- If a worktree was used, remind the user it can be cleaned up after merge:
  ```bash
  git worktree remove ../{worktree-path}
  ```

## Rules

- Never create a PR without user confirmation
- Never auto-resolve ambiguous merge conflicts
- All tests must pass after the final sync
- PR body must be self-contained — don't rely on ticket links for context
- One concern per PR — if you notice unrelated changes crept in, flag it
