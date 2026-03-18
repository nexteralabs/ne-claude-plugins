---
description: Review a pull request with multi-agent analysis — security, logic, style, and test coverage
argument-hint: [pr-number|pr-url]
allowed-tools: [Read, Grep, Glob, Bash, Agent]
---

# PR Review Command

Perform a thorough, multi-agent review of a pull request.

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

1. **Identify the PR**: Parse the argument as a PR number or URL. If no argument, use the current branch's open PR.

2. **Fetch the diff**: Use `gh pr diff <number>` to get the full diff. Also get PR metadata with `gh pr view <number>`.

3. **Spawn parallel review agents** for each concern:

   - **Security Agent**: Check for secrets, injection vulnerabilities, unsafe patterns, OWASP top 10
   - **Logic Agent**: Analyze correctness, edge cases, error handling, race conditions
   - **Style Agent**: Check naming, consistency with codebase conventions, unnecessary complexity
   - **Test Agent**: Evaluate test coverage, missing test cases, test quality

4. **Aggregate results**: Collect all agent findings. Assign confidence scores (high/medium/low).

5. **Present review**: Output a structured review with:
   - Summary of changes
   - Critical issues (high confidence) — must fix
   - Suggestions (medium confidence) — should consider
   - Nits (low confidence) — optional improvements
   - Overall assessment: approve / request changes / needs discussion
