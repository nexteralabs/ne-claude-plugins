# Confluence rules

Applies on top of the core rules in SKILL.md. Confluence pages are read in a browser at a fixed content width, skimmed from search results, and edited by many people. Optimize for scanning and for the next editor.

## Workflow

Follow these steps for every Confluence request. All commands are `python3 <this skill's directory>/scripts/confluence.py …`; run it with `--help` for options.

1. **Locate the target.** Get the page URL (or parent page URL for a new page) from the user. Pass it as `--page-url` — it sets the site and page id. Credentials come from env vars or `--env-file .env` (`CONFLUENCE_*` or `JIRA_URL` / `JIRA_USERNAME` / `JIRA_API_TOKEN`); if the `.env` targets another site, `--page-url` / `--site` wins. Never print credential values.
2. **Read before writing.** `get --page-url URL --out current.xml`. For an update, work from `current.xml` (see section 6).
3. **Plan** the page from SKILL.md sections 1–2: reader, job, doc type, outline (headings only).
4. **Diagrams first.** For each diagram, use the **drawio** skill: build the `.drawio`, run its lint until `RESULT: CLEAN` and width ≤ 1100px. Then publish it with `zenuml` (ZenUML "Graph (DrawIO)", the default) or `drawio` (draw.io app) — section 4, "Diagrams" — and keep the printed macro.
5. **Write the body** in storage format to a local `body.xml`, using only the elements in section 4, with the diagram macros in place.
6. **Lint the body:** `lint --body-file body.xml`. Fix every FAIL and every WARN you can; repeat until `RESULT: CLEAN`.
7. **Publish:** `put --page-url URL --body-file body.xml --message "<what changed>"` (or `create --parent-id ID --title T --body-file body.xml` for a new page). One request handles pages up to at least 10 KB.
8. **Verify:** `get` the page again and confirm the version went up and every diagram macro is present (`detect`).
9. **Report** to the user: page URL, sections created or changed, TBDs, anything that could not be expressed.

Updates through the API do not refresh an editor the user already has open: tell them to reload before editing, or their stale draft can overwrite the new version.

## Contents

1. Choosing the format to send
2. Page skeleton
3. Width budget
4. Allowed elements (storage format snippets)
5. Elements to avoid
6. Creating and updating pages via tools
7. Confluence checklist

---

## 1. Choosing the format to send

Confluence stores pages in **storage format** (XHTML-like XML, Cloud and Data Center). Cloud also uses ADF (JSON) internally. Check the schema of the tool you have before writing:

| Tool accepts | Write in | Notes |
|---|---|---|
| Storage format (`representation: storage`, or XHTML body) | Storage format | Full feature set: layouts, panels, status, expand, TOC |
| ADF JSON | ADF | Same features; panels are `panel` nodes with `panelType` |
| Markdown only | Markdown | No layouts, panels, status or expand. Use tables and plain headings; tell the user which features could not be expressed |
| Wiki markup | Wiki markup | Legacy; prefer storage if offered |

Never paste Markdown into a field that expects storage format — it renders as literal `#` and `**`.

---

## 2. Page skeleton

```
Title            Specific noun phrase: "Payments API — Runbook", not "Runbook" or "Notes"
Summary          2–4 sentences, plain paragraph (no panel)
Fact box         Optional. Owner, status, last reviewed, links — as a 2-column table
                 or a two_right_sidebar layout beside the summary
TOC              Only if the page has 5+ H2 sections
Sections         H2 per section, H3 inside; follow the doc-type skeleton
Related pages    Bulleted links at the end
```

Page properties / fact box example (2-column key/value table, no header row needed). In a `two_right_sidebar` layout the sidebar is ~250px wide: keep every value to 1–2 short words (`Platform team`, not `Commerce platform team`), or place the fact box under the summary instead of beside it. Values that wrap onto 3 lines look broken. Unknown values: write just `TBD` in the fact box and list who can answer under "Open questions".

| Owner | Platform team (@lead) |
|---|---|
| Status | Active (status lozenge) |
| Last reviewed | 2026-10-05 |
| Source | link to repo |

