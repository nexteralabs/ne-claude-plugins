---
name: brainstorm
description: "Explore intent, propose multiple approaches, and refine specs before any code is written. Use before any creative or non-trivial development work. Triggers on: 'brainstorm', 'let's think about', 'how should we', 'design this', 'what's the best way to', or when starting a feature that needs architectural decisions. Also invoked automatically as phase 1 of the codesmith workflow. When triggered standalone with build intent, ask the user if they want the full codesmith workflow instead of proceeding alone."
version: 3.2.0
---

# Brainstorm

Explore the problem space before writing code. This skill ensures you understand what you're building, why, and that the user has approved the approach before a single line is written.

## When to use

- Before any feature or non-trivial change
- When requirements are ambiguous
- When there are multiple valid approaches
- Automatically as the first phase of the codesmith workflow

## Process

### 0. Workflow On-Ramp (standalone only)

**Skip this step if the codesmith orchestrator is already running** (i.e., you were called from within the codesmith workflow — the orchestrator will have already set context).

If brainstorm was triggered directly by the user and the request implies building, adding, or changing something (a feature, fix, refactor, new skill, etc.), ask before proceeding:

> "This looks like a new feature. Want me to start the full **codesmith workflow** (brainstorm → workspace → plan → implement → review → ship), or just brainstorm the approach for now?"

- If they want the **full workflow**: invoke the `codesmith` skill and let it drive from Phase 1.
- If they want to **just brainstorm**: continue with the steps below.
- If the request is clearly exploratory only ("how should we think about X", "what are the options for Y") with no build intent: skip the question and proceed directly.

### 1. Explore Context

Gather everything you need to understand the problem:

- **Read the request carefully** — what did the user actually ask for?
- **Pull ticket details** — if a ticket ID was mentioned and a ticket system is configured (check CLAUDE.md for `ticket-system`), fetch the ticket. If not configured, work with what the user gave you.
- **Explore the codebase** — use subagents to understand existing patterns, architecture, and conventions. Don't guess at the codebase structure.
- **Check recent history** — `git log --oneline -10` for context on what's been happening

### 2. Ask Clarifying Questions

If anything is ambiguous, ask. One question at a time, prefer multiple choice. Stop once you have enough to proceed.

Good questions:
- "Should this handle X or is that out of scope?"
- "I see two patterns in the codebase for this — A and B. Which should I follow?"
- "The ticket says X but the code suggests Y. Which is correct?"

Don't ask questions you can answer by reading the code.

### 3. Propose Approaches

For non-trivial work, present **2-3 concrete approaches**. For each:

```markdown
### Approach {N}: {Name}

**What changes:** {files and components affected}
**How it works:** {brief technical description}
**Gains:** {what you get}
**Costs:** {what you lose or risk}
**Complexity:** {low / medium / high — how many moving parts}
```

Use these design pattern lenses to generate approaches:

- **Extend vs. extract** — add to existing module or create a new one?
- **Inline vs. abstracted** — write it where it's needed or create a reusable piece?
- **Sync vs. async** — can it run synchronously or does it need async?
- **Build vs. library** — write it yourself or use a dependency?
- **Modify in place vs. migrate** — change existing code or add a migration path?
- **Top-down vs. bottom-up** — start from API/UI or from data layer?

Include a recommendation with reasoning. Be opinionated — don't just list options neutrally.

### 4. Spec Review Loop

After the user picks an approach:

1. Write a brief **design spec** summarizing:
   - What we're building (scope)
   - What we're NOT building (explicit exclusions)
   - Acceptance criteria (how we know it's done)
   - Edge cases to handle
   - Edge cases we're explicitly ignoring

2. Present the spec to the user for review.

3. If they have changes, revise and re-present. Loop until approved.

This is a **hard gate**. No planning or implementation until the spec is approved.

### 5. Hand Off

Once the spec is approved, the brainstorm phase is complete. If running as part of the codesmith workflow, the orchestrator advances to the next phase with the approved spec as input.

If running standalone, output the approved spec in a format ready for the `plan` skill.

## Rules

- Never propose code during brainstorming — this is about design, not implementation
- Be ruthless about YAGNI — remove anything not strictly required from the spec
- Follow existing codebase patterns; don't invent new ones unless the existing ones are broken
- Use subagents for codebase exploration to keep context clean
- For trivial changes (typo, config tweak, < 10 lines with obvious intent), skip brainstorming entirely
