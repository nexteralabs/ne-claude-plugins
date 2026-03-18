# Code Review

## Requesting Review

After completing implementation, gather context:

```bash
BASE_SHA=$(git merge-base HEAD main)
HEAD_SHA=$(git rev-parse HEAD)
git diff $BASE_SHA..$HEAD_SHA --stat
git log $BASE_SHA..$HEAD_SHA --oneline
```

Dispatch the code-reviewer agent with:
- What was implemented (summary)
- The plan or requirements it was built against
- BASE_SHA and HEAD_SHA
- Working directory path

## Receiving Review

### The Response Protocol

1. **READ** — Complete feedback without reacting
2. **UNDERSTAND** — Restate the requirement in your own words
3. **VERIFY** — Check against the actual codebase
4. **EVALUATE** — Is this technically sound for THIS codebase?
5. **RESPOND** — Technical acknowledgment or reasoned pushback
6. **IMPLEMENT** — One item at a time, test after each fix

### Forbidden responses

- "You're absolutely right!" (performative agreement)
- "Great point!" / "Excellent feedback!"
- "Let me implement that now" (before verifying the claim)

### Instead

- Restate the technical requirement
- Ask clarifying questions if the feedback is ambiguous
- Push back with technical reasoning if you disagree
- Just start working — actions over words

### Acting on findings

| Severity | Action |
|----------|--------|
| Critical | Fix immediately — blocks everything |
| Important | Fix before PR — should not ship with these |
| Minor/Nit | Note for later or push back with reasoning |

### YAGNI check

If a reviewer suggests "implement this properly" or "add handling for X":
1. Grep the codebase for actual usage
2. If unused or hypothetical: push back — "This isn't called anywhere. YAGNI?"
3. If actually used: implement properly

### Never

- Blindly implement all feedback without verification
- Batch multiple fixes without testing each one
- Assume the reviewer is right without checking the code
