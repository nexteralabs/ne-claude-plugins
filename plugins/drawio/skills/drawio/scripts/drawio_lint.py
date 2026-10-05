#!/usr/bin/env python3
"""Layout linter for .drawio files.

Renders the diagram with the draw.io CLI (so edge routes are the ones draw.io
actually draws), then measures:

  shape_overlaps      shapes that overlap each other (not parent/child nesting)
  edge_crossings      points where two different connectors cross
  edge_overlaps       connectors running on top of each other (shared segments)
  edge_through_shape  connectors passing through a shape that is not their source/target
  label_collisions    connector labels sitting on a shape or on another label
  broken_edges        connectors whose source/target id does not exist / is missing

Writes <name>.lint.png: the diagram with every problem circled in red, and
prints a summary (or JSON with --json). Exit code 0 = clean, 1 = issues found,
2 = could not render.

Usage: python3 drawio_lint.py diagram.drawio [--json] [--no-png] [--max-crossings N]
Stdlib only. Needs the draw.io desktop app (set DRAWIO_BIN if not auto-found).
"""
import argparse, base64, json, os, re, shutil, subprocess, sys, tempfile, zlib
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from collections import Counter

TOL = 2.0  # px of slack before something counts as touching


# ---------------------------------------------------------------- draw.io CLI
def find_drawio():
    cands = [os.environ.get("DRAWIO_BIN"), shutil.which("drawio"), shutil.which("draw.io"),
             "/Applications/draw.io.app/Contents/MacOS/draw.io",
             os.path.expanduser("~/Applications/draw.io.app/Contents/MacOS/draw.io"),
             "/opt/drawio/drawio", "/usr/bin/drawio", "/snap/bin/drawio",
             r"C:\Program Files\draw.io\draw.io.exe"]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def export(drawio_bin, src, out, fmt, extra=()):
    cmd = [drawio_bin, "-x", "-f", fmt, *extra, "-o", out, src]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a", *cmd, "--no-sandbox"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.isfile(out):
        raise RuntimeError(f"draw.io export failed: {r.stderr.strip() or r.stdout.strip()}")


# ---------------------------------------------------------------- model
def load_model(path):
    tree = ET.parse(path)
    root = tree.getroot()
    diagram = root.find("diagram") if root.tag == "mxfile" else None
    if diagram is not None:
        model = diagram.find("mxGraphModel")
        if model is None:  # compressed page
            raw = zlib.decompress(base64.b64decode(diagram.text.strip()), -15)
            model = ET.fromstring(unquote(raw.decode("utf-8")))
    elif root.tag == "mxGraphModel":
        model = root
    else:
        raise ValueError("not a draw.io file")
    cells = {}
    for c in model.iter("mxCell"):
        cells[c.get("id")] = c
    # UserObject / object wrappers carry the id + label, the mxCell inside carries geometry
    for wrap in list(model.iter("UserObject")) + list(model.iter("object")):
        inner = wrap.find("mxCell")
        if inner is not None:
            inner.set("id", wrap.get("id"))
            inner.set("value", wrap.get("label", ""))
            cells[wrap.get("id")] = inner
    return cells


