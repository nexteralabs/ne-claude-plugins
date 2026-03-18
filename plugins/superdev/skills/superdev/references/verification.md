# Verification Before Completion

## Core Principle

Evidence before claims. Always.

## The Gate Function

Before claiming ANY status (tests pass, build succeeds, bug fixed, feature complete):

```
1. IDENTIFY — What command proves this claim?
2. RUN     — Execute the full command (fresh, complete)
3. READ    — Full output, check exit code
4. VERIFY  — Does output actually confirm the claim?
   → NO:  State actual status with evidence
   → YES: State claim WITH evidence
5. ONLY THEN — Make the claim
```

## Verification Requirements

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command: 0 failures, exit 0 | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, previous run |
| Build succeeds | Build command: exit 0 | Linter passing |
| Bug fixed | Reproduce original symptom: no longer occurs | "Code changed, should work" |
| Feature complete | All acceptance criteria verified individually | Some criteria checked |

## Red Flags — Stop Immediately

You are about to make an unverified claim if you:

- Use "should", "probably", "seems to", "I believe"
- Express satisfaction before running verification
- Are about to commit/push without running tests
- Trust a subagent's success report without checking
- Rely on a previous run instead of a fresh one
- Check partial output instead of full results

## After Subagent Work

When a subagent reports "DONE" or "tests pass":

1. Read their report — note what they claim
2. Run the test command yourself in the working directory
3. Compare actual output to their claim
4. Only proceed if YOUR verification confirms

Never trust a report. Verify independently.
