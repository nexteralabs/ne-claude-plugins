---
name: drawio
description: "Use this skill whenever the user wants to create or edit a diagram, chart, or visual with drawio. Triggers include: flowcharts, sequence diagrams, architecture diagrams, swimlane diagrams, ER diagrams, network diagrams, mind maps, org charts, process flows, or any request to 'draw', 'diagram', 'visualize', 'map out', or 'create a chart'. Also use when the user mentions draw.io, diagrams.net, .drawio files, or asks to export a diagram to PNG. Use even when the user doesn't name draw.io explicitly — if they want a visual diagram of any kind, this skill applies. Do NOT use for charts that are pure data visualizations (bar charts, line graphs) — those belong in spreadsheet or plotting tools."
---

# Draw.io Diagram Skill

Create and edit draw.io files (`.drawio`) directly in XML. This is the fastest path to a shareable, editable diagram — no GUI needed.

## Layout Method (do this before writing any XML)

Overlaps and tangled lines come from placing shapes first and wiring them afterwards. Plan the graph, then the grid, then the wires.

1. **List nodes and edges.** Pick one main flow direction: left→right for architectures (tiers as columns), top→down for processes.
2. **Assign columns (tiers).** Column = position in the main flow (clients → edge → gateway → services → data). Edges that go *against* the flow (callbacks, push notifications, webhooks) are back-edges: keep them, but plan to route them around the outside.
3. **Order shapes inside each column to minimize crossings.** Place each shape at the average row of the neighbours it connects to in the previous column (barycenter), then do one pass right→left the same way. Shapes that talk to each other must be adjacent. Put hubs (gateway, bus, BFF) in the middle row so their fan-out spreads up and down evenly.
4. **Containers follow the grid**, not the other way round: a container must cover a contiguous block of cells. If the column order forces a container to split, change the order.
5. **Leave routing room.** Gap between columns ≥ 120px (≥ 160px if the edges carry labels); gap between rows ≥ 60px. All shapes in a row share the same center-y; all shapes in a column share the same center-x, so most edges become straight lines.
6. **One port per edge.** When ≥ 2 connectors leave (or enter) the same side of a shape, give each its own `exitX/exitY` (`entryX/entryY`) — e.g. 0.25 / 0.5 / 0.75 — ordered like their targets, so they never merge into a shared trunk or cross at the shape.
7. **Route long edges through gaps.** An edge that skips a column, or a back-edge, gets explicit `<Array as="points">` waypoints that run through an empty gap or around the diagram's outside edge — never through the column in between.
8. **Labels:** ≤ 3 words, only on edges whose meaning is not obvious, `labelBackgroundColor=#ffffff`, and only on segments long enough to hold them (≥ 120px). Never put a label in a gap narrower than the label.
9. **Count before you write.** Walk every edge on your grid and count crossings. With ~15 shapes, 0–2 is achievable; if you count more, reorder (step 3) before writing XML.

---

## Mandatory: Render and Lint Before You Finish

The XML only says where shapes are. draw.io decides at render time where connectors go, so a layout that looks fine on paper can still produce crossings, lines stacked on top of each other, or labels sitting on shapes. Never hand over a diagram you haven't measured.

```bash
python3 <this skill's directory>/scripts/drawio_lint.py diagram.drawio
```

The script renders the file with the draw.io CLI (auto-detected; set `DRAWIO_BIN` if needed) and reports, with the edges named `Source -> Target`:

| Check | Meaning | Target |
|---|---|---|
| `shape_overlaps` | two shapes overlap (proper container nesting is fine) | 0 |
| `edge_crossings` | two connectors cross | ≤ 2, aim for 0 |
| `edge_overlaps` | two connectors run on top of each other (shared trunk) | 0 |
| `edge_through_shape` | a connector passes through an unrelated shape | 0 |
| `label_collisions` | a connector label sits on a shape, header, line or label | 0 |
| `broken_edges` | dangling source/target | 0 |

It also writes `diagram.lint.png` with every problem circled. **Open that PNG (Read it) and look at it** before deciding the fix.