---

## 3. Width budget

Default page width (fixed, ~760px content) is the target. Do not switch a page to full width to make a wide table fit — fix the table.

| Element | Fixed width (default) |
|---|---|
| Table | ≤ 5 columns; ≤ 4 if any column holds sentences |
| Layout section | `single`, `two_equal`, `two_left_sidebar`, `two_right_sidebar`. `three_equal` only for 3 short parallel cards (≤ 40 words each) |
| Code block | ≤ 100 chars per line |
| Image | Width ≤ 760; set `ac:width="760"` on large diagrams so they don't overflow |

Layout rules:
- One layout per page region; don't alternate layouts every section. Most pages are `single` top to bottom, with at most one or two multi-column sections.
- Each column in a section must make sense alone and be roughly equal in length.
- Never put a wide table inside a layout column — tables inside a column get half the width.
- No `three_with_sidebars`; no layouts inside expand macros.

---

## 4. Allowed elements (storage format)

### Headings, text, lists

```xml
<h2>Rotate the API key</h2>
<p>Keys expire every <strong>90 days</strong>. Rotation takes about 5 minutes.</p>
<ol>
  <li><p>Open <strong>Settings &gt; API keys</strong>.</p></li>
  <li><p>Run <code>payments-cli keys rotate --env prod</code>.</p></li>
</ol>
```

Escape `&`, `<`, `>` in text (`&amp;`, `&lt;`, `&gt;`). Use `<p>` inside `<li>` and `<td>` when the content has more than one line.

### Table

```xml
<table data-layout="default">
  <tbody>
    <tr><th><p>Environment</p></th><th><p>URL</p></th><th><p>Deploys</p></th></tr>
    <tr><td><p>Staging</p></td><td><p><code>stg.example.com</code></p></td><td><p>On merge</p></td></tr>
    <tr><td><p>Production</p></td><td><p><code>example.com</code></p></td><td><p>Tuesday, Thursday</p></td></tr>
  </tbody>
</table>
```

`data-layout="default"` keeps the table at page width. Do not set `full-width` or `wide`.

### Layout (side-by-side)

```xml
<ac:layout>
  <ac:layout-section ac:type="two_right_sidebar">
    <ac:layout-cell><p>Summary paragraph…</p></ac:layout-cell>
    <ac:layout-cell><table>…fact box…</table></ac:layout-cell>
  </ac:layout-section>
  <ac:layout-section ac:type="single">
    <ac:layout-cell><h2>…</h2><p>…</p></ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

When a page uses `ac:layout`, **all** body content must be inside layout sections.

### Panels (max 3 per page, one per job)

```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p><strong>Key takeaway:</strong> all order events are replayable for 7 days.</p></ac:rich-text-body>
</ac:structured-macro>
```

| Macro | Colour | Job | Max |
|---|---|---|---|
| `info` | Blue | Key takeaway, context needed first | 1 |
| `tip` | Green | Decision or recommendation | 1 |
| `note` | Yellow | Prerequisite or caveat | 1 |
| `warning` | Red | Data loss, outage, security, cost | 1 |

Never the custom `panel` macro with your own colours; never two panels back to back; never a panel as the first block (the summary paragraph comes first).

### Pros and cons (two-column layout)

```xml
<ac:layout-section ac:type="two_equal">
  <ac:layout-cell><h3>Strengths</h3><ul>
    <li><p>✅&#160; Services deploy independently</p></li>
    <li><p>✅&#160; Events replay after an incident</p></li></ul></ac:layout-cell>
  <ac:layout-cell><h3>Trade-offs</h3><ul>
    <li><p>❌&#160; Order status is eventually consistent</p></li>
    <li><p>⚠️&#160; ERP sync depends on a VPN</p></li></ul></ac:layout-cell>
