---
name: doc-writer
description: "Write and update professional documentation — overviews, how-to guides, runbooks, references, decision records, onboarding pages. Use whenever the user asks to write, draft, create, restructure, clean up, or update documentation or a wiki page, including Confluence pages ('put this in Confluence', 'update the Confluence page', 'document this service'). Applies a core set of writing and layout rules, plus media-specific rules (Confluence first). Do NOT use for code comments, commit messages, or chat replies."
---

# Doc Writer

Produce documentation that a busy reader can scan in 30 seconds and act on in 5 minutes. Calm, structured, professional: clear sections, tables where comparison helps, nothing decorative.

This file holds the **core rules** that apply to every medium. Before writing, also read the reference for the target medium:

| Medium | Reference | When |
|---|---|---|
| Confluence | [references/confluence.md](references/confluence.md) | Any Confluence page (create or update) — follow its **Workflow** section step by step |
| Markdown (repo docs, README, wiki) | [references/markdown.md](references/markdown.md) | Files in a repo, GitHub/GitLab wikis |

Doc-type skeletons live in [references/doc-types.md](references/doc-types.md).

---

## 1. Before writing

Answer these four questions, from the request and the material at hand. Ask the user only for what you cannot infer.

1. **Reader** — who opens this page, and what do they already know?
2. **Job** — what should they be able to do or decide after reading?
3. **Type** — which doc type fits (see doc-types.md): overview, how-to, runbook, reference, decision record, onboarding. One page = one type. If the material mixes types, split it and link the pages.
4. **Medium** — Confluence, Markdown, other. Load its reference.

Gather facts before prose: read the code, config, tickets or existing pages the doc describes. Never invent values (URLs, ports, owners, limits, dates). When a fact is unknown, write `TBD — <who can answer>` and list it to the user at the end.

---

## 2. Structure

- **Lead with the answer.** The first block under the title is a 2–4 sentence summary: what this is, who it is for, the key takeaway. A reader who stops there should still get value.
- **Headings are a table of contents.** Specific nouns or tasks ("Rotate the API key"), never "Overview", "Misc", "Notes", "Other". Sentence case.
- **Max 3 heading levels** (H2, H3, rarely H4). The page title is the H1; do not repeat it in the body.
- **One idea per section, 3–7 sections per page.** More than ~8 H2s → the page wants splitting.
- **Paragraphs ≤ 4 sentences.** Prefer a list when there are 3+ parallel items; prefer prose when there is reasoning.
- **Numbered lists only for sequences** where order matters. Bullets for everything else.
- **Every procedure step starts with a verb** and contains one action. Put the expected result after the step if the reader needs to verify it.
- **Close with what's next**: related pages, owner/contact, or open questions. No "Conclusion" sections that repeat the page.

---

## 3. Visual rules

The goal is clarity, not decoration. A page should look the same in a year and on any screen.

### Tables and columns — fit the screen

Horizontal space is the scarcest resource. Design for a standard reading width (~760px of content, roughly 100 characters).

