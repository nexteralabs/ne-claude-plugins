# Systematic Debugging

## Core Principle

Find the root cause before attempting any fix. Never guess-and-check.

## The Four Phases

Complete each phase before moving to the next.

### Phase 1: Build a Feedback Loop

This is the phase that matters. With a fast, deterministic pass/fail signal that goes red on _this_ bug, the cause will be found; without one, staring at code won't save you. Spend effort here first. In rough order of preference:

1. **Failing test** at whatever seam reaches the bug (unit, integration, e2e)
2. **curl / HTTP script** against a running dev server
3. **CLI run** on a fixture input, diffed against a known-good output
4. **Headless browser script** (Playwright) asserting on DOM, console, or network
5. **Replay a captured trace**: save a real payload or event log, push it through the code path alone
6. **Throwaway harness**: the smallest slice of the system (mocked deps) that hits the bug in one call
7. **Fuzz loop** for "sometimes wrong": run 1000 random inputs, catch the failing one
8. **Bisection**: if it broke between two known states, script the check and `git bisect run` it

Flaky bug? Raise the reproduction rate (loop it, add load, pin seeds) until the signal is reliable. No loop possible? Say so and ask the user for access, logs, or a capture rather than guessing.

**Redact secrets** in every command, output, and capture you show (`<REDACTED>`); keep credentials in env vars.

Then investigate with the loop:

1. **Read error messages completely** — every line, every frame in the stack trace
2. **Check recent changes** — `git log --oneline -10`, `git diff HEAD~3`
3. **Trace data flow backward** — start from the error, work backward through the call chain

For multi-component systems, add diagnostic instrumentation at each layer:
```python
print(f"[DEBUG] layer={layer} input={input!r} state={state!r}")
```

### Phase 2: Pattern Analysis

1. **Find working examples** — is there a similar case that works?
2. **Compare against references** — read the docs for the function/API involved (completely, not skimming)
3. **Identify differences** — what's different between working and broken?
4. **Understand dependencies** — trace imports, configs, environment

### Phase 3: Hypothesis and Testing

1. Form a **single hypothesis**: "I think X is root cause because Y"
2. Test **one variable at a time** — change one thing, observe result
3. Verify before continuing — did the hypothesis hold?

If the hypothesis was wrong, go back to Phase 1 with new information. Don't stack hypotheses.

### Phase 4: Implementation

1. Turn the Phase 1 loop into a failing regression test (if it isn't one already)
2. Implement the fix — address root cause, not symptoms
3. Verify the test passes
4. Run the full suite — no regressions

## Red Flags: Stop and Reconsider

- **3+ failed fix attempts** on the same issue — question the architecture, not just the code
- **Fixing symptom, not cause** — if the fix is "add a null check here," ask why it's null
- **Cascading failures** — one fix causes another break, which causes another — step back
- **"It works on my machine"** — investigate environment differences, don't ignore

## Root Cause Tracing

When an error appears deep in a stack trace:

1. **Observe the symptom** — what error, where
2. **Find immediate cause** — what code directly produces this error
3. **Ask: what called this?** — trace up the call chain
4. **Keep tracing** — until you reach the original trigger
5. **Fix at the right level** — usually closer to the origin than the symptom

## Defense in Depth

For recurring classes of bugs, add validation at multiple layers:

1. **Entry point** — reject invalid input at API/UI boundary
2. **Business logic** — validate data makes sense in context
3. **Environment guards** — prevent dangerous operations in wrong context
4. **Debug instrumentation** — capture context for forensics when things go wrong