def style_of(c):
    d = {}
    for part in (c.get("style") or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
        elif part.strip():
            d[part.strip()] = "1"
    return d


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


class Vertex:
    def __init__(self, cid, label, x, y, w, h, parent, container):
        self.id, self.label = cid, label
        self.x, self.y, self.w, self.h = x, y, w, h
        self.parent, self.container = parent, container

    @property
    def box(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


def build_vertices(cells):
    raw = {}
    for cid, c in cells.items():
        if c.get("vertex") != "1":
            continue
        g = c.find("mxGeometry")
        if g is None or g.get("relative") == "1":
            continue  # edge-attached label
        st = style_of(c)
        if "text" in st or st.get("shape") == "text":
            continue  # free text annotations are not obstacles
        raw[cid] = (c, g, st)
    parents_with_children = {c.get("parent") for c, _, _ in raw.values()}
    out = {}

    def absolute(cid, depth=0):
        if cid in out:
            return out[cid]
        c, g, st = raw[cid]
        x, y = float(g.get("x", 0)), float(g.get("y", 0))
        p = c.get("parent")
        if p in raw and depth < 50:
            pv = absolute(p, depth + 1)
            x, y = x + pv.x, y + pv.y
        cont = (cid in parents_with_children or "swimlane" in st or st.get("container") == "1"
                or st.get("shape") in ("pool", "swimlane") or "group" in st)
        v = Vertex(cid, strip_html(c.get("value")), x, y,
                   float(g.get("width", 0)), float(g.get("height", 0)), p, cont)
        out[cid] = v
        return v

    for cid in raw:
        absolute(cid)
    return out


def ancestors(v, verts):
    seen, p = [], v.parent
    while p in verts and p not in seen:
        seen.append(p)
        p = verts[p].parent
    return seen


# ---------------------------------------------------------------- svg geometry
NUM = r"-?\d+(?:\.\d+)?(?:e-?\d+)?"


def parse_path(d):
    """Polyline points of an SVG path (curves collapse to their end point)."""
    toks = re.findall(r"[MLQCZHVmlqczhv]|" + NUM, d)
    pts, i, cmd, cur = [], 0, None, (0.0, 0.0)
    need = {"M": 2, "L": 2, "Q": 4, "C": 6, "H": 1, "V": 1}
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t.upper()
            i += 1
            if cmd == "Z":
                continue
        n = need.get(cmd)
        if n is None or i + n > len(toks):
            break
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        if cmd in "MLQC":
            cur = (vals[-2], vals[-1])
        elif cmd == "H":
            cur = (vals[0], cur[1])
        elif cmd == "V":
            cur = (cur[0], vals[0])
        pts.append(cur)
    return pts


def parse_svg(svg_path):
    tree = ET.parse(svg_path)
    ns = "{http://www.w3.org/2000/svg}"
    groups = {}
    for g in tree.iter(ns + "g"):
        cid = g.get("data-cell-id")
        if cid:
            groups[cid] = g
    return groups, ns


def own_children(g, ns):
    """Descendants of a cell group that do not belong to a nested cell group."""
    stack = list(g)
    while stack:
        e = stack.pop(0)
        if e.get("data-cell-id"):
            continue
        yield e
        stack[0:0] = list(e)


def edge_polyline(g, ns):
    for e in own_children(g, ns):
        if e.tag == ns + "path" and e.get("fill") == "none":
            pts = parse_path(e.get("d", ""))
            if len(pts) >= 2:
                return pts
    return None


def label_box(g, ns):
    for e in own_children(g, ns):
        if e.tag == ns + "image" and e.get("width"):
            x, y = float(e.get("x")), float(e.get("y"))
            return (x, y, x + float(e.get("width")), y + float(e.get("height")))
    for e in own_children(g, ns):
        if e.tag == ns + "text" and (e.text or "").strip():
            fs = 11.0
            x, y = float(e.get("x", 0)), float(e.get("y", 0))
            w = len(e.text.strip()) * fs * 0.6
            return (x - w / 2, y - fs, x + w / 2, y + fs * 0.3)
    return None


def svg_offset(groups, ns, verts):
    """SVG coords = diagram coords + offset. Recover it from rectangle shapes."""
    votes = Counter()
    for cid, v in verts.items():
        g = groups.get(cid)
        if g is None:
            continue
        for e in own_children(g, ns):
            if e.tag == ns + "rect" and abs(float(e.get("width", -1)) - v.w) < 0.6:
                votes[(round(float(e.get("x")) - v.x), round(float(e.get("y")) - v.y))] += 1
                break
            if e.tag == ns + "path" and "pointer-events" in e.attrib:
                pts = parse_path(e.get("d", ""))
                if pts:
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    if abs((max(xs) - min(xs)) - v.w) < 1 and abs((max(ys) - min(ys)) - v.h) < 1:
                        votes[(round(min(xs) - v.x), round(min(ys) - v.y))] += 1
                        break
    return votes.most_common(1)[0][0] if votes else (0, 0)


# ---------------------------------------------------------------- geometry
def seg_intersection(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    return None


def collinear_overlap(a1, a2, b1, b2, tol=3.0):
    """Length two segments share when they run along the same line (axis-aligned)."""
    if abs(a1[1] - a2[1]) < 0.5 and abs(b1[1] - b2[1]) < 0.5 and abs(a1[1] - b1[1]) < tol:
        lo = max(min(a1[0], a2[0]), min(b1[0], b2[0]))
        hi = min(max(a1[0], a2[0]), max(b1[0], b2[0]))
        return max(0.0, hi - lo), ((lo + hi) / 2, a1[1])
    if abs(a1[0] - a2[0]) < 0.5 and abs(b1[0] - b2[0]) < 0.5 and abs(a1[0] - b1[0]) < tol:
        lo = max(min(a1[1], a2[1]), min(b1[1], b2[1]))
        hi = min(max(a1[1], a2[1]), max(b1[1], b2[1]))
        return max(0.0, hi - lo), (a1[0], (lo + hi) / 2)
    return 0.0, None


def seg_hits_box(p1, p2, box, shrink=TOL):
    x1, y1, x2, y2 = box[0] + shrink, box[1] + shrink, box[2] - shrink, box[3] - shrink
    if x2 <= x1 or y2 <= y1:
        return False
    # Liang-Barsky clip
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p1[0] - x1), (dx, x2 - p1[0]), (-dy, p1[1] - y1), (dy, y2 - p1[1])):
        if abs(p) < 1e-9:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return (t1 - t0) * (dx * dx + dy * dy) ** 0.5 > 1.0


def boxes_overlap(a, b, tol=TOL):
    return a[0] < b[2] - tol and b[0] < a[2] - tol and a[1] < b[3] - tol and b[1] < a[3] - tol


def contains(outer, inner):
    return outer[0] <= inner[0] + TOL and outer[1] <= inner[1] + TOL and \
        outer[2] >= inner[2] - TOL and outer[3] >= inner[3] - TOL


def near(p, q, r):
    return abs(p[0] - q[0]) <= r and abs(p[1] - q[1]) <= r


# ---------------------------------------------------------------- lint
def lint(path, want_png=True, keep_dir=None):
    drawio = find_drawio()
    if not drawio:
        raise RuntimeError("draw.io CLI not found. Install the draw.io desktop app or set DRAWIO_BIN.")
    cells = load_model(path)
    verts = build_vertices(cells)
    edges = {cid: c for cid, c in cells.items() if c.get("edge") == "1"}
    edge_labels = {}  # edge id -> [child label cell ids]
    for cid, c in cells.items():
        if c.get("vertex") == "1" and c.get("parent") in edges and strip_html(c.get("value")):
            edge_labels.setdefault(c.get("parent"), []).append(cid)

    tmp = keep_dir or tempfile.mkdtemp(prefix="drawio-lint-")
    svg = os.path.join(tmp, "render.svg")
    export(drawio, path, svg, "svg")
    groups, ns = parse_svg(svg)
    ox, oy = svg_offset(groups, ns, verts)

    def to_diag(p):
        return (p[0] - ox, p[1] - oy)

    issues = {k: [] for k in ("broken_edges", "shape_overlaps", "edge_crossings", "edge_overlaps",
                              "edge_through_shape", "label_collisions")}

    # --- broken edges
    for eid, c in edges.items():
        for end in ("source", "target"):
            ref = c.get(end)
            if ref is None:
                g = c.find("mxGeometry")
                if g is None or g.find(f"mxPoint[@as='{end}Point']") is None:
                    issues["broken_edges"].append({"edge": eid, "problem": f"no {end}"})
            elif ref not in cells:
                issues["broken_edges"].append({"edge": eid, "problem": f"{end} '{ref}' does not exist"})

    # --- shape overlaps
    vl = list(verts.values())
    for i, a in enumerate(vl):
        for b in vl[i + 1:]:
            if a.id in ancestors(b, verts) or b.id in ancestors(a, verts):
                continue
            if not boxes_overlap(a.box, b.box):
                continue
            if a.container and contains(a.box, b.box) or b.container and contains(b.box, a.box):
                continue  # visually nested even if not structurally
            ix = (max(a.x, b.x) + min(a.box[2], b.box[2])) / 2
            iy = (max(a.y, b.y) + min(a.box[3], b.box[3])) / 2
            issues["shape_overlaps"].append({"a": a.id, "b": b.id, "a_label": a.label,
                                             "b_label": b.label, "at": [round(ix), round(iy)]})

    # --- edge geometry
    polys, ends = {}, {}
    for eid in edges:
        g = groups.get(eid)
        pts = edge_polyline(g, ns) if g is not None else None
        if pts:
            pts = [to_diag(p) for p in pts]
            polys[eid] = pts
            ends[eid] = (pts[0], pts[-1])

    def is_endpoint(eid, p, r=6):
        return any(near(p, q, r) for q in ends[eid])

    eids = sorted(polys)
    found = []
    for i, e1 in enumerate(eids):
        s1 = list(zip(polys[e1], polys[e1][1:]))
        c1 = edges[e1]
        for e2 in eids[i + 1:]:
            c2 = edges[e2]
            shared = {c1.get("source"), c1.get("target")} & {c2.get("source"), c2.get("target")} - {None}
            s2 = list(zip(polys[e2], polys[e2][1:]))
            overlap_len, overlap_at = 0.0, None
            for a1, a2 in s1:
                for b1, b2 in s2:
                    p = seg_intersection(a1, a2, b1, b2)
                    if p and not is_endpoint(e1, p) and not is_endpoint(e2, p):
                        if not any(near(p, q["at"], 4) and {q["a"], q["b"]} == {e1, e2} for q in found):
                            found.append({"a": e1, "b": e2, "at": [round(p[0]), round(p[1])]})
                    ln, at = collinear_overlap(a1, a2, b1, b2)
                    if ln > overlap_len:
                        overlap_len, overlap_at = ln, at
            if overlap_len > 12:
                issues["edge_overlaps"].append({"a": e1, "b": e2, "length": round(overlap_len),
                                                "shared_endpoint": bool(shared),
                                                "at": [round(overlap_at[0]), round(overlap_at[1])]})
    # crossings exactly on a shared collinear run are overlaps, not crossings
    issues["edge_crossings"] = [f for f in found
                                if not any({o["a"], o["b"]} == {f["a"], f["b"]} for o in issues["edge_overlaps"])]

    # --- edges through shapes
    for eid, pts in polys.items():
        c = edges[eid]
        mine = {c.get("source"), c.get("target")}
        for v in verts.values():
            if v.container or v.id in mine:
                continue
            # an edge leaving a shape nested inside its source/target is fine
            if mine & set(ancestors(v, verts)):
                continue
            for a, b in zip(pts, pts[1:]):
                if seg_hits_box(a, b, v.box):
                    cx, cy = (v.x + v.w / 2, v.y + v.h / 2)
                    issues["edge_through_shape"].append({"edge": eid, "shape": v.id, "shape_label": v.label,
                                                         "at": [round(cx), round(cy)]})
                    break

    # --- edge labels
    labels = []
    for eid in edges:
        for lid in [eid] + edge_labels.get(eid, []):
            g = groups.get(lid)
            if g is None:
                continue
            bx = label_box(g, ns)
            if bx:
                a, b = to_diag(bx[:2]), to_diag(bx[2:])
                labels.append((eid, (a[0], a[1], b[0], b[1])))
    for i, (eid, lb) in enumerate(labels):
        for v in verts.values():
            if not v.container and boxes_overlap(lb, v.box):
                issues["label_collisions"].append({"edge": eid, "with": v.id, "with_label": v.label,
                                                   "at": [round((lb[0] + lb[2]) / 2), round((lb[1] + lb[3]) / 2)]})
            elif v.container and boxes_overlap(lb, (v.x, v.y, v.box[2], v.y + header_h(cells[v.id]))):
                issues["label_collisions"].append({"edge": eid, "with": v.id, "with_label": v.label + " (header)",
                                                   "at": [round((lb[0] + lb[2]) / 2), round((lb[1] + lb[3]) / 2)]})
        for eid2, pts2 in polys.items():
            if eid2 != eid and any(seg_hits_box(a, b, lb, shrink=1) for a, b in zip(pts2, pts2[1:])):
                issues["label_collisions"].append({"edge": eid, "with": eid2, "with_label": "line",
                                                   "at": [round((lb[0] + lb[2]) / 2), round((lb[1] + lb[3]) / 2)]})
        for eid2, lb2 in labels[i + 1:]:
            if boxes_overlap(lb, lb2, tol=0):
                issues["label_collisions"].append({"edge": eid, "with": eid2, "with_label": "label",
                                                   "at": [round((lb[0] + lb[2]) / 2), round((lb[1] + lb[3]) / 2)]})

    # human-readable names so a reader can act on the report without decoding ids
    def name(cid):
        if cid in edges:
            c = edges[cid]
            src = verts.get(c.get("source")); tgt = verts.get(c.get("target"))
            return f"{cid} ({src.label if src else '?'} -> {tgt.label if tgt else '?'})"
        return f"{cid} ({verts[cid].label})" if cid in verts else str(cid)
    for items in issues.values():
        for it in items:
            for k in ("a", "b", "edge", "with", "shape"):
                if k in it:
                    it[k] = name(it[k])
            for k in ("a_label", "b_label", "shape_label", "with_label"):
                it.pop(k, None)

    leaf = [v for v in verts.values() if not v.container]
    summary = {
        "file": path,
        "shapes": len(leaf), "containers": len(verts) - len(leaf), "edges": len(edges),
        "counts": {k: len(v) for k, v in issues.items()},
        "issues": issues,
    }
    if want_png:
        png = os.path.splitext(path)[0] + ".lint.png"
        annotate_png(drawio, path, issues, png, tmp)
        summary["png"] = png
    return summary


def header_h(cell):
    st = style_of(cell)
    if "swimlane" in st or st.get("shape") in ("swimlane", "pool"):
        return float(st.get("startSize", 23))
    return 0.0


# ---------------------------------------------------------------- annotated png
MARK = {"shape_overlaps": ("#ff0000", "OVERLAP"), "edge_crossings": ("#ff0000", "X"),
        "edge_overlaps": ("#ff00ff", "SHARED"), "edge_through_shape": ("#ff6600", "THROUGH"),
        "label_collisions": ("#0066ff", "LABEL")}


def annotate_png(drawio, path, issues, png, tmp):
    text = open(path, encoding="utf-8").read()
    if "<mxGraphModel" not in text:  # compressed: rewrite uncompressed first
        un = os.path.join(tmp, "uncompressed.drawio")
        export(drawio, path, un, "xml", ["-u"])
        text = open(un, encoding="utf-8").read()
    marks, n = [], 0
    for kind, (color, tag) in MARK.items():
        for it in issues[kind]:
            n += 1
            x, y = it["at"]
            marks.append(
                f'<mxCell id="lint-{n}" value="{tag}" vertex="1" parent="1" '
                f'style="ellipse;fillColor=none;strokeColor={color};strokeWidth=3;fontColor={color};'
                f'fontStyle=1;fontSize=11;labelPosition=right;verticalLabelPosition=top;align=left;verticalAlign=bottom;">'
                f'<mxGeometry x="{x - 14}" y="{y - 14}" width="28" height="28" as="geometry"/></mxCell>')
    i = text.rfind("</root>")
    if i < 0:
        raise RuntimeError("cannot annotate: no <root> element")
    out = os.path.join(tmp, "annotated.drawio")
    open(out, "w", encoding="utf-8").write(text[:i] + "\n".join(marks) + text[i:])
    export(drawio, out, png, "png", ["-s", "1.5", "-b", "20"])


# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", help="print full JSON report")
    ap.add_argument("--no-png", action="store_true", help="skip the annotated PNG")
    ap.add_argument("--max-crossings", type=int, default=2, help="crossings tolerated before failing (default 2)")
    a = ap.parse_args()
    try:
        r = lint(a.file, want_png=not a.no_png)
    except Exception as e:  # noqa: BLE001
        print(f"LINT ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    c = r["counts"]
    ok = (c["edge_crossings"] <= a.max_crossings and
          all(v == 0 for k, v in c.items() if k != "edge_crossings"))
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['file']}: {r['shapes']} shapes, {r['containers']} containers, {r['edges']} edges")
        for k, v in c.items():
            limit = a.max_crossings if k == "edge_crossings" else 0
            print(f"  {'OK  ' if v <= limit else 'FAIL'} {k:<20} {v}")
        for k, items in r["issues"].items():
            for it in items:
                print(f"    - {k}: " + ", ".join(f"{kk}={vv}" for kk, vv in it.items()))
        if "png" in r:
            print(f"  annotated render: {r['png']}")
        print("RESULT:", "CLEAN" if ok else "ISSUES FOUND")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