| Element | Limit |
|---|---|
| Table columns | 2–4 is the default; **5 max**. More attributes → transpose the table (items as columns, attributes as rows) or split it into two tables |
| Table cell | ≤ ~12 words. Long text in cells means it belongs in prose or a list below the table |
| Side-by-side layout columns | **2**, rarely 3. Never nest layouts |
| Code lines | ≤ 100 characters; wrap long commands with `\` |
| Table rows | No hard limit, but > 15 rows → consider grouping with sub-headings |

**Use a table when** the reader compares 2+ items along the same attributes (options, environments, tiers, before/after), or looks up values (config keys, endpoints, owners).
**Don't use a table** for a sequence (use a numbered list), for a single item (use a definition list or bold labels), or to lay out prose.

The first column is the thing being compared, in bold or plain text; the header row names attributes. Keep units in the header (`Timeout (s)`), not in every cell. Align values consistently; use `—` for "not applicable", never blank cells.

**Side-by-side columns** (layouts) are for genuinely parallel content: before/after, option A vs option B summaries, a short fact box next to the intro. Never use them just to fill width.

### Emphasis and callouts

- **Bold** for UI labels, key terms on first use, and the one phrase per paragraph the reader must not miss. Never bold whole sentences.
- *Italics* sparingly; never for warnings.
- `Code style` for commands, file paths, config keys, values, identifiers.
- **Callouts (info/note/warning panels) are rare.** At most 2 per page, and only for:
  - **Warning** — the action can cause data loss, outage, security exposure or cost. Not for "be careful".
  - **Note/Info** — a prerequisite or a fact the reader will otherwise get wrong.
  If everything is highlighted, nothing is. Never stack two callouts, never put a callout as the first thing on the page.

### Colour, emoji, icons

- **No emoji** in headings, lists or tables. Not as bullets, not as status markers, not "for friendliness". Exception: the user explicitly asks, or the existing page convention uses them and you are updating it.
- **No colour for decoration.** Neutral text. Colour only carries meaning (status), and the medium's built-in status elements are used for it (e.g. Confluence status lozenges) — max one status per table row.
- No ALL CAPS, no exclamation marks, no "!!" or "IMPORTANT:" prefixes.
- Use status words, not symbols: `Supported` / `Not supported`, `Yes` / `No` — not ✅ / ❌.

### Diagrams and images

- Use a diagram when the reader needs to see relationships (architecture, flow, sequence). One diagram per concept, introduced by a sentence saying what it shows.
- Every image gets alt text / a caption that states the takeaway, not "diagram".
- **Diagrams stay editable.** Build them with the **drawio** skill (it lints the layout) and embed the live diagram — on Confluence the draw.io macro, in Markdown the committed `.drawio` + exported SVG. Never paste a static PNG of a diagram: nobody can maintain it.
- Screenshots only for UI; crop them to the relevant region.

---

## 4. Writing style

- **Plain, direct, active voice.** "Run the migration", not "The migration should be run".
- **Second person** for instructions ("you"), present tense.
- **Concrete over abstract.** Real names, numbers, commands, examples. "Requests time out after 30 s", not "there is a timeout".
- **Cut filler.** Delete: "simply", "just", "easily", "basically", "it's worth noting that", "in order to", "please note", "robust", "seamless", "leverage", "comprehensive". Delete sentences that restate the heading.
- **Define acronyms** on first use unless the audience uses them daily.
- **One term per concept.** Pick "service" or "component" and keep it.
- **Dates absolute** (`2026-10-05`), never "last week" or "recently". Versions explicit.
- **Links**: descriptive text ("see the [deployment runbook]"), never "click here" or bare URLs in prose.

---

## 5. Updating an existing doc

Updates are the common case; treat the existing page as the user's work.

1. **Read the full current version first** (for Confluence: fetch the page body and its version number).
2. **Preserve what you were not asked to change**: section order, headings, anchors that other pages link to, macros, attachments, labels, the author's tone and conventions (if the page uses emoji or a template, keep it consistent).
3. **Make the smallest change that fixes the problem.** Rewrite a section only when asked, or when it is wrong.
4. **Fix stale facts you notice** only if you can verify them; otherwise list them to the user as suspected stale.
5. If the page has a change log / "Last reviewed" field, update it with the date and a one-line summary.
6. **Report the diff** to the user: which sections changed and why, in 3–6 bullets.

Restructuring a messy page: propose the new outline (headings only) to the user before moving content, unless they asked for a full rewrite.

---

## 6. Final review (always)

Before delivering, re-read the doc as its reader, top to bottom, and check:

- [ ] The summary alone tells the reader what this is and the key takeaway
- [ ] Headings alone read as a sensible table of contents
- [ ] No table wider than 5 columns; no cell longer than ~12 words; no layout with more than 3 columns
- [ ] At most 2 callouts; every warning describes a real consequence
- [ ] No emoji, no decorative colour, no ALL CAPS, no exclamation marks
- [ ] No filler words from section 4; no sentence that repeats its heading
- [ ] Every command, path, value is in code style and was taken from a real source (or marked TBD)
- [ ] Procedures are numbered, one verb-first action per step
- [ ] Links have descriptive text; images have meaningful alt text
- [ ] Medium-specific checklist from the reference file passes

For Confluence, `scripts/confluence.py lint` checks most of this list automatically — run it, but still read the page as its reader: the linter cannot judge clarity.

Then tell the user: what was created/changed, where it lives (path or URL), and any TBDs or open questions.
