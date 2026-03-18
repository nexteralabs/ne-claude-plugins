---
name: jira-workflow
description: Use this skill when the user mentions Jira tickets (e.g., "KAN-123"), asks about sprint work, wants to start or finish a task, or discusses ticket management. Provides context-aware Jira integration patterns.
version: 1.0.0
---

# Jira Workflow Skill

Provides intelligent Jira integration within Claude Code development workflows.

## When This Skill Applies

- User references a Jira ticket ID (e.g., KAN-123, PROJ-456)
- User asks to start, finish, or check on work items
- User asks about sprint status or backlog
- User wants to link commits or PRs to tickets

## Workflow Patterns

### Starting Work on a Ticket

1. Fetch ticket details from Jira
2. Create a feature branch: `<ticket-id>/<short-description>`
3. Transition ticket to "In Progress"
4. Write task context to `.claude/current-task.md`

### Completing Work

1. Verify all changes are committed
2. Create a pull request with ticket reference in the title
3. Transition ticket to "In Review"
4. Add a comment with the PR link

### Branch Naming Convention

```
KAN-123/add-user-authentication
PROJ-456/fix-pagination-bug
```

### Commit Message Convention

Reference the ticket ID in commit messages:
```
KAN-123: Add user authentication endpoint

Implements JWT-based auth with refresh tokens.
```

## Integration Priority

1. **Atlassian MCP** — Preferred when available (mcp__atlassian__* tools)
2. **Jira CLI** — Fallback if `jira` command is installed
3. **REST API** — Last resort via curl to Jira Cloud API