**Loop:** write → lint → fix the reported items → lint again, until it prints `RESULT: CLEAN` (up to ~6 rounds). Fix the cause, not the symptom:

| Problem | Fix |
|---|---|
| crossing | Reorder shapes in the row/column so connected shapes sit next to each other; move a node to the side where most of its neighbours are; route a back-edge around the outside of the diagram with waypoints |
| shared trunk (`edge_overlaps`) | Give each connector leaving the same side of a shape its own port: `exitX/exitY` (and `entryX/entryY` on the target) at 0.25 / 0.5 / 0.75, ordered the same way as the targets so they don't cross each other |
| edge through shape | Move the shape out of the corridor, or add `<Array as="points">` waypoints that run through an empty gap |
| label collision | Make the gap between the two shapes wider (≥ 140px for a labelled edge), shorten the label, or slide it along the edge with `<mxGeometry relative="1" x="-0.4" ...>`; add `labelBackgroundColor=#ffffff` |
| shape overlap | Recompute coordinates; grow the container so it holds its children plus 20px padding |

If the draw.io CLI is not installed, say so to the user and fall back to the Validation Checklist at the end of this skill.

---

## File Structure

Every `.drawio` file is an XML document with this skeleton:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Claude" version="21.0.0">
  <diagram name="Page-1" id="page-1">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1654" pageHeight="1169"
                  math="0" shadow="0" defaultFontFamily="Helvetica">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- shapes and connectors go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Page size tip:** `pageWidth="1654" pageHeight="1169"` is A3 landscape — good for wide diagrams. Use `827` × `1169` for A4 portrait.

---

## XML Element Order = Drawing Order

Elements written first are rendered first (behind). Structure your `<root>` like this to avoid z-order headaches:

```xml
<root>
  <mxCell id="0" />
  <mxCell id="1" parent="0" />

  <!-- 1. Swimlane / container backgrounds (bottommost) -->
  <!-- 2. Connectors / arrows (behind shapes) -->
  <!-- 3. Shapes / vertices -->
  <!-- 4. Floating text labels (topmost) -->
</root>
```

---

## Shape Reference

### Rectangle
```xml
<mxCell id="rect-1" value="Label" vertex="1" parent="1"
  style="rounded=0;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry" />
</mxCell>
```

### Rounded Rectangle
```xml
<mxCell id="rounded-1" value="Label" vertex="1" parent="1"
  style="rounded=1;arcSize=20;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry" />
</mxCell>
```

### Ellipse / Circle
```xml
<mxCell id="ellipse-1" value="Label" vertex="1" parent="1"
  style="ellipse;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry" />
</mxCell>
```

### Diamond (Decision)
```xml
<mxCell id="diamond-1" value="Yes?" vertex="1" parent="1"
  style="rhombus;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="200" y="200" width="120" height="120" as="geometry" />
</mxCell>
```

### Cylinder (Database)
```xml
<mxCell id="db-1" value="PostgreSQL" vertex="1" parent="1"
  style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fontSize=14;fillColor=#dae8fc;strokeColor=#6c8ebf;">
  <mxGeometry x="100" y="100" width="80" height="100" as="geometry" />
</mxCell>
```

### Parallelogram (Input/Output)
```xml
<mxCell id="io-1" value="User Input" vertex="1" parent="1"
  style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry" />
</mxCell>
```

### Text Label (floating)
```xml
<mxCell id="text-1" value="Note" vertex="1" parent="1"
  style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=14;">
  <mxGeometry x="100" y="100" width="120" height="30" as="geometry" />
</mxCell>
```

### Start / End (Rounded Terminal)
```xml
<!-- Start -->
<mxCell id="start-1" value="Start" vertex="1" parent="1"
  style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;">
  <mxGeometry x="100" y="40" width="120" height="40" as="geometry" />
</mxCell>

<!-- End -->
<mxCell id="end-1" value="End" vertex="1" parent="1"
  style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;">
  <mxGeometry x="100" y="600" width="120" height="40" as="geometry" />
</mxCell>
```

---

