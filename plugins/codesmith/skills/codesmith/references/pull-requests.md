# Pull Requests

A PR is a communication tool. Its job is to give every person who touches it (reviewer, QA, on-call, future developer) exactly what they need to do their job. A PR that requires the reviewer to read every line of diff to understand what's happening has failed.

## PR Title

Follow the same Conventional Commits format as commit messages:

```
feat(auth): add JWT refresh token rotation
fix(checkout): prevent double charge on retry
refactor(db): extract query builder from repository
```

If there's a Jira ticket, prepend the key:

```
KAN-234 feat(auth): add JWT refresh token rotation
```

## PR Body

### Problem

What was wrong or missing before this change. Be specific. Not "improve auth" but "users get logged out after 15 minutes because the access token expires and there's no refresh mechanism." This section answers **why this PR exists**.

If there's a Jira ticket, link it here. But don't rely on the ticket alone. The PR should be self-contained. Tickets get archived, moved, deleted. The PR stays in git history.

### Approach

The design decision you made and why. If you considered alternatives, mention what you rejected and why. This is where you explain your thinking so the reviewer doesn't have to reverse-engineer it from the diff.

Bad: "Added refresh token logic."
Good: "Implemented token rotation using a sliding window. Considered storing refresh tokens in the database but went with signed JWTs to avoid a database call on every token refresh. Tradeoff: tokens can't be individually revoked without a blocklist."

### Key Changes

The important parts of the diff. Not every file, just the ones that matter. Point the reviewer to where the real decisions are, where the risk is, where they should spend their time.

```
- `src/auth/token.ts` - New refresh token generation and validation logic (core change)
- `src/middleware/auth.ts` - Updated to handle token rotation on expired access tokens
- `src/db/migrations/003_add_refresh_tokens.sql` - New table for token blocklist
- `tests/auth/token.test.ts` - 12 new tests covering rotation, expiry, and revocation
```

Mention anything surprising or non-obvious. If you made a choice that looks wrong at first glance, explain it here before the reviewer flags it.

### Breaking Changes

If this PR changes behavior that other code, services, or users depend on:

- What breaks
- Who is affected (other services, API consumers, end users)
- Migration path (what do they need to do)
- Is this behind a feature flag

If nothing breaks, skip this section. Don't write "None" for the sake of having a section.

### Testing

Two parts: what you tested, and what QA should test.

**What was tested:**
- Test suite results: all passing, new tests added, coverage delta
- Manual testing you did and what you verified
- Edge cases you specifically tested

**QA testing guide:**
- Prerequisites (test account, specific data, environment setup)
- Steps to reproduce the original problem (so QA can verify it's fixed)
- Steps to verify the new behavior works
- Areas of risk to pay extra attention to (what could break that isn't covered by automated tests)

```
### QA Testing Guide

**Verify the fix:**
1. Log in with test account
2. Wait 15 minutes (or set token expiry to 30s in dev config)
3. Perform any action
4. Should stay logged in (previously would redirect to login)

**Risk areas:**
- Concurrent requests during token rotation (try rapid-clicking while token expires)
- Multiple tabs open simultaneously
- Mobile app behavior (uses same auth endpoint)
```

### Deployment Notes

Anything the person deploying needs to know:

- Database migrations that need to run
- Environment variables to add
- Feature flags to enable
- Services that need restarting
- Order of deployment (if multiple services)
- Rollback instructions if something goes wrong

Skip this for straightforward deploys.

### Screenshots

If the change is visual, include before/after. If it's an API change, include example request/response. If it's a CLI change, include terminal output. Show, don't describe.

### Follow-up

Intentional scope boundaries. What you chose NOT to do in this PR and why. If there's planned follow-up work, mention it so reviewers don't ask "but what about X?"

```
Out of scope (planned for next sprint):
- Token revocation endpoint (KAN-235)
- Rate limiting on refresh endpoint (KAN-236)
```

## PR Hygiene

**Size.** A PR should be reviewable in one sitting. If it touches more than 400 lines of logic (excluding tests, generated code, config), consider splitting it. Large PRs get rubber-stamped, not reviewed.

**Draft PRs.** Use drafts for work-in-progress that you want early feedback on. Don't request review on a draft.

**Self-review.** Before requesting review, read your own diff as if you were the reviewer. You'll catch half the issues yourself. Check:
- No debug code left behind (console.log, TODO hacks, commented-out code)
- No unrelated changes mixed in
- Tests actually test the behavior, not the implementation
- Commit history is clean (squash WIP commits)

**One concern per PR.** A bug fix and a refactor are two PRs. A feature and a dependency upgrade are two PRs. Mixing concerns makes review harder and rollback impossible.
