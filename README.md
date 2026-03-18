<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/nexteralabs/ne-claude-plugins" alt="License" /></a>
  <a href="https://github.com/nexteralabs/ne-claude-plugins/releases"><img src="https://img.shields.io/github/v/release/nexteralabs/ne-claude-plugins" alt="Release" /></a>
  <img src="https://img.shields.io/github/last-commit/nexteralabs/ne-claude-plugins" alt="Last Commit" />
  <img src="https://img.shields.io/badge/plugins-6-brightgreen" alt="Plugins" />
  <img src="https://img.shields.io/badge/claude--code-compatible-blueviolet" alt="Claude Code Compatible" />
</p>

<h1 align="center">NextEra Labs Claude Plugins</h1>

A curated marketplace of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), extending it with development workflows, code review, and integrations.

> **Important:** Review any plugin before installing. Plugins may include MCP servers, hooks, and scripts that execute on your machine. We cannot guarantee that third-party plugins will work as intended.

---

# superdev

An opinionated development workflow that enforces good engineering practices. Fast code that breaks costs more than thoughtful code that ships clean.

**Refine specs before writing code.** No ambiguity survives the design phase. Requirements are clarified, edge cases surfaced, and scope locked before a single line is written.

**TDD by default.** Write a failing test first. Then make it pass. Then refactor. No production code exists without a test that demanded it.

**KISS over complexity.** Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations. The right amount of code is the minimum that works.

**Multi-agent review before merge.** Security, logic, and spec compliance reviewed by dedicated agents that catch what humans skip.

The skill triggers automatically when you start any dev work: building a feature, fixing a bug, implementing a ticket. It drives the full lifecycle from understanding the task, through spec refinement, TDD implementation with subagents, multi-agent code review, all the way to a clean PR. Jira integration is built in when the Atlassian MCP is available, no setup commands needed.

---

## All Plugins

Developed and maintained by [Nextera Labs](https://github.com/nexteralabs).

| Plugin | Type | Description |
|--------|------|-------------|
| [**superdev**](plugins/superdev/) | skill, agents | Opinionated dev workflow with spec refinement, TDD, KISS, multi-agent review, ticket to PR |
| [**code-audit**](plugins/code-audit/) | skill, agents | Multi-agent code review with parallel security and logic analysis |
| [**deploy-guard**](plugins/deploy-guard/) | hooks | Pre-deployment validation with secret scanning and push protection |
| [**obsidian-vault**](plugins/obsidian-vault/) | mcp | Read and write notes in your Obsidian vault from Claude Code |
| [**discord-notify**](plugins/discord-notify/) | mcp, commands | Send messages to Discord channels via bot API with guided setup |
| [**drawio**](plugins/drawio/) | skill | Create and edit draw.io diagrams: flowcharts, architecture, sequence diagrams, and more |

### code-audit

Ask Claude to review your code, a PR, or your current changes. The skill dispatches parallel security and logic review agents, then aggregates findings with confidence scores: critical issues, suggestions, and nits. No commands to remember, just say "review my code" or "check this PR."

### deploy-guard

Hook-based plugin that runs automatically:

- **Secret scanning** blocks writes containing API keys, tokens, passwords, and private keys
- **Push protection** warns on uncommitted changes, blocks force-push to main/master

### obsidian-vault

MCP server connecting Claude Code to your Obsidian vault. Requires `OBSIDIAN_VAULT_PATH` environment variable.

### discord-notify

Send messages to Discord channels. The skill detects when you need to notify a channel and handles it. Just say "send a message to #general." Requires `~/.claude/discord.env` with bot token and guild ID (run `/discord-setup` for guided configuration).

### drawio

Ask Claude to create any kind of diagram: flowcharts, architecture diagrams, sequence diagrams, swimlanes, ER diagrams, network maps. The skill triggers whenever you want to visualize something and generates `.drawio` XML files you can open in draw.io or VS Code.

---

## Plugin Structure

Every plugin follows the standard Claude Code plugin format:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── skills/              # Skill definitions (optional)
│   └── skill-name/
│       └── SKILL.md
├── agents/              # Agent definitions (optional)
│   └── agent-name.md
├── hooks/               # Event-driven hooks (optional)
│   └── hooks.json
└── README.md            # Documentation (required)
```

### Frontmatter Reference

Skills and agents use YAML frontmatter:

**Skills** (require `description`):
```yaml
---
name: skill-name
description: When Claude should invoke this skill
version: 1.0.0
---
```

**Agents** (require `name` and `description`):
```yaml
---
name: agent-name
description: When to use this agent
model: sonnet
tools: Read, Glob, Grep
---
```

<details>
<summary><strong>Contributing</strong></summary>

We welcome contributions! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the full guide.

**Quick start:**

1. Fork the repo
2. Add your plugin under `plugins/`
3. Register it in `.claude-plugin/marketplace.json`
4. Validate frontmatter: `bun .github/scripts/validate-frontmatter.ts`
5. Open a pull request

You can also submit a plugin via the [Plugin Submission](https://github.com/nexteralabs/ne-claude-plugins/issues/new?template=plugin-submission.yml) issue template.

</details>

<details>
<summary><strong>Development</strong></summary>

### Validation

All skills and agents are validated for correct YAML frontmatter on every PR:

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
└── .github/
    ├── scripts/                  # Validation tooling
    └── workflows/                # CI automation
```

For more information on developing Claude Code plugins, see the [official documentation](https://docs.anthropic.com/en/docs/claude-code/plugins).

</details>

<details>
<summary><strong>Installation</strong></summary>

Install any plugin directly from Claude Code:

```
/plugin install {plugin-name}@ne-claude-plugins
```

Browse available plugins:

```
/plugin > Discover
```

</details>

<details>
<summary><strong>License</strong></summary>

This project is licensed under the [MIT License](LICENSE).

Copyright 2026 Nextera Labs.

</details>