## Connectors / Arrows

Arrows need a `source` and `target` that match `id` values on shapes. Put them **before** shapes in the XML.

### Basic Arrow
```xml
<mxCell id="arrow-1" edge="1" parent="1" source="rect-1" target="rect-2"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Labeled Arrow
```xml
<mxCell id="arrow-2" value="calls" edge="1" parent="1" source="a" target="b"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontSize=12;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Dashed Arrow (async / optional flow)
```xml
<mxCell id="arrow-3" edge="1" parent="1" source="a" target="b"
  style="edgeStyle=orthogonalEdgeStyle;dashed=1;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Bidirectional Arrow
```xml
<mxCell id="arrow-4" edge="1" parent="1" source="a" target="b"
  style="edgeStyle=orthogonalEdgeStyle;endArrow=block;startArrow=block;startFill=1;endFill=1;rounded=0;html=1;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### No-arrowhead Line (for group boundaries / notes)
```xml
<mxCell id="line-1" edge="1" parent="1" source="a" target="b"
  style="endArrow=none;html=1;dashed=1;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

---

## Swimlanes and Containers

Swimlanes group shapes visually and enforce parent-child layout. The key is `parent="lane-id"` on child shapes, and `<mxGeometry>` on children uses **coordinates relative to the swimlane's top-left corner**.

### Horizontal Swimlane (lanes are rows)
```xml
<!-- Outer container -->
<mxCell id="pool-1" value="Process Name" vertex="1" parent="1"
  style="shape=pool;startSize=30;horizontal=1;childLayout=stackLayout;horizontalStack=0;resizeParent=1;resizeParentMax=0;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;fontSize=14;">
  <mxGeometry x="40" y="80" width="900" height="500" as="geometry" />
</mxCell>

<!-- Lane A -->
<mxCell id="lane-a" value="User" vertex="1" parent="pool-1"
  style="swimlane;startSize=30;horizontal=0;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;">
  <mxGeometry x="0" y="0" width="900" height="160" as="geometry" />
</mxCell>

<!-- Lane B -->
<mxCell id="lane-b" value="System" vertex="1" parent="pool-1"
  style="swimlane;startSize=30;horizontal=0;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;">
  <mxGeometry x="0" y="160" width="900" height="160" as="geometry" />
</mxCell>

<!-- Shape inside Lane A — coordinates relative to lane-a -->
<mxCell id="s1" value="Submit Form" vertex="1" parent="lane-a"
  style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="60" y="50" width="140" height="60" as="geometry" />
</mxCell>
```

### Simple Container / Group Box
Use a swimlane with no child lanes — just a labelled bounding box:
```xml
<mxCell id="box-1" value="Frontend" vertex="1" parent="1"
  style="swimlane;startSize=25;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;">
  <mxGeometry x="40" y="80" width="400" height="300" as="geometry" />
</mxCell>

<!-- Child shapes use parent="box-1" and local coordinates -->
<mxCell id="comp-1" value="React App" vertex="1" parent="box-1"
  style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;">
  <mxGeometry x="40" y="60" width="140" height="60" as="geometry" />
</mxCell>
```

**Important:** Connectors between shapes in different containers must have `parent="1"` (the root), not the container. Use global coordinates for the geometry.

---

## Diagram Patterns

### Flowchart
Standard top-to-bottom flow. Use terminals for start/end, diamonds for decisions, rectangles for steps. Space steps ~100px apart vertically.

```
Start (y=40)
  ↓ arrow
Step 1 (y=120)
  ↓ arrow
Decision (y=220, diamond)
  ↓ Yes          → No → Step 2B (y=280, offset x)
Step 2A (y=360)
  ↓ arrow
End (y=460)
```

### Sequence Diagram

Sequence diagrams need lifelines (vertical dashed lines) and message arrows. Build them manually:

```xml
<!-- Lifeline headers -->
<mxCell id="actor-user" value="User" vertex="1" parent="1"
  style="shape=mxgraph.flowchart.start_2;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;">
  <mxGeometry x="100" y="40" width="80" height="40" as="geometry" />
