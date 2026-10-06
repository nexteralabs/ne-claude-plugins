# Markdown rules (repo docs, README, Git wikis)

Applies on top of the core rules in SKILL.md.

## Structure

- One `#` H1 per file = the title. Sections start at `##`.
- README order: what it is (1–3 sentences) → quick start → usage → configuration → contributing/links. Put install/run commands within the first screen.
- File names: `kebab-case.md`. Link relatively (`[deploy guide](docs/deploy.md)`) so links survive forks and branches.

## Width and layout

- Markdown has no columns. For side-by-side comparison use a table (≤ 5 columns, short cells).
- Keep tables readable in raw form: align pipes when the table is small; don't hand-align large tables.
- Code fences always carry a language (` ```bash `). Lines ≤ 100 chars.
- Wrap prose at sentence boundaries or not at all — never hard-wrap mid-sentence at 80 chars in files others edit through a web UI.

## Callouts

GitHub renders alert blocks; use them under the same limit as core rules (max 2 per page):

```markdown
> [!WARNING]
> Running this against production drops the cache for all tenants.
```

`NOTE` and `WARNING` only. Other renderers show these as plain quotes, which is still readable.

## Diagrams

Prefer Mermaid (renders on GitHub/GitLab) or a committed `.drawio` + exported `.png`/`.svg` next to the doc. Always add alt text: `![Request path from CDN to services](docs/img/request-path.png)`.

## Markdown checklist

- [ ] Single H1, sections from H2
- [ ] Relative links resolve; no bare URLs in prose
- [ ] Every code fence has a language
- [ ] Tables ≤ 5 columns; no HTML tables unless needed for merged cells
- [ ] No emoji headings or badges walls (max one badge row in a README)
