# Contributing to NE Claude Plugins

Thank you for your interest in contributing! This guide explains how to add plugins, report issues, and submit improvements.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ne-claude-plugins.git
   cd ne-claude-plugins
   ```
3. Create a feature branch:
   ```bash
   git checkout -b add-my-plugin
   ```

## Submitting a Plugin

Community plugins live under `external_plugins/`. To submit one:

1. Create your plugin directory under `external_plugins/your-plugin-name/`
2. Follow the standard plugin structure (see README)
3. Add your plugin entry to `.claude-plugin/marketplace.json`
4. Include a clear `README.md` with setup instructions
5. Open a pull request

### plugin.json (required)

```json
{
  "name": "your-plugin-name",
  "description": "Clear, one-line description of what your plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

### marketplace.json entry

Add your plugin to the `plugins` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "description": "Same description as plugin.json",
  "version": "1.0.0",
  "author": { "name": "Your Name" },
  "source": "./external_plugins/your-plugin-name",
  "category": "development"
}
```

Valid categories: `development`, `productivity`, `integrations`, `devops`.

## Validating Frontmatter

All commands, agents, and skills require valid YAML frontmatter. Validate before submitting:

```bash
bun .github/scripts/validate-frontmatter.ts
```

### Frontmatter Requirements

**Commands** require `description`. **Agents** require `name` and `description`. **Skills** require `description`.

## Testing Your Plugin Locally

```bash
claude --plugin-dir /path/to/your-plugin
```

## Plugin Quality Checklist

- [ ] Has a clear, descriptive `plugin.json`
- [ ] Includes a `README.md` with setup instructions
- [ ] Has valid frontmatter on all commands, agents, and skills
- [ ] Does not include hardcoded secrets or credentials
- [ ] Uses `${CLAUDE_PLUGIN_ROOT}` for portable file paths in hooks
- [ ] Uses environment variables for any required credentials
- [ ] Documents all required setup steps

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(plugin-name): add new command for X
fix(plugin-name): correct frontmatter validation
docs(plugin-name): update setup instructions
chore: update marketplace.json
```

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.