</mxCell>
<mxCell id="actor-api" value="API" vertex="1" parent="1"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;">
  <mxGeometry x="400" y="40" width="80" height="40" as="geometry" />
</mxCell>

<!-- Lifelines (vertical dashed lines) -->
<mxCell id="life-user" edge="1" parent="1"
  style="endArrow=none;dashed=1;strokeColor=#999999;">
  <mxGeometry relative="1" as="geometry">
    <Array as="points" />
    <mxPoint x="140" y="80" as="sourcePoint" />
    <mxPoint x="140" y="600" as="targetPoint" />
  </mxGeometry>
</mxCell>
<mxCell id="life-api" edge="1" parent="1"
  style="endArrow=none;dashed=1;strokeColor=#999999;">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="440" y="80" as="sourcePoint" />
    <mxPoint x="440" y="600" as="targetPoint" />
  </mxGeometry>
</mxCell>

<!-- Message arrows (horizontal, with labels) -->
<mxCell id="msg-1" value="POST /login" edge="1" parent="1"
  style="edgeStyle=none;html=1;fontSize=12;">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="140" y="150" as="sourcePoint" />
    <mxPoint x="440" y="150" as="targetPoint" />
  </mxGeometry>
</mxCell>
<mxCell id="msg-2" value="200 OK + token" edge="1" parent="1"
  style="edgeStyle=none;dashed=1;html=1;fontSize=12;">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="440" y="200" as="sourcePoint" />
    <mxPoint x="140" y="200" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

**Sequence diagram layout rules:**
- Lifelines are vertical; messages are horizontal
- Requests go left→right; responses go right→left (dashed)
- Space messages 50-60px apart vertically
- Activation boxes (optional) are thin rectangles on the lifeline

### Architecture Diagram

Use containers to represent system boundaries. Mix shape types to convey component roles:

| Component type | Shape style |
|---|---|
| User / Actor | `shape=mxgraph.flowchart.start_2` or ellipse |
| Web server | rounded rectangle, `fillColor=#dae8fc` |
| Database | `shape=cylinder3` |
| Queue / Bus | parallelogram or `shape=mxgraph.flowchart.delay` |
| Cache | rounded rect, `fillColor=#fff2cc` |
| External service | dashed border rect |
| Cloud boundary | swimlane / container |

**Cloud provider shape libraries** (use in `style=`):
- Azure: `shape=mxgraph.azure2.<service>` (e.g. `mxgraph.azure2.app_service`, `mxgraph.azure2.storage`, `mxgraph.azure2.sql_database`)
- AWS: `shape=mxgraph.aws4.<service>` (e.g. `mxgraph.aws4.lambda`, `mxgraph.aws4.s3`)
- GCP: `shape=mxgraph.gcp2.<service>`

Example Azure service shape:
```xml
<mxCell id="azure-fn" value="Function App" vertex="1" parent="1"
  style="shape=mxgraph.azure2.app_service;fillColor=#0078D4;strokeColor=#005A9E;fontColor=#ffffff;fontStyle=1;fontSize=12;labelPosition=center;verticalLabelPosition=bottom;verticalAlign=top;">
  <mxGeometry x="200" y="200" width="65" height="65" as="geometry" />
</mxCell>
```

### System Boundaries

Always wrap components in boundary containers to show scope and ownership. Nest boundaries to reflect real topology.

#### Cloud Provider Boundaries

Use swimlane containers with the provider's brand color and a clear label:

