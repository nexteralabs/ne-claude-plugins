---
description: Set up Jira credentials and project config for the jira-workflow plugin
allowed-tools: [Read, Write, Edit, Bash]
---

# Jira Setup

Configure Jira credentials and project settings so the jira-workflow plugin can manage tickets.

## Step 1 — Check existing config

```bash
cat ~/.claude/jira.env 2>/dev/null
```

If the file exists and has `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_BASE_URL` set, tell the user:
> "Jira credentials already configured. Want to reconfigure? (yes / no)"

If they say no, skip to Step 4 (project config).

## Step 2 — Guide the user through API token setup

Present this to the user:

> **To use this plugin, you need a Jira API token.**
>
> ### Create an API Token
> 1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
> 2. Click **Create API token**
> 3. Give it a label (e.g., "Claude Code")
> 4. Copy the token
>
> ### What I'll need from you
> 1. Your **Jira email** (the one you log in with)
> 2. The **API token** you just created
> 3. Your **Jira base URL** (e.g., `https://company.atlassian.net`)
>
> Paste your **Jira email** when ready.

Wait for the email. Then ask for the API token. Then ask for the base URL.

## Step 3 — Write credentials

```bash
mkdir -p ~/.claude
```

Write `~/.claude/jira.env`:
```
JIRA_EMAIL={email}
JIRA_API_TOKEN={token}
JIRA_BASE_URL={base_url}
```

Do NOT echo the token in any output. Confirm:
> "Credentials saved to `~/.claude/jira.env`."

## Step 4 — Project config

Check the current project's `CLAUDE.md` for a `## Task Tracking` section.

If missing, ask:
> "What's the Jira project key for this repo? (e.g., KAN, PROJ, ENG)"

Then write to CLAUDE.md:
```markdown
## Task Tracking
- source: jira
- base-url: {base_url from jira.env}
- project-key: {project_key}
```

If CLAUDE.md doesn't exist, create it with just this section.

## Step 5 — Test the connection

Try to list current user's tickets using the Atlassian MCP if available:

Use MCP tool `mcp__atlassian__searchJiraIssuesUsingJql` with JQL:
```
assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC
```

If MCP is not available, fall back to curl:
```bash
source ~/.claude/jira.env
curl -sf -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/search?jql=assignee%3DcurrentUser()%20AND%20statusCategory%21%3DDone&maxResults=5" \
  | python3 -c "import sys,json; issues=json.load(sys.stdin)['issues']; [print(f'{i[\"key\"]} — {i[\"fields\"][\"summary\"]}') for i in issues]"
```

If it succeeds, show the tickets and confirm setup is complete.

If it fails, show the error and suggest:
- Verify email and token are correct
- Check the base URL matches your Jira instance
- Ensure the API token has not expired
- Re-run `/jira-setup` to reconfigure
