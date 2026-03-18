# PR Review Plugin

Multi-agent pull request review with security, logic, style, and test coverage analysis.

## Usage

```
/review-pr 123
/review-pr https://github.com/org/repo/pull/123
/review-pr          # reviews current branch's PR
```

## Agents

- **Security Reviewer** — Scans for vulnerabilities and unsafe patterns
- **Logic Reviewer** — Checks correctness, edge cases, and error handling

## Output

Structured review with confidence-scored findings categorized as critical issues, suggestions, and nits.

## License

MIT
