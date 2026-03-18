# NE Claude Plugin Marketplace

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A curated marketplace of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — extending it with development workflows, task tracking, code review, and integrations.

> **Important:** Review any plugin before installing. Plugins may include MCP servers, hooks, and scripts that execute on your machine. We cannot guarantee that third-party plugins will work as intended.

## Table of Contents

- [Installation](#installation)
- [Available Plugins](#available-plugins)
- [Plugin Structure](#plugin-structure)
- [Contributing](#contributing)
- [Development](#development)
- [License](#license)

## Installation

Install any plugin directly from Claude Code:

```
/plugin install {plugin-name}@ne-claude-plugins
```

Browse available plugins:

```
/plugin > Discover
```

## Available Plugins

### Internal Plugins

Developed and maintained by [Nextera Labs](https://github.com/nexteralabs).

| Plugin | Type | Description |
|--------|------|-------------|
| [**superdev**](plugins/superdev/) | commands, agents, skills | Supercharged dev workflow — ticket to PR with TDD, subagent-driven implementation, multi-agent code review, and task tracking |
| [**jira-workflow**](plugins/jira-workflow/) | commands, skills | Jira ticket management — view, start, complete, log work, and manage sprints |
| [**code-audit**](plugins/code-audit/) | commands, agents | Multi-agent code audit with security scanning and logic analysis |
| [**deploy-guard**](plugins/deploy-guard/) | hooks | Pre-deployment validation — secret scanning in writes and push protection |
| [**obsidian-vault**](plugins/obsidian-vault/) | mcp | Read and write notes in your Obsidian vault from Claude Code |
| [**discord-notify**](plugins/discord-notify/) | mcp, commands | Send messages to Discord channels via bot API with guided setup |

### Plugin Details

#### superdev

The flagship plugin. Full development lifecycle driven by `/dev`:

```
/dev              # Full workflow: pick task > design > plan > implement > review > PR
/dev start        # Pick up a task from Jira or Obsidian and design the approach
/dev plan         # Write an implementation plan with TDD steps
/dev code         # Implement with subagent-driven development
/dev review       # Multi-agent code review (security, logic, spec compliance)
/dev pr           # Create PR, update task status, notify Discord
```

Includes 3 specialized agents (implementer, spec-reviewer, code-reviewer) and reference docs on TDD, systematic debugging, and verification practices. Integrates with Jira and Obsidian for task tracking.

#### jira-workflow

```
/jira list                    # List sprint tickets
/jira view KAN-123            # View ticket details
/jira start KAN-123           # Create branch + transition to In Progress
/jira done KAN-123            # Transition to Done/In Review
/jira comment KAN-123 "msg"   # Add a comment
/jira log KAN-123 2h          # Log time
/jira-setup                   # Configure Jira credentials
```

#### code-audit

```
/review-pr 123                # Review a PR by number
/review-pr                    # Review current branch's PR
```

Dispatches parallel security and logic review agents with confidence-scored findings.

#### deploy-guard

Hook-based plugin that runs automatically:

- **Secret scanning** — blocks writes containing API keys, tokens, passwords, and private keys
- **Push protection** — warns on uncommitted changes, blocks force-push to main/master

#### obsidian-vault

MCP server connecting Claude Code to your Obsidian vault. Requires `OBSIDIAN_VAULT_PATH` environment variable.

#### discord-notify

```
/discord general "Build passed!"   # Send a message to #general
/discord-setup                     # Configure bot token and guild ID
```

## Plugin Structure

Every plugin follows the standard Claude Code plugin format:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── commands/            # Slash commands (optional)
│   └── command-name.md
├── agents/              # Agent definitions (optional)
│   └── agent-name.md
├── skills/              # Skill definitions (optional)
│   └── skill-name/
│       └── SKILL.md
├── hooks/               # Event-driven hooks (optional)
│   └── hooks.json
└── README.md            # Documentation (required)
```

### Frontmatter Reference

Commands, agents, and skills use YAML frontmatter:

**Commands** — require `description`:
```yaml
---
description: Short description shown in /help
argument-hint: <arg> [optional]
allowed-tools: [Read, Glob, Grep, Bash]
---
```

**Agents** — require `name` and `description`:
```yaml
---
name: agent-name
description: When to use this agent
model: sonnet
tools: Read, Glob, Grep
---
```

**Skills** — require `description`:
```yaml
---
name: skill-name
description: When Claude should invoke this skill
version: 1.0.0
---
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the full guide.

**Quick start:**

1. Fork the repo
2. Add your plugin under `external_plugins/`
3. Register it in `.claude-plugin/marketplace.json`
4. Validate frontmatter: `bun .github/scripts/validate-frontmatter.ts`
5. Open a pull request

You can also submit a plugin via the [Plugin Submission](https://github.com/nexteralabs/ne-claude-plugins/issues/new?template=plugin-submission.yml) issue template.

## Development

### Validation

All commands, agents, and skills are validated for correct YAML frontmatter on every PR:

```bash
bun .github/scripts/validate-frontmatter.ts
```

### Testing Locally

Test a plugin in development:

```bash
claude --plugin-dir /path/to/your-plugin
```

### Repository Structure

```
ne-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry
├── plugins/                      # Internal plugins (Nextera Labs)
├── external_plugins/             # Community plugins
└── .github/
    ├── scripts/                  # Validation tooling
    └── workflows/                # CI automation
```

## Documentation

For more information on developing Claude Code plugins, see the [official documentation](https://docs.anthropic.com/en/docs/claude-code/plugins).

## License

This project is licensed under the [MIT License](LICENSE).
