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

## Why order matters

- Tests written after implementation pass immediately — proves nothing
- You might test the wrong thing or miss edge cases
- Test-first forces you to see it fail, proving the test actually catches the bug
- Manual testing is ad-hoc and unrepeatable
