<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/nexteralabs/ne-claude-plugins" alt="License" /></a>
  <a href="https://github.com/nexteralabs/ne-claude-plugins/releases"><img src="https://img.shields.io/github/v/release/nexteralabs/ne-claude-plugins?display_name=tag" alt="Release" /></a>
  <img src="https://img.shields.io/github/last-commit/nexteralabs/ne-claude-plugins" alt="Last Commit" />
  <img src="https://img.shields.io/badge/plugins-7-brightgreen" alt="Plugins" />
</p>

<h1 align="center">NextEra Labs Claude Plugins</h1>

A curated marketplace of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), extending it with development workflows, code review, and integrations.

> **Important:** Review any plugin before installing. Plugins may include MCP servers, hooks, and scripts that execute on your machine. We cannot guarantee that third-party plugins will work as intended.

---

# CodeSmith

A development workflow that enforces spec refinement, TDD, and simplicity at every step.<br>
Fast code that breaks costs more than thoughtful code that ships clean.

<table>
<tr>
<td width="50%">

### Spec first, code second
No ambiguity survives the design phase. Requirements are clarified, edge cases surfaced, and scope locked before a single line is written.

### TDD by default
Write a failing test first. Then make it pass. Then refactor. No production code exists without a test that demanded it.

</td>
<td width="50%">

### KISS over complexity
Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations. Minimum code that works.

### Multi-agent review
Security, logic, and spec compliance reviewed by dedicated agents that catch what humans skip.

</td>
</tr>
</table>

> The skill triggers automatically when you start any dev work. It drives the full lifecycle: understand the task, refine the spec, plan with TDD steps, implement test-first with subagents, review with parallel agents, and ship a clean PR. Jira integration is built in when the Atlassian MCP is available.

---

# SkillForge

Your skills get smarter every time you run this.<br>
Point it at any skill, define what "good output" looks like, and it runs an autonomous experiment loop until the failure rate disappears.

<table>
<tr>
<td width="50%">

### Parallel execution
N runner agents spawn simultaneously — each gets the skill and a test input, executes it in isolation, returns clean output. A full 5-run experiment takes the same wall time as a single run.

### Blind scoring
A separate grader agent scores every output without knowing what mutation was attempted. No self-grading bias. Strict: if unsure, FAIL.

</td>
<td width="50%">

### Checkpoint/resume
Artifacts are saved after every experiment. If the loop gets interrupted, pick up exactly where you left off — no reruns, no lost progress.

### Eval discriminability
Before the loop starts, SkillForge flags evals that trivially pass or fail 100% of the time. Prevents wasting 50 experiments optimizing against a broken signal.

</td>
</tr>
</table>

> Say "this skill is flaky" or "run skillforge on my X skill." SkillForge establishes a baseline, runs an autonomous mutation loop — one targeted change at a time — and delivers a terminal summary with the score improvement, top changes, and a merge prompt. The original SKILL.md is never touched until you approve.

---

## All Plugins

Developed and maintained by [Nextera Labs](https://github.com/nexteralabs).

| Plugin | Type | Description |
|--------|------|-------------|
| [**codesmith**](plugins/codesmith/) | skill, agents | Dev workflow with spec refinement, TDD, KISS, multi-agent review, ticket to PR |
| [**skillforge**](plugins/skillforge/) | skill, agents | Autonomous skill optimizer — parallel execution, blind grading, checkpoint/resume |
| [**drawio**](plugins/drawio/) | skill | Create and edit draw.io diagrams: flowcharts, architecture, sequence diagrams, and more |
| [**code-audit**](plugins/code-audit/) | skill, agents | Multi-agent code review with parallel security and logic analysis |
| [**secret-guard**](plugins/secret-guard/) | hooks | Pre-commit guard — scans staged files for leaked secrets before committing |
| [**obsidian-vault**](plugins/obsidian-vault/) | mcp | Read and write notes in your Obsidian vault from Claude Code |
| [**discord-notify**](plugins/discord-notify/) | mcp, commands | Send messages to Discord channels via bot API with guided setup |

### skillforge

Autonomously optimizes any Claude Code skill through a scored mutation loop. Spawns parallel runner agents to execute the skill, parallel grader agents to score outputs blindly, and keeps only mutations that improve the score. Supports checkpoint/resume, parallel candidate testing, and an eval discriminability check before the loop starts. Ends with a terminal summary and a prompt to merge the improved skill back into the original.

### code-audit

Ask Claude to review your code, a PR, or your current changes. The skill dispatches parallel security and logic review agents, then aggregates findings with confidence scores: critical issues, suggestions, and nits. No commands to remember, just say "review my code" or "check this PR."

### secret-guard

Pre-commit hook that scans `git diff --cached` for API keys, tokens, passwords, private keys, and cloud credentials. Blocks the commit if anything is found. Zero overhead on all other commands.

### obsidian-vault

MCP server connecting Claude Code to your Obsidian vault. Requires `OBSIDIAN_VAULT_PATH` environment variable.

### discord-notify

Send messages to Discord channels. The skill detects when you need to notify a channel and handles it. Just say "send a message to #general." Requires `~/.claude/discord.env` with bot token and guild ID (run `/discord-setup` for guided configuration).

### drawio

Ask Claude to create any kind of diagram: flowcharts, architecture diagrams, sequence diagrams, swimlanes, ER diagrams, network maps. The skill triggers whenever you want to visualize something and generates `.drawio` XML files you can open in draw.io or VS Code.

---

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
