# Jira Workflow Plugin

Manage your Jira tickets, sprints, and development workflow directly from Claude Code.

## Setup

```
/jira-setup
```

Walks you through creating a Jira API token, configuring credentials, and setting the project key. Credentials are stored in `~/.claude/jira.env`.

## Usage

- `/jira list` — List your current sprint tickets
- `/jira view KAN-123` — View ticket details
- `/jira start KAN-123` — Start work (branch + transition)
- `/jira done KAN-123` — Complete work (transition + PR)
- `/jira comment KAN-123 "message"` — Add a comment
- `/jira log KAN-123 2h` — Log time

## License

MIT
