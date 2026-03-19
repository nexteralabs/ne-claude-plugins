# Test-Driven Development

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

No exceptions. Not for "simple" changes. Not for "obvious" code. Not when you're "almost done."

## RED-GREEN-REFACTOR

### RED: Write the failing test

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

Rules:
- One behavior per test
- Clear, descriptive name
- Real code, not mocks (unless you fully understand the dependency)
- Test the interface, not the implementation

### Verify RED (mandatory)

Run the test. Confirm it **fails** — not errors, fails. The failure message should describe the missing behavior. If it fails because of a typo or import error, fix that first.

### GREEN: Write minimal implementation

```typescript
async function retryOperation<T>(fn: () => T | Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === maxRetries - 1) throw e;
    }
  }
  throw new Error('unreachable');
}
```

Rules:
- Just enough to pass the test — nothing more
- No "improvements" beyond what the test requires
- No YAGNI violations

### Verify GREEN (mandatory)

Run the test. Confirm it passes. Run the full suite — no regressions.

### REFACTOR (only after green)

- Remove duplication
- Improve names
- Extract helpers
- **Keep tests green the entire time**

## Testing Anti-Patterns

### Never test mock behavior

```typescript
// BAD — tests that the mock works, not the code
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});

// GOOD — tests actual behavior
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

### Never add test-only methods to production code

```typescript
// BAD — production class polluted with test plumbing
class Session {
  async destroy() { /* only used in tests */ }
}

// GOOD — test utility
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) await workspaceManager.destroyWorkspace(workspace.id);
}
```

### Never mock without understanding the dependency

If you mock something and the test passes but the mock doesn't match reality — your test proves nothing. Only mock at the boundary (network, filesystem, clock), and verify the mock matches the real interface.

### Integration tests are not optional

Unit tests verify logic. Integration tests verify the system works. Both are required. Don't test a database query by mocking the database — that tests your mock, not your query.

## Testing Strategy

Unit tests and integration tests serve different purposes. You need both, but you need to know which one you're writing and why.

### Unit tests

Test a single function or class in isolation. Fast, focused, and deterministic. Use them for:
- Pure logic: calculations, transformations, parsing, validation
- Business rules: pricing, permissions, eligibility
- State machines: transitions, edge cases, invalid states

Mock only at true boundaries (network, filesystem, clock). If you're mocking the function next door, you're testing your mock, not your code.

### Integration tests

Test that components work together through real interactions. Slower, but catch the bugs that unit tests can't. Required for:
- Database queries — test against a real database, not a mock. Migrations, constraints, and query behavior are where bugs hide.
- API endpoints — test the full request/response cycle through middleware, validation, and serialization.
- External service integrations — at minimum, test the client's error handling against realistic failure modes.
- Multi-step workflows — operations that span multiple services or components need end-to-end verification.

### When to write which

| Situation | Test type | Why |
|-----------|-----------|-----|
| New business logic | Unit | Verify every rule and edge case fast |
| New API endpoint | Integration | Verify the full request path works |
| Database query | Integration | Mocking the database proves nothing |
| Bug fix | Unit first, then integration if the bug crossed boundaries | Prove the specific fix works |
| Refactoring | Existing tests should still pass | If they don't, the refactor changed behavior |

### Coverage targets

Don't chase 100% line coverage — it incentivizes writing tests for getters and config files. Focus on:
- **Decision coverage**: every `if`, `switch`, and `catch` branch exercised
- **Error paths**: failures handled, not just success paths
- **Edge cases**: boundaries, nulls, empty states (see implementer agent's edge case checklist)

### Flaky tests

A test that sometimes passes and sometimes fails is worse than no test — it teaches the team to ignore failures. When you encounter a flaky test:

1. **Reproduce** — run it 10 times in isolation. If it only fails in the full suite, it has a dependency on test ordering or shared state.
2. **Identify the source** — usually one of: timing/race condition, shared mutable state, external dependency (network, clock), non-deterministic data (random IDs, timestamps).
3. **Fix the root cause** — don't add retries or sleeps. Fix ordering dependencies, isolate state, mock the clock, seed random generators.
4. If you can't fix it quickly, skip it with a clear `TODO` and a ticket reference. A skipped test with a tracking issue beats a flaky test that erodes trust.

## Why order matters

- Tests written after implementation pass immediately — proves nothing
- You might test the wrong thing or miss edge cases
- Test-first forces you to see it fail, proving the test actually catches the bug
- Manual testing is ad-hoc and unrepeatable
