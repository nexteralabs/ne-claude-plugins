---
name: review
description: "Multi-agent code review — spec compliance then code quality. Dispatches spec-reviewer and code-reviewer agents. Use after implementation is complete. Triggers on: 'review this', 'review my code', 'check my work', or automatically as part of the codesmith workflow."
version: 3.2.0
---

# Review

Verify the implementation is correct, complete, and clean. Uses two-stage review: spec compliance first, then code quality.

## When to use

- After all implementation tasks are complete
- When you want a second opinion on your work
- Automatically as part of the codesmith workflow after implementation

## Process

### 1. Pre-Review Verification

Before dispatching reviewers, verify locally:

```bash
# Run the full test suite
{test command for the project}

# Get the diff scope
BASE_SHA=$(git merge-base HEAD main)
HEAD_SHA=$(git rev-parse HEAD)
git diff $BASE_SHA..$HEAD_SHA --stat
```

**All tests must pass before review.** If tests fail, go back to the implement phase — don't send broken code to review.

### 2. Stage 1 — Spec Compliance

Dispatch the **spec-reviewer agent** (see `agents/spec-reviewer.md`) with:

- The approved spec / requirements
- The implementation (files changed)
- Working directory

The spec reviewer checks:
- Every requirement has a corresponding implementation
- No extra/unneeded work beyond the spec
- No misunderstandings of requirements
- Every requirement has a corresponding test

**If FAIL:** Fix the missing/wrong items, then re-submit for spec review. Loop until PASS.

### 3. Stage 2 — Code Quality

After spec compliance passes, dispatch the **code-reviewer agent** (see `agents/code-reviewer.md`) with:

- What was implemented (summary)
- The plan or requirements
- BASE_SHA and HEAD_SHA
- Working directory

The code reviewer checks:
- Plan alignment
- Code quality and conventions
- Test quality
- Security concerns
- Correctness under load (when relevant)
- Architecture

### 4. Acting on Findings

| Severity | Action |
|----------|--------|
| **Critical** | Fix immediately — blocks everything |
| **Important** | Fix before shipping — should not merge with these |
| **Minor** | Fix if quick, otherwise note for follow-up |

For each finding:
1. **Read** the feedback without reacting
2. **Verify** against the actual code — is the reviewer right?
3. **Evaluate** — is this a real problem or YAGNI?
4. **Fix or push back** — with technical reasoning

See `references/code-review.md` for the full response protocol.

### 5. Verification Before Done

Follow the verification protocol (see `references/verification.md`):

```
1. IDENTIFY — What command proves this claim?
2. RUN     — Execute it fresh
3. READ    — Full output, check exit code
4. VERIFY  — Does output confirm the claim?
5. ONLY THEN — Claim it's done
```

Never say "should work" or "probably passes." Prove it.

**Ask yourself: "Would a staff engineer approve this?"**

If the answer is no, keep going.

## Rules

- All tests must pass BEFORE dispatching reviewers
- Spec compliance before code quality — correct first, clean second
- Never trust a subagent's "DONE" report without independent verification
- Fix critical and important findings. Push back on nits with reasoning.
- Don't batch multiple review fixes — test after each one