```xml
<!-- AWS boundary -->
<mxCell id="aws-boundary" value="AWS (us-east-1)" vertex="1" parent="1"
  style="swimlane;startSize=30;fillColor=#FF9900;fontColor=#333333;strokeColor=#CC7A00;fontSize=14;fontStyle=1;opacity=15;align=left;spacingLeft=10;">
  <mxGeometry x="40" y="40" width="600" height="400" as="geometry" />
</mxCell>

<!-- Azure boundary -->
<mxCell id="azure-boundary" value="Azure (West Europe)" vertex="1" parent="1"
  style="swimlane;startSize=30;fillColor=#0078D4;fontColor=#333333;strokeColor=#005A9E;fontSize=14;fontStyle=1;opacity=15;align=left;spacingLeft=10;">
  <mxGeometry x="700" y="40" width="600" height="400" as="geometry" />
</mxCell>

<!-- GCP boundary -->
<mxCell id="gcp-boundary" value="GCP (europe-west1)" vertex="1" parent="1"
  style="swimlane;startSize=30;fillColor=#4285F4;fontColor=#333333;strokeColor=#2D5BB9;fontSize=14;fontStyle=1;opacity=15;align=left;spacingLeft=10;">
  <mxGeometry x="40" y="500" width="600" height="400" as="geometry" />
</mxCell>
```

#### Network / Infrastructure Boundaries

Nest these inside cloud boundaries to show network segmentation:

```xml
<!-- VPC / VNet -->
<mxCell id="vpc-1" value="VPC 10.0.0.0/16" vertex="1" parent="aws-boundary"
  style="swimlane;startSize=25;fillColor=#E8F5E9;strokeColor=#66BB6A;dashed=1;fontSize=14;fontStyle=1;">
  <mxGeometry x="20" y="40" width="560" height="340" as="geometry" />
</mxCell>

<!-- Subnet -->
<mxCell id="subnet-pub" value="Public Subnet (10.0.1.0/24)" vertex="1" parent="vpc-1"
  style="swimlane;startSize=25;fillColor=#E3F2FD;strokeColor=#42A5F5;dashed=1;fontSize=14;">
  <mxGeometry x="20" y="35" width="250" height="140" as="geometry" />
</mxCell>

<mxCell id="subnet-priv" value="Private Subnet (10.0.2.0/24)" vertex="1" parent="vpc-1"
  style="swimlane;startSize=25;fillColor=#FFF3E0;strokeColor=#FFA726;dashed=1;fontSize=14;">
  <mxGeometry x="290" y="35" width="250" height="140" as="geometry" />
</mxCell>
```

#### On-Premise Boundary

```xml
<mxCell id="onprem" value="On-Premise (Data Center)" vertex="1" parent="1"
  style="swimlane;startSize=30;fillColor=#F3E5F5;strokeColor=#AB47BC;fontSize=14;fontStyle=1;opacity=15;">
  <mxGeometry x="40" y="40" width="500" height="350" as="geometry" />
</mxCell>
```

#### Component / Application Boundaries

Group microservices, modules, or application layers:

```xml
<!-- Application boundary -->
<mxCell id="app-backend" value="Backend Services" vertex="1" parent="1"
  style="swimlane;startSize=25;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;">
  <mxGeometry x="40" y="80" width="400" height="300" as="geometry" />
</mxCell>

<!-- Trust boundary (security) — dashed red -->
<mxCell id="trust-boundary" value="Trust Boundary" vertex="1" parent="1"
  style="swimlane;startSize=25;fillColor=#f8cecc;strokeColor=#b85450;dashed=1;dashPattern=8 4;fontSize=14;fontStyle=1;opacity=20;">
  <mxGeometry x="40" y="80" width="800" height="500" as="geometry" />
</mxCell>

<!-- DMZ -->
<mxCell id="dmz" value="DMZ" vertex="1" parent="1"
  style="swimlane;startSize=25;fillColor=#FFF9C4;strokeColor=#F9A825;dashed=1;fontSize=14;fontStyle=1;">
  <mxGeometry x="40" y="40" width="300" height="200" as="geometry" />
</mxCell>
```

#### Boundary nesting rules

