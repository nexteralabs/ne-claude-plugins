# Doc types

Pick one type per page (based on the Diátaxis framework, extended with common engineering pages). Headings below are defaults — rename them to specific nouns for the subject.

| Type | Reader's question | Tone |
|---|---|---|
| Overview | "What is this and how does it fit?" | Explanatory |
| How-to | "How do I accomplish X?" | Imperative, minimal theory |
| Runbook | "Something is wrong / scheduled op — what do I do now?" | Imperative, terse, copy-pasteable |
| Reference | "What is the exact value / option / endpoint?" | Neutral, complete, tabular |
| Decision record | "What did we decide, and why?" | Factual, balanced |
| Onboarding | "I'm new — where do I start?" | Welcoming but concise, ordered |

---

## Overview (service, system, project)

1. Summary — what it does, for whom, status
2. Fact box — owner, repo, environments, on-call, last reviewed
3. How it works — one diagram + 1–3 paragraphs
4. Key components — table: component, responsibility, tech (≤ 4 columns)
5. Dependencies and consumers
6. Operations — links to runbooks, dashboards, alerts
7. Related pages

## How-to

1. Summary — the goal and when you'd do it
2. Prerequisites — access, tools, versions (bullets)
3. Steps — numbered, one action each, expected result where useful
4. Verify — how to confirm it worked
5. Troubleshooting — table: symptom, cause, fix (only real, known issues)

## Runbook

1. Summary — what this runbook handles, severity, who can run it
2. Triggers — alert names or symptoms that lead here
3. Diagnose — numbered checks with exact commands and what output means
4. Mitigate / resolve — numbered steps; destructive steps get the page's single `warning`
5. Escalate — who, how, when (table)
6. Afterwards — follow-up actions, where to log the incident

## Reference

1. Summary — what is covered, version it applies to
2. Tables grouped by H2 (e.g. per resource or config section); columns: name, type, default, description
3. Examples — minimal, copy-pasteable
Keep it complete and boring; no narrative.

## Decision record (ADR)

1. Summary — the decision in one sentence, status lozenge, date, deciders
2. Context — the problem and constraints
3. Options considered — comparison table (options as rows, ≤ 4 criteria as columns), then a short paragraph per option only if needed
4. Decision — what and why
5. Consequences — positive, negative, follow-ups (task list)

## Onboarding

1. Summary — who this is for, how long it takes
2. First day — ordered checklist (access, tools, accounts)
3. First week — key pages to read, people to meet (table: who, why)
4. Glossary — terms the team uses (2-column table)
5. Where to ask questions
