# drawio

Create and edit [draw.io](https://www.drawio.com/) diagrams (`.drawio` XML files) directly from Claude Code — no GUI needed.

## What it does

This skill lets Claude generate production-quality draw.io diagrams from natural language. Supports:

- **Flowcharts** — decision trees, process flows
- **Architecture diagrams** — system components, service maps
- **Sequence diagrams** — request/response flows
- **Swimlane diagrams** — cross-team processes
- **ER diagrams** — database schemas and relationships
- **Network diagrams** — infrastructure topology
- **Mind maps** — brainstorming and idea organization
- **Org charts** — team structures

## Installation

```
/plugin install drawio@ne-claude-plugins
```

## Usage

Just ask Claude to create a diagram:

```
Draw an architecture diagram for a microservices system with an API gateway, auth service, and database
```

```
Create a flowchart showing the CI/CD pipeline
```

```
Make a sequence diagram for the OAuth2 authorization code flow
```

The skill triggers automatically when you mention diagrams, flowcharts, architecture visuals, or ask to "draw", "diagram", "visualize", or "map out" something.

## Output

Generates `.drawio` XML files that can be:

- Opened in [draw.io](https://www.drawio.com/) desktop or web
- Opened in VS Code with the [Draw.io Integration](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension
- Exported to PNG via the draw.io CLI
- Committed to version control alongside your code

## Plugin Structure

```
drawio/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── drawio/
│       └── SKILL.md
└── README.md
```
