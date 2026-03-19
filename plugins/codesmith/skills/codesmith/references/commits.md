# Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard.

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, semicolons (no logic change) |
| `perf` | Performance improvement |
| `chore` | Build process, tooling, dependencies |
| `ci` | CI/CD configuration |
| `revert` | Reverting a previous commit |

## Breaking Changes

If a commit introduces a breaking change, add `!` after the type or `BREAKING CHANGE:` in the footer:

```
feat(api)!: change authentication endpoint response format

BREAKING CHANGE: /auth/login now returns { token, expiresAt }
instead of { accessToken, refreshToken }. Clients must update
their token handling.
```

## Subject Line

- 50 characters max
- Imperative mood: "add", "fix", "change", not "added", "fixed", "changed"
- No period at the end
- Lowercase after the colon

```
feat(auth): add JWT refresh token rotation
fix(api): handle null response from payment provider
refactor(db): extract query builder from repository
```

## Body

- Explain **why**, not what. The diff shows what changed.
- Wrap at 72 characters
- Separate from subject with a blank line
- Use when the subject alone doesn't explain the reasoning

```
fix(checkout): prevent double charge on retry

The payment gateway returns 200 on duplicate requests but still
processes them. Added idempotency key based on order ID to prevent
charging the customer twice when they hit retry.
```

## Scope

Optional. Use the module, component, or area affected:

```
feat(auth): ...
fix(api/users): ...
refactor(db): ...
test(checkout): ...
```

## Ticket References

If there's a Jira ticket or issue, include it in the footer:

```
feat(notifications): add email digest for weekly summary

Refs: KAN-234
```

## One Commit, One Change

Each commit should be one logical change that can be reverted independently. Tests must pass after every commit.

Bad: "Add login page, fix header bug, update dependencies"
Good: Three separate commits, each self-contained.

## When to Squash

- Multiple "fix typo" or "WIP" commits on the same feature: squash into one clean commit before PR
- Each meaningful step in the implementation: keep separate
- Exploratory commits that were later replaced: squash away
