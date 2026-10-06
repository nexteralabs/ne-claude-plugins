# doc-writer

Write and update documentation that is clear, scannable and professional: structured sections, tables where comparison helps, layouts that fit the screen, no decoration.

## What it does

- **Core rules** for every medium: audience and doc type first, lead with a summary, heading discipline, table and column limits (≤ 5 table columns, ≤ 3 layout columns), callouts only for real risks, no emoji or decorative colour, plain active voice.
- **Media rules**, loaded only when needed:
  - **Confluence** — storage-format snippets for layouts, tables, panels, status lozenges, code, expand, TOC; width budget; safe create/update procedure (version bump, macro preservation).
  - **Markdown** — repo docs, READMEs, Git wikis.
- **Doc-type skeletons**: overview, how-to, runbook, reference, decision record, onboarding.
- **Live diagrams**: pairs with the `drawio` skill — diagrams are linted, then embedded as editable diagrams through ZenUML "Graph (DrawIO)" (default, full or Lite auto-detected) or the draw.io app. Never static PNGs.
- **Page linter**: `confluence.py lint` checks a page body against the rules (table width, callouts, emoji, colours, layouts, diagram width, Markdown leftovers) before publishing.
- **Update mode**: minimal, structure-preserving edits with a summary of what changed.

## Installation

```
/plugin install doc-writer@ne-claude-plugins
```

## Usage

```
Document the payments service in Confluence under the Platform space
Update the "Deploy pipeline" Confluence page for the new staging step
Write a runbook for rotating the API keys
```

## Plugin Structure

```
doc-writer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── doc-writer/
│       ├── SKILL.md              # core rules
│       ├── scripts/
│       │   └── confluence.py     # lint / create / get / put / attach / detect / drawio / zenuml
│       └── references/
│           ├── confluence.md     # Confluence rules + storage format
│           ├── markdown.md       # Markdown rules
│           └── doc-types.md      # page skeletons per doc type
└── README.md
```

Adding a medium: create `references/<medium>.md` with its rules and checklist, and add a row to the medium table at the top of `SKILL.md`.