</ac:layout-section>
```

### Comparison table with signals

```xml
<tr><th><p>Criterion</p></th><th><p>Kafka</p></th><th><p>RabbitMQ</p></th></tr>
<tr><td><p>Replay</p></td><td><p>✅&#160; By offset</p></td><td><p>❌&#160; No</p></td></tr>
<tr><td><p>Ops effort</p></td><td><p>⚠️&#160; Medium</p></td><td><p>✅&#160; Low</p></td></tr>
```

Signal first, then `&#160;` and a space, then words — Confluence drops a plain space after an emoji (verified). Only ✅ ❌ ⚠️.

### Status lozenge (meaning only)

```xml
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="colour">Green</ac:parameter>
  <ac:parameter ac:name="title">Active</ac:parameter>
</ac:structured-macro>
```

Fixed vocabulary, one per row or fact box: `Green` = Active / Done / Supported, `Yellow` = In progress / At risk, `Red` = Blocked / Deprecated, `Grey` = Planned / Not started, `Blue` = In review. Same word always maps to the same colour on the page.

### Code block

```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">bash</ac:parameter>
  <ac:plain-text-body><![CDATA[payments-cli keys rotate --env prod]]></ac:plain-text-body>
</ac:structured-macro>
```

Always set `language`. Code goes in CDATA, unescaped.

### Expand (collapse long, optional detail)

```xml
<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Full error output</ac:parameter>
  <ac:rich-text-body><p>…</p></ac:rich-text-body>
</ac:structured-macro>
```

For logs, long examples, rarely-needed detail. Never hide steps the reader must do.

### Table of contents (5+ H2 sections)

```xml
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="maxLevel">2</ac:parameter>
</ac:structured-macro>
```

### Links

```xml
<ac:link><ri:page ri:content-title="Payments API — Runbook" /><ac:plain-text-link-body><![CDATA[payments runbook]]></ac:plain-text-link-body></ac:link>
<a href="https://github.com/org/repo">payments repository</a>
```

Jira issue: `<ac:structured-macro ac:name="jira"><ac:parameter ac:name="key">PAY-123</ac:parameter></ac:structured-macro>`

### Diagrams: embed the live diagram

Diagrams are embedded as live, editable diagrams — never as a PNG. Pair with the **drawio** skill: it builds the `.drawio` file and lints it (`RESULT: CLEAN`, width ≤ 1100px); this skill publishes it. Put each diagram after the sentence that introduces it and follow it with a caption: `<p><em>Figure N — takeaway.</em></p>`.

**Width:** the page shows diagrams at ~760px whatever the app. Keep the diagram ≤ 1100px wide (top-to-bottom flow when there are more than 5 columns, external systems below or beside the main boundary — never far away). The "Image ≤ 760 / `ac:width`" rule applies to screenshots only.

**Replacing or updating a page that already has diagrams:** run `detect` first. It lists existing diagram macros with their ZenUML `customContentId`. Reuse them with `zenuml --update-id <id>` (same macro, new diagram version) instead of creating new records; for a diagram you remove from the page, tell the user which record is now unused rather than deleting it silently.

#### Which app — pick the publish path

Sites embed draw.io diagrams through different apps, and the editor label varies ("draw.io Diagram", "Graph (DrawIO)", "Graph (DrawIO) Lite"). Ask the user which one their site uses if it is not obvious. Every path below is fully scripted — no manual step in the browser.

**Default: ZenUML "Graph (DrawIO)"** — use `confluence.py zenuml` unless the user says the site uses the draw.io app. It auto-detects the full app or Lite.

| App (editor label) | Diagram stored as | Publish with | Status |
|---|---|---|---|
| ZenUML ("Graph (DrawIO)", "… Lite") — **default** | ZenUML custom content + `zenuml-graph-macro[-lite]` | `confluence.py zenuml` | Verified (Lite; full by the same format) |
| draw.io for Confluence ("draw.io Diagram") | Page attachment + `drawio` macro | `confluence.py drawio` | Verified |
| draw.io Zero Egress, other Forge-only apps | Forge storage, site-specific `ac:adf-extension` | Template from `confluence.py detect` | Not verified |

**ZenUML** stores the `.drawio` XML as `graphXml` in a custom-content record attached to the page; the macro points at it.

