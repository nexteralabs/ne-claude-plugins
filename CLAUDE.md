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