- **Cloud → Region → VPC/VNet → Subnet → Components** — follow real topology
- Always include region in cloud boundary labels (e.g. "AWS (us-east-1)")
- Include CIDR ranges on VPCs and subnets when known
- Cross-boundary connections (e.g. VPN, peering, ExpressRoute) use `parent="1"` and should be labeled with the connection type
- Use `opacity=15` on outermost boundaries so nested content stays readable — and keep the title `fontColor=#333333`: white text on a 15%-opacity header is unreadable
- Left-align container titles (`align=left;spacingLeft=10;`) so connectors entering from above don't run through the title text
- Never put a connector label where the edge crosses a container border: move it along the edge (`<mxGeometry relative="1" x="-0.5">`) into open space
- Use `dashed=1` for logical/security boundaries; solid for infrastructure boundaries
- Global services (CloudFront, WAF, Route 53, IAM) go inside the cloud boundary but outside any region/VPC box
- Callbacks from external SaaS (webhooks) are drawn to the service that handles them (logical path), not via the gateway they physically pass through — say so in the caption

---

## Color Palette

| Role | Fill | Stroke |
|---|---|---|
| Default / neutral | `#ffffff` | `#000000` |
| Info / input | `#dae8fc` | `#6c8ebf` |
| Success / output | `#d5e8d4` | `#82b366` |
| Warning / queue | `#fff2cc` | `#d6b656` |
| Error / critical | `#f8cecc` | `#b85450` |
| Background / group | `#f5f5f5` | `#666666` |

Text color: `fontColor=#333333` for light fills, `fontColor=#ffffff` for dark fills.

---

## Style Quick Reference

```
# Typography — MINIMUM FONT SIZES (hard rule)
fontSize=14               ALL vertex shapes (boxes, diamonds, swimlane headers, entity fields, labels)
fontSize=16;fontStyle=1   bold section heading
fontSize=12               ONLY for connector/edge labels (the value="" on edge="1" elements)
# fontSize=12 or 13 on a vertex is NEVER acceptable — always use 14+

# Borders
strokeColor=#b85450;strokeWidth=2   emphasized / error
dashed=1                             optional / async

# Alignment (for text-only cells)
align=center;verticalAlign=middle

# Shape sizing guidelines
Standard box:       width=160, height=60
Decision diamond:   width=120, height=120  (equal sides)
Database cylinder:  width=80,  height=100
Icon (cloud lib):   width=65,  height=65
Swimlane header:    startSize=30 (height of the header bar)
```

---

## PNG Export

```bash
drawio -x -f png -s 2 -o output.png input.drawio
# macOS app bundle: /Applications/draw.io.app/Contents/MacOS/draw.io
```

| Option | Effect |
|---|---|
| `-x` | export mode |
| `-f png` | output format |
| `-s 2` | 2× scale (crisp on retina / presentations) |
| `-t` | transparent background (omit for white) |
| `-o output.png` | output path |

For SVG (infinitely scalable): `-f svg`

---

## Publishing to Confluence

When the diagram goes into a Confluence page, embed the live diagram — not a PNG — so readers can open and edit it in place. The **doc-writer** skill publishes it once the lint is clean, with its `scripts/confluence.py`:

- ZenUML "Graph (DrawIO)" (default): `confluence.py zenuml --page-url URL --file diagram.drawio --name "Diagram name"`
- draw.io app ("draw.io Diagram"): `confluence.py drawio --page-url URL --file diagram.drawio --name "Diagram name"`

Paste the printed macro into the page body. Details in doc-writer's `references/confluence.md`, "Diagrams".

**Width budget for pages:** Confluence (and most doc pages) shows the diagram at ~760px. Keep the total diagram width ≤ 1100px so 14px labels stay readable after scaling: prefer top-to-bottom flow when there are more than 5 columns, and put external systems below the main boundary rather than beside it. Check the width in the lint output before publishing.

---

## Layout Planning

Good placement requires explicit arithmetic — draw.io won't auto-arrange shapes when you write XML directly. Think in rows: pick a standard row center-y, then derive all y coordinates from it.

### Center-alignment formula

When mixing rectangular boxes with icon shapes (Azure stencils, SVG images), their **vertical centers must match** or arrows will angle instead of running straight.

```
box: y=80, h=60  →  center_y = 80 + 60/2 = 110
icon (h=65):     →  y = 110 - 65/2 = 77.5
icon (h=80):     →  y = 110 - 80/2 = 70
```

Apply the same math horizontally when stacking shapes in a column.

### Standard spacing rules

