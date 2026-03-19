---
name: code-audit
description: "Multi-agent code review that catches what humans skip. Use this skill when the user asks to review code, audit a PR, check for security issues, review changes, or wants a second opinion on their implementation. Triggers on: 'review this', 'review my code', 'review the PR', 'audit this', 'check for security issues', 'is this safe', 'code review', 'look over my changes', 'anything wrong with this', PR numbers or URLs. Also triggers automatically as part of the codesmith workflow's review phase. Do NOT trigger for explaining code or answering questions about how code works."
version: 1.0.0
---

# Code Audit

Multi-agent code review that dispatches parallel security and logic reviewers, then aggregates findings with confidence scores.

## How it works

When this skill triggers, automatically:

1. **Figure out what to review.** If the user mentioned a PR number or URL, fetch the diff with `gh pr diff`. If they're on a feature branch, diff against main. If they pointed at specific files, review those.

2. **Dispatch parallel review agents.** Spawn both agents at the same time — they review independently:
   - **Security reviewer** (`agents/security-reviewer.md`) — secrets, injection, auth, data exposure, dependencies, crypto, input validation
   - **Logic reviewer** (`agents/logic-reviewer.md`) — edge cases, error handling, race conditions, resource management, data integrity, API contracts

   Give each agent: the diff or file contents, the context of what was changed and why (from PR description or commit messages), and the working directory.

3. **Aggregate and present.** Collect findings from both agents, deduplicate, and present a structured review:

   **Critical** (high confidence) — must fix before merging
   **Important** (medium-high confidence) — should fix
   **Suggestions** (medium confidence) — worth considering
   **Nits** (low confidence) — optional improvements

   End with an overall assessment: approve / request changes / needs discussion.

The review should be direct and technical — no fluff, no "great job overall." Just the findings and the verdict.
