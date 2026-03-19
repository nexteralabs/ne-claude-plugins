# NE Claude Plugin Marketplace

A curated marketplace of Claude Code plugins — installable via `/plugin install {name}@ne-claude-plugins`.

## Structure

- **`/plugins`** — Internal plugins developed and maintained by NE
- Community plugins also go under `/plugins`
- **`.claude-plugin/marketplace.json`** — Master registry of all plugins

## Plugin Anatomy

Each plugin follows the standard Claude Code plugin structure:
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server config (optional)
├── commands/            # Slash commands (optional)
├── agents/              # Agent definitions (optional)
├── skills/              # Skill definitions (optional)
├── hooks/               # Hook automation (optional)
│   └── hooks.json
└── README.md
```

## Conventions

- Plugin names are lowercase kebab-case
- All commands/agents/skills must have valid YAML frontmatter
- Commands require `description` in frontmatter
- Agents require `name` and `description` in frontmatter
- Skills require `description` in frontmatter (in SKILL.md)
- Hooks use `${CLAUDE_PLUGIN_ROOT}` for portable paths

## Validation

```bash
bun .github/scripts/validate-frontmatter.ts
```

## Adding a Plugin

1. Create the plugin directory under `plugins/`
2. Add `.claude-plugin/plugin.json` with name, description, author
3. Add commands/agents/skills/hooks as needed
4. Register the plugin in `.claude-plugin/marketplace.json`
5. Run validation and submit a PR

## Project Configuration

- **Language:** Markdown, TypeScript (validation scripts)
- **Package manager:** bun
- **Test/validation:** `bun .github/scripts/validate-frontmatter.ts`
- **Build command:** none
- **Ticket system:** none

## Development Workflow

This project uses the codesmith workflow. Start any dev task by describing what you want to build — the workflow drives automatically through brainstorm → workspace → plan → implement → review → ship.

## Core Principles

### Plan Mode Default

Enter plan mode for any non-trivial task (3+ steps or architectural decisions). If something goes wrong, STOP and re-plan immediately — don't keep pushing. Use plan mode for verification steps, not just building. Write detailed specs upfront to reduce ambiguity.

### Subagent Strategy

Use subagents frequently to keep the main context window clean. Offload research, exploration, and parallel analysis to subagents. For complex problems, throw more compute via subagents. Assign one task per subagent for focused execution.

### Memory-Driven Learning

When the user corrects your approach, consider whether the lesson is a general pattern about tools, techniques, or workflow preferences that transfers across any codebase — or a project-specific fix already captured in the code. Only offer to save general patterns as memories. Code fixes belong in the code, not in memory.

### Verification Before Done

Never mark a task complete without proving it works. Diff behavior between main and your changes when relevant. Ask yourself: "Would a staff engineer approve this?" Run tests, check logs, and demonstrate correctness.

### Demand Elegance (Balanced)

For non-trivial changes, ask: "Is there a more elegant solution?" If a fix feels hacky, ask: "Knowing everything I know now, implement the elegant solution." Skip this for simple fixes — don't over-engineer. Challenge your own work before presenting it.

### Autonomous Bug Fixing

When given a bug report: just fix it. Use logs, errors, and failing tests to diagnose. Require zero context switching from the user. Fix failing CI tests automatically.

## Task Management

1. **Plan First** — Write the plan in `.claude/tasks/todo.md` with checkable items
2. **Verify Plan** — Confirm the plan before implementation
3. **Track Progress** — Mark items complete as you go
4. **Explain Changes** — Provide a high-level summary at each step
5. **Document Results** — Add a review section to `.claude/tasks/todo.md`
6. **Capture Lessons** — When corrected, ask the user if they want to save the pattern as a memory

## Core Rules

### Simplicity First
Make every change as simple as possible and minimize code impact. Three clear lines beat a premature abstraction. No feature flags for hypotheticals. No helpers for one-time operations.

### No Laziness
Find root causes. Avoid temporary fixes. Maintain senior-level engineering standards. Never say "should work" — prove it.