| Situation | Rule |
|---|---|
| Horizontal row of boxes | Same `y`, same `h`; space centers ~190px apart |
| Icon + box on same row | Derive icon `y` from `center_y = box_y + box_h/2` |
| Secondary shape below primary | `y = primary_bottom + 15` minimum clearance |
| Return edge waypoint | Route below the lowest shape bottom + 20px |

### Icon shape fillColor

Stencil shapes (Azure, Veeam, etc.) color their own SVG paths using `fillColor`. **Do not omit or override fillColor** — a missing fill renders the shape white/transparent. Use the exact style string from draw.io's Edit Style dialog (right-click → Edit Style) to get the stencil's native fill.

Image shapes (`image;html=1;image=img/lib/...`) are PNG/SVG files bundled with draw.io. The image path must match exactly — get it from Edit Style dialog on a shape placed from the draw.io panel.

### Lane sizing

Size lanes to contain all their content plus margin:

```
lane_height = row_top_y + row_h + secondary_h + clearances + 40px bottom margin
```

Example with two content rows:
- Main row: y=80, h=60 → bottom=140
- Secondary row (e.g. metastore): y=158, h=50 → bottom=208
- Lane height: 208 + 40 = 248 → round up to 260

### Pre-flight layout check

Before writing XML, sketch the grid on paper or in comments:
```
<!-- Ingestion lane: center_y=110
     sp    x=30   y=77.5  w=65  h=65  (icon, center_y=110 ✓)
     conn  x=175  y=80    w=140 h=60  (box,  center_y=110 ✓)
     ext   x=365  y=80    w=140 h=60
     vdb   x=960  y=77.5  w=65  h=65  (icon, center_y=110 ✓)
     meta  x=918  y=158   w=150 h=50  (below vdb, gap=15px ✓)
-->
```

---

## Common Mistakes to Avoid

**Broken connectors** — An arrow with `source="x"` where no shape has `id="x"` will silently float. Always verify IDs match exactly before writing arrows.

**Child shapes in wrong coordinate space** — If a shape's `parent="lane-a"`, its `x` and `y` are relative to the lane's top-left, not the page. Forgetting this causes shapes to appear far off-screen.

**Arrows rendered on top of shapes** — Put `edge="1"` elements before `vertex="1"` elements in the XML.

**Container connectors** — Connectors between shapes in different containers must have `parent="1"`. Giving them a container as parent causes routing errors.

**Missing XML declaration** — Some tools require `<?xml version="1.0" encoding="UTF-8"?>` on line 1. Include it to be safe.

**Overlapping labels on connectors** — Add `exitX/exitY/entryX/entryY` waypoints or use `edgeStyle=elbowEdgeStyle` when orthogonal routing causes crowding.

**Icon not vertically centered with its row** — Calculate `icon_y = row_center_y - icon_h/2`. Eyeballing this produces diagonal arrows.

**Subsidiary shape overlapping its parent** — Place metastore/detail boxes at `y = parent_bottom + 15`, not at the same y as the parent.

**Style string with line breaks** — When writing style attributes in XML, keep the entire style on one line. Newlines inside an attribute value can corrupt draw.io's style parser and render the shape as a blank box.

---

## Validation Checklist

Before saving / exporting, verify:

- [ ] All arrow `source`/`target` IDs exist as `vertex` elements
- [ ] Child shapes inside containers use `parent="container-id"` and local coordinates
- [ ] Connectors crossing container boundaries have `parent="1"`
- [ ] Arrows appear before shapes in XML
- [ ] Font sizes are legible (≥12 for labels, ≥14 for shape text)
- [ ] Color contrast is sufficient (dark text on light fill, or vice versa)
- [ ] Icon shapes center-y matches their row's rectangular boxes
- [ ] No subsidiary shape (metastore, detail box) overlaps its parent shape
- [ ] Style attributes are on a single unbroken line
- [ ] Icon fillColor comes from Edit Style dialog — not guessed
- [ ] `scripts/drawio_lint.py` prints `RESULT: CLEAN` and you have looked at the `.lint.png`