```bash
python3 <this skill's directory>/scripts/confluence.py zenuml --page-url URL --file diagram.drawio --name "Payments architecture"
```

It prints the macro to paste where the diagram belongs:

```xml
<ac:structured-macro ac:name="zenuml-graph-macro-lite" ac:schema-version="1">
  <ac:parameter ac:name="uuid">…</ac:parameter>
  <ac:parameter ac:name="customContentId">…</ac:parameter>
  <ac:parameter ac:name="updatedAt">2026-10-06T00:00:00Z</ac:parameter>
</ac:structured-macro>
```

- Edition is auto-detected (full app first, then Lite); force it with `--edition full|lite`.
- **Update in place** with `--update-id <customContentId>` (read it from the macro): the record gets a new version, the page itself needs no edit.
- The diagram stays editable in ZenUML's embedded draw.io editor.

**Forge-only apps (not verified):** run `confluence.py detect --page-id ID` on a page that already has a diagram from that app and reuse the printed `<ac:adf-extension>` markup with a fresh `local-id`; its `extension-key` holds installation-specific IDs and cannot be written from memory. If you cannot tell where that app stores the diagram, attach the `.drawio` file and tell the user rather than publishing a broken macro.

After publishing with any app, re-fetch the page (`confluence.py get`) and confirm the macro is there.

#### draw.io app (when the site uses it instead of ZenUML)

Diagrams are embedded with the **draw.io macro**, never as a PNG. A PNG cannot be edited by the next person and goes stale; the macro renders the real `.drawio` file, which anyone can open and edit in the page.

Pair with the **drawio** skill: it produces the `.drawio` file and lints the layout. This skill publishes it.

1. Build and lint the diagram with the drawio skill until `drawio_lint.py` prints `RESULT: CLEAN`.
2. Upload it and get the macro:
   ```bash
   python3 <this skill's directory>/scripts/confluence.py drawio --page-id ID --file diagram.drawio --name "Payments architecture"
   ```
   This attaches the source (media type `application/vnd.jgraph.mxfile`, attachment named exactly `--name`, no extension) plus `<name>.png` as the preview used by search and export, and prints the macro.
3. Paste the macro into the body where the diagram belongs: after the sentence introducing it, followed by a caption.

```xml
<ac:structured-macro ac:name="drawio" ac:schema-version="1" data-layout="default">
  <ac:parameter ac:name="diagramName">Payments architecture</ac:parameter>
  <ac:parameter ac:name="simpleViewer">false</ac:parameter>
  <ac:parameter ac:name="zoom">1</ac:parameter>
  <ac:parameter ac:name="lbox">true</ac:parameter>
  <ac:parameter ac:name="diagramWidth">1000</ac:parameter>
  <ac:parameter ac:name="revision">1</ac:parameter>
</ac:structured-macro>
<p><em>Figure 1 — Payment request path from the CDN to the services.</em></p>
```

- **Requires the draw.io app** on the site. Without it the macro renders as "unknown macro" — tell the user instead of falling back silently to a PNG.
- **Updating a diagram**: edit the `.drawio`, re-lint, run the same `drawio` command with the same `--name` (a new attachment version is created), and increment `revision` in the macro. The page body otherwise does not change.
- One diagram name per diagram on a page; names are the link between macro and attachment, so never rename one without updating the other.
- **Design the diagram for the page width.** The macro scales the diagram down to the content width (~760px). A diagram wider than ~1100px renders with unreadable labels (verified: a 2000px architecture diagram became illegible). Before publishing, keep the diagram's total width ≤ 1100px: flow top-to-bottom instead of left-to-right when there are more than 5 columns, tighten container padding, put external systems (SaaS, on-premise) below rather than beside. If it cannot fit, split it into an overview diagram plus one diagram per zone.
- `lbox=true` lets readers open the diagram full screen — keep it on, but never rely on it for readability.

### Other images (screenshots)

```xml
<ac:image ac:width="760" ac:alt="Settings page with the API keys tab open">
  <ri:attachment ri:filename="api-keys-settings.png" />
</ac:image>
```

