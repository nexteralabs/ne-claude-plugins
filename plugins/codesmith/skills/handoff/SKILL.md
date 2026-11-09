---
name: handoff
description: "Write a handoff doc so a fresh session can continue the current work."
disable-model-invocation: true
version: 3.3.0
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to `$TMPDIR` (else `/tmp`), not the workspace, and print its path.

Keep it short. Include:

- **Goal and current state**: the task, the codesmith phase it's in, what's done, what's next.
- **Decisions and dead ends**: what was decided and why, and approaches tried that failed (so they aren't retried).
- **Pointers, not copies**: reference the plan (`docs/plans/`), `.claude/tasks/todo.md`, branch, commits, PR, and ticket by path or URL. Don't duplicate what they already hold.
- **Suggested skills**: which skills the next session should invoke first (e.g. `codesmith` to resume).

Redact secrets, tokens, and personal data.

If the user passed arguments, treat them as what the next session will focus on and tailor the doc to it.
