---
description: Interact with Jira — view tickets, update status, log work, and manage sprints
argument-hint: <action> [ticket-id] [options]
allowed-tools: [Read, Bash, Grep, Glob]
---

# Jira Workflow Command

Manage your Jira tickets and sprint workflow without leaving Claude Code.

## Arguments

The user invoked this command with: $ARGUMENTS

## Pre-flight: Check credentials

```bash
test -f ~/.claude/jira.env && grep -q "JIRA_API_TOKEN=." ~/.claude/jira.env && echo "OK" || echo "MISSING"
```

If MISSING, tell the user:
> "Jira credentials not configured. Run `/jira-setup` first."

Stop here.

## Supported Actions

Parse the first argument to determine which action to perform:

### `view <TICKET-ID>`
Fetch and display the ticket details including summary, description, status, assignee, and comments.

### `start <TICKET-ID>`
Transition the ticket to "In Progress", create a git branch named after the ticket, and record the task context in `.claude/current-task.md`.

### `done <TICKET-ID>`
Transition the ticket to "Done" or "In Review". If there are uncommitted changes, prompt the user to commit first.

### `list [sprint|backlog]`
List tickets assigned to the current user. Default to current sprint.

### `comment <TICKET-ID> <message>`
Add a comment to the specified ticket.

### `log <TICKET-ID> <duration>`
Log time worked on a ticket (e.g., `2h`, `30m`).

## Implementation Notes

- Use the Atlassian MCP tools if available (mcp__atlassian__*)
- Fall back to the `jira` CLI or direct REST API via curl if MCP is not configured
- Always confirm destructive actions (transitions, time logging) before executing