Only for things that are not diagrams (UI screenshots). Upload with `confluence.py attach` first; width ≤ 760; alt text states what to look at.

### Task list (action items, decisions)

```xml
<ac:task-list>
  <ac:task><ac:task-status>incomplete</ac:task-status><ac:task-body>Rotate staging key — @owner, 2026-10-12</ac:task-body></ac:task>
</ac:task-list>
```

---

## 5. Elements to avoid

| Avoid | Why | Use instead |
|---|---|---|
| Emoji outside ✅ ❌ ⚠️, emoji in headings, emoticon markup (`(/)`, `:check:`) | Noise, inconsistent rendering | ✅ ❌ ⚠️ in comparisons, status lozenges |
| Coloured text (`<span style="color…">`), highlighted backgrounds | Decorative, unreadable in dark mode | Bold, or a status lozenge |
| Custom `panel` macro with colours | Rainbow pages | `info` / `tip` / `note` / `warning`, one each, max 3 |
| Full-width page / `data-layout="full-width"` tables | Breaks reading width | Transpose or split the table |
| Nested tables, tables in layout columns | Unreadable on narrow screens | Separate tables, or lists |
| Headings inside table cells | Breaks TOC and anchors | Rows with bold labels |
| Empty paragraphs `<p></p>` / `<br/>` for spacing | Inconsistent gaps | Let the theme space blocks |
| Divider `<hr/>` between every section | Headings already separate | Use at most one, before "Related pages" |
| Excerpt / include macros you did not create | Hidden coupling | Link to the source page |

---

## 6. Creating and updating pages via tools

Use `scripts/confluence.py` (stdlib Python, REST API, storage format) when credentials are available — `get`, `put`, `attach`, `drawio`; run it with `--help` for the credential variables (`CONFLUENCE_*` or `JIRA_*`, `--env-file`, `--site`). An Atlassian MCP server works too. If neither is available, write the storage format to a local `.xhtml` file and tell the user how to paste it (Insert > Markup is not available in Cloud; they can use the REST API or a storage-format editor app).

**Create**
1. Find the parent page and space (search by title / CQL) — ask the user if ambiguous; never create at space root by default.
2. Check a page with the same title doesn't already exist in the space (titles are unique per space).
3. Create the page; add labels the space already uses (search existing labels, don't invent a taxonomy).
4. Return the page URL.

**Update**
1. Fetch the page **with its body in storage format and its current version number**.
2. Edit the storage XML surgically — keep every `ac:structured-macro` you are not changing (including its `ac:macro-id`), every `ri:` reference, anchors and attachments.
3. Send the update with `version = current + 1` and a short version message ("Update deploy steps for v2 pipeline").
4. If the update is rejected for a version conflict, re-fetch and re-apply — never overwrite someone else's newer edit.
5. Report the changed sections and the page URL.

Large pages: if a tool limits body size, update section by section only if the tool supports it; otherwise tell the user rather than truncating content.

---

## 7. Confluence checklist

- [ ] `confluence.py lint` prints `RESULT: CLEAN`
- [ ] Body is in the format the tool expects (storage / ADF / markdown) — no stray Markdown in storage
- [ ] Title is specific and unique in the space
- [ ] Summary is a plain paragraph, not a panel; TOC only if 5+ sections
- [ ] Tables ≤ 5 columns, `data-layout="default"`; no tables inside layout columns
- [ ] Layouts: only single / two-column types, all content inside sections when `ac:layout` is used
- [ ] ≤ 3 panels, one per job; status lozenges use the fixed colour vocabulary
- [ ] Visual minimum met: 2+ of diagram, status lozenges, ✅/❌ comparison, two-column layout, takeaway panel
- [ ] Diagrams are ≤ 1100px wide so labels stay readable at page width
- [ ] Sidebar fact-box values fit on one line
- [ ] Diagrams are draw.io macros backed by a linted `.drawio` attachment, not PNGs; screenshots have `ac:alt` and width ≤ 760
- [ ] Code blocks have `language`
- [ ] On update: version incremented, untouched macros and macro-ids preserved
