#!/usr/bin/env python3
"""Minimal Confluence Cloud client for the doc-writer skill (stdlib only).

Commands:
  lint    --body-file body.xml                   check a storage-format body against the doc-writer
                                                 rules (no credentials needed); exit 1 if it fails
  create  --parent-id ID --title T --body-file body.xml
                                                 create a child page, print its id and URL
  get     --page-id ID [--out body.xml]          print title/version/url, save storage body
  put     --page-id ID --body-file body.xml [--message "..."]
                                                 replace body, version = current + 1
  attach  --page-id ID --file path [--name N] [--type MIME]
                                                 create or update an attachment
  detect  --page-id ID                            report which draw.io macro variant the page uses
                                                 (classic "drawio" macro, or a Forge app such as
                                                 draw.io Zero Egress / a renamed "Graph" macro) and
                                                 print its raw markup to use as a template
  drawio  --page-id ID --file diagram.drawio [--name N]
                                                 upload a draw.io diagram (source + PNG preview)
                                                 and print the macro XML to paste in the body
  zenuml  --page-id ID --file diagram.drawio [--name N] [--edition lite|full] [--update-id CC_ID]
                                                 publish through the ZenUML app's "Graph (DrawIO)"
                                                 macro (diagram stored as ZenUML custom content);
                                                 --update-id updates an existing diagram in place

Credentials (env vars, or --env-file; first match wins):
  URL    CONFLUENCE_URL   | JIRA_URL       (site root or .../wiki)
  USER   CONFLUENCE_USER  | JIRA_USERNAME  | JIRA_EMAIL
  TOKEN  CONFLUENCE_TOKEN | JIRA_API_TOKEN
  --site overrides the URL (e.g. when the token's .env targets another site).
  --page-url https://acme.atlassian.net/wiki/spaces/X/pages/123/Title sets both --site and --page-id.
"""
import argparse, base64, json, mimetypes, os, shutil, subprocess, sys, tempfile, uuid
import urllib.error, urllib.parse, urllib.request
from pathlib import Path


def load_env(path):
    if not path:
        return
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def first(*names):
    return next((os.environ[n] for n in names if os.environ.get(n)), "")


class Client:
    def __init__(self, site=None):
        url = (site or first("CONFLUENCE_URL", "JIRA_URL")).rstrip("/")
        user, token = first("CONFLUENCE_USER", "JIRA_USERNAME", "JIRA_EMAIL"), first("CONFLUENCE_TOKEN", "JIRA_API_TOKEN")
        if not (url and user and token):
            sys.exit("ERROR: missing credentials (see --help for variable names)")
        self.base = url if url.endswith("/wiki") else url + "/wiki"
        self.auth = "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()

    def call(self, method, path, body=None, headers=None, fatal=True):
        h = {"Authorization": self.auth, "Accept": "application/json", **(headers or {})}
        if isinstance(body, (dict, list)):
            body, h["Content-Type"] = json.dumps(body).encode(), "application/json"
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = f"ERROR {e.code} {method} {path}: {e.read()[:500].decode(errors='replace')}"
            if fatal:
                sys.exit(msg)
            raise RuntimeError(msg)

    def page(self, pid):
        return self.call("GET", f"/rest/api/content/{pid}?expand=body.storage,version,space")

    def put(self, pid, body_xml, message=""):
        p = self.page(pid)
        ver = p["version"]["number"] + 1
        return self.call("PUT", f"/rest/api/content/{pid}", {
            "id": pid, "type": "page", "title": p["title"],
            "version": {"number": ver, "message": message},
            "body": {"storage": {"value": body_xml, "representation": "storage"}},
        })

    def attach(self, pid, data, name, mime):
        """Create the attachment, or upload a new version if one with this name exists."""
        q = urllib.parse.urlencode({"filename": name})
        found = self.call("GET", f"/rest/api/content/{pid}/child/attachment?{q}")["results"]
        path = f"/rest/api/content/{pid}/child/attachment"
        if found:
            path += f"/{found[0]['id']}/data"
        boundary = uuid.uuid4().hex
        parts = [f"--{boundary}\r\nContent-Disposition: form-data; name=\"minorEdit\"\r\n\r\ntrue\r\n".encode(),
                 (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
                  f"Content-Type: {mime}\r\n\r\n").encode() + data + b"\r\n",
                 f"--{boundary}--\r\n".encode()]
        r = self.call("POST", path, b"".join(parts), {
            "Content-Type": f"multipart/form-data; boundary={boundary}", "X-Atlassian-Token": "no-check"})
        return r["results"][0] if "results" in r else r


def find_drawio():
    for c in [os.environ.get("DRAWIO_BIN"), shutil.which("drawio"), shutil.which("draw.io"),
              "/Applications/draw.io.app/Contents/MacOS/draw.io", "/opt/drawio/drawio", "/usr/bin/drawio"]:
        if c and os.path.isfile(c):
            return c
    return None


def detect_diagrams(body):
    """Find draw.io macros in a storage body. Returns [(variant, title, markup)]."""
    import re
    found = []
    for m in re.finditer(r'<ac:structured-macro\b[^>]*ac:name="(drawio|drawio-sketch|inc-drawio)".*?</ac:structured-macro>', body, re.S):
        found.append(("classic", m.group(1), m.group(0)))
    for m in re.finditer(r'<ac:adf-extension>.*?</ac:adf-extension>', body, re.S):
        x = m.group(0)
        key = re.search(r'key="extension-key">([^<]+)<', x)
        title = re.search(r'key="extension-title">([^<]+)<', x)
        text = (key.group(1) if key else "") + " " + (title.group(1) if title else "")
        if re.search(r"draw|graph|diagram|mxgraph", text, re.I):
            found.append(("forge", title.group(1) if title else "?", x))
    return found


def drawio_macro(name, width):
    return (f'<ac:structured-macro ac:name="drawio" ac:schema-version="1" data-layout="default">'
            f'<ac:parameter ac:name="diagramName">{name}</ac:parameter>'
            f'<ac:parameter ac:name="simpleViewer">false</ac:parameter>'
            f'<ac:parameter ac:name="zoom">1</ac:parameter>'
            f'<ac:parameter ac:name="lbox">true</ac:parameter>'
            f'<ac:parameter ac:name="diagramWidth">{width}</ac:parameter>'
            f'<ac:parameter ac:name="revision">1</ac:parameter>'
            f'</ac:structured-macro>')


def zenuml_publish(c, pid, xml, title, edition, update_id=None):
    """Store a draw.io diagram as ZenUML custom content; return (custom content id, uuid, macro XML)."""
    if edition == "auto":
        errors = []
        for ed in ("full", "lite"):
            try:
                return zenuml_publish(c, pid, xml, title, ed, update_id)
            except RuntimeError as e:
                errors.append(f"{ed}: {e}")
        sys.exit("ERROR: no ZenUML app accepted the diagram. Is ZenUML installed on this site?\n" + "\n".join(errors))
    import datetime, json as _json
    suffix = "-lite" if edition == "lite" else ""
    ctype = f"ac:com.zenuml.confluence-addon{suffix}:zenuml-content-graph"
    if update_id:
        cur = c.call("GET", f"/api/v2/custom-content/{update_id}?body-format=raw", fatal=False)
        if cur.get("type") != ctype:
            raise RuntimeError(f"custom content {update_id} is {cur.get('type')}, not {ctype}")
        uid = _json.loads(cur["body"]["raw"]["value"]).get("id") or str(uuid.uuid4())
        body = {"diagramType": "graph", "graphXml": xml, "title": title, "id": uid}
        cc = c.call("PUT", f"/api/v2/custom-content/{update_id}", fatal=False, body={
            "id": update_id, "type": ctype, "status": "current", "pageId": pid, "title": title,
            "body": {"value": _json.dumps(body), "representation": "raw"},
            "version": {"number": cur["version"]["number"] + 1, "message": "Update diagram"}})
    else:
        uid = str(uuid.uuid4())
        body = {"diagramType": "graph", "graphXml": xml, "title": title, "id": uid}
        cc = c.call("POST", "/api/v2/custom-content", fatal=False, body={
            "type": ctype, "pageId": pid, "title": title,
            "body": {"value": _json.dumps(body), "representation": "raw"}})
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    macro = (f'<ac:structured-macro ac:name="zenuml-graph-macro{suffix}" ac:schema-version="1">'
             f'<ac:parameter ac:name="uuid">{uid}</ac:parameter>'
             f'<ac:parameter ac:name="customContentId">{cc["id"]}</ac:parameter>'
             f'<ac:parameter ac:name="updatedAt">{now}</ac:parameter>'
             f'</ac:structured-macro>')
    return cc["id"], uid, macro


EMOJI = "[\U0001F300-\U0001FAFF☀-➿⭐✅❌✔✖]"
CALLOUTS = ("info", "note", "warning", "tip", "panel")
ALLOWED_LAYOUTS = ("single", "two_equal", "two_left_sidebar", "two_right_sidebar", "three_equal")


def lint_body(body):
    """Check a storage-format body against the doc-writer rules. Returns (fails, warns)."""
    import re
    import xml.etree.ElementTree as ET
    fails, warns = [], []
    text = lambda x: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()
    try:
        ET.fromstring('<r xmlns:ac="ac" xmlns:ri="ri">' + re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", body) + "</r>")
    except ET.ParseError as e:
        return [f"not well-formed XML: {e}"], []
    prose = re.sub(r"<ac:plain-text-body>.*?</ac:plain-text-body>|<code>.*?</code>", " ", body, flags=re.S)

    first = re.sub(r"^(<ac:layout>|<ac:layout-section[^>]*>|<ac:layout-cell>|\s)+", "", body)
    if not first.startswith("<p"):
        fails.append("the page must open with a plain summary paragraph (not a heading, panel or macro)")
    if "<h1" in body:
        fails.append("<h1> in the body: the page title is the H1, start sections at <h2>")
    for t in re.findall(r"<table.*?</table>", body, re.S):
        rows = re.findall(r"<tr.*?</tr>", t, re.S)
        cols = max((len(re.findall(r"<t[hd][ >]", r)) for r in rows), default=0)
        if cols > 5:
            fails.append(f"table with {cols} columns (max 5): transpose or split it")
        for cell in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S):
            n = len(text(cell).split())
            if n > 25:
                warns.append(f"table cell with {n} words: move long text out of the table ({text(cell)[:40]}...)")
        if re.search(r'data-layout="(full-width|wide)"', t):
            fails.append("full-width/wide table: keep data-layout=\"default\" and fix the table instead")
    n_callouts = sum(len(re.findall(rf'ac:name="{c}"', body)) for c in CALLOUTS)
    if n_callouts > 2:
        fails.append(f"{n_callouts} callout panels (max 2)")
    for c in ("tip", "panel"):
        if f'ac:name="{c}"' in body:
            fails.append(f'"{c}" macro: use info/note/warning (or plain text)')
    if re.search(r"<ac:layout-section[^>]*>", body):
        for t in re.findall(r'ac:type="([a-z_]+)"', body):
            if t not in ALLOWED_LAYOUTS:
                fails.append(f"layout type {t} not allowed")
        outside = re.sub(r"<ac:layout>.*?</ac:layout>", "", body, flags=re.S).strip()
        if outside:
            fails.append("content outside <ac:layout>: when a page uses layouts, all content goes in layout sections")
        for cell in re.findall(r'two_right_sidebar">.*?<ac:layout-cell>.*?</ac:layout-cell>\s*<ac:layout-cell>(.*?)</ac:layout-cell>', body, re.S):
            for v in re.findall(r"<td[^>]*>(.*?)</td>", cell, re.S):
                if len(text(v).split()) > 2:
                    warns.append(f"sidebar value '{text(v)}' will wrap: keep sidebar values to 1-2 words")
    if re.search(EMOJI, prose) or re.search(r"\((/|x|!|\?|on|off|\*)\)|:[a-z_]+:", prose):
        fails.append("emoji / emoticons in the text: use words or a status lozenge")
    if re.search(r'style="[^"]*(color|background)', body):
        fails.append("coloured text or background: neutral text only")
    for m in re.finditer(r'<ac:structured-macro[^>]*ac:name="code"[^>]*>(.*?)</ac:structured-macro>', body, re.S):
        if 'ac:name="language"' not in m.group(1):
            fails.append("code block without a language parameter")
    for m in re.finditer(r"<ac:image([^>]*)>(.*?)</ac:image>", body, re.S):
        if "ac:alt" not in m.group(1):
            fails.append("image without ac:alt")
        if re.search(r"(diagram|architecture|flow|drawio)[^\"]*\.png", m.group(2), re.I):
            fails.append("diagram embedded as PNG: embed the live diagram (drawio / zenuml command)")
    for m in re.finditer(r'ac:name="diagramWidth">(\d+)<', body):
        if int(m.group(1)) > 1100:
            warns.append(f"diagram {m.group(1)}px wide: labels unreadable at page width (max 1100)")
    if re.search(r"(^|>)\s*(#{1,6} |\*\*\w|```)", prose, re.M):
        fails.append("Markdown syntax in a storage body (#, **, ```)")
    if re.search(r"!\s*<|!\s*$|IMPORTANT:|NOTE:|WARNING:", text(prose)):
        warns.append("exclamation mark or IMPORTANT:/NOTE: prefix: state it plainly")
    caps = [w for w in re.findall(r"\b[A-Z]{5,}\b", text(prose)) if w not in ("HTTPS", "OWASP", "UTF", "JSON", "CIDR")]
    if len(caps) > 3:
        warns.append(f"ALL CAPS words: {', '.join(sorted(set(caps))[:5])}")
    filler = re.findall(r"\b(simply|just|easily|basically|seamless(?:ly)?|leverage|robust|comprehensive|in order to|please note)\b", text(prose), re.I)
    if filler:
        warns.append(f"filler words: {', '.join(sorted(set(w.lower() for w in filler)))}")
    if len(re.findall(r"<h2", body)) >= 5 and 'ac:name="toc"' not in body:
        warns.append("5+ sections without a table of contents macro")
    return fails, warns


def page_url_parts(url):
    import re
    m = re.match(r"(https://[^/]+)/wiki/.*?/pages/(?:edit-v2/)?(\d+)", url)
    if not m:
        sys.exit(f"ERROR: not a Confluence page URL: {url}")
    return m.group(1), m.group(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["lint", "create", "get", "put", "attach", "detect", "drawio", "zenuml"])
    ap.add_argument("--page-id")
    ap.add_argument("--page-url", help="full page URL: sets --site and --page-id")
    ap.add_argument("--parent-id"), ap.add_argument("--title")
    ap.add_argument("--env-file")
    ap.add_argument("--site", help="override site URL, e.g. https://acme.atlassian.net")
    ap.add_argument("--out"), ap.add_argument("--body-file"), ap.add_argument("--message", default="")
    ap.add_argument("--file"), ap.add_argument("--name"), ap.add_argument("--type")
    ap.add_argument("--edition", choices=["auto", "lite", "full"], default="auto",
                    help="ZenUML app edition: auto tries the full app (\"Graph (DrawIO)\") then Lite")
    ap.add_argument("--update-id", help="existing ZenUML custom content id to update")
    a = ap.parse_args()
    if a.command == "lint":
        fails, warns = lint_body(Path(a.body_file).read_text(encoding="utf-8"))
        for f in fails:
            print(f"  FAIL {f}")
        for w in warns:
            print(f"  WARN {w}")
        print("RESULT:", "ISSUES FOUND" if fails else "CLEAN" + (" (with warnings)" if warns else ""))
        sys.exit(1 if fails else 0)
    if a.page_url:
        a.site, a.page_id = page_url_parts(a.page_url)
    load_env(a.env_file)
    c = Client(a.site)
    if a.command == "create":
        parent = c.page(a.parent_id)
        r = c.call("POST", "/rest/api/content", {
            "type": "page", "title": a.title, "space": {"key": parent["space"]["key"]},
            "ancestors": [{"id": a.parent_id}],
            "body": {"storage": {"value": Path(a.body_file).read_text(encoding="utf-8"), "representation": "storage"}}})
        print(f"Created '{r['title']}' ({r['id']}): {c.base}{r['_links']['webui']}")
        return
    if not a.page_id:
        sys.exit("ERROR: --page-id or --page-url is required")

    if a.command == "get":
        p = c.page(a.page_id)
        print(f"Title  : {p['title']}\nVersion: {p['version']['number']}\nURL    : {c.base}/pages/{p['id']}")
        if a.out:
            Path(a.out).write_text(p["body"]["storage"]["value"], encoding="utf-8")
            print(f"Body   : {a.out}")
    elif a.command == "put":
        r = c.put(a.page_id, Path(a.body_file).read_text(encoding="utf-8"), a.message)
        print(f"Updated '{r['title']}' to version {r['version']['number']}: {c.base}/pages/{r['id']}")
    elif a.command == "attach":
        f = Path(a.file)
        mime = a.type or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        r = c.attach(a.page_id, f.read_bytes(), a.name or f.name, mime)
        print(f"Attached {r.get('title', a.name or f.name)}")
    elif a.command == "detect":
        found = detect_diagrams(c.page(a.page_id)["body"]["storage"]["value"])
        if not found:
            print("No draw.io macro on this page. Insert one diagram through the editor (any title), then run detect again.")
        for variant, title, markup in found:
            print(f"--- {variant} macro: {title}")
            print(markup[:3000])
        if any(v == "forge" for v, _, _ in found):
            print("\nForge variant: reuse the markup above as the template (the extension-key is specific to this site).")
    elif a.command == "zenuml":
        src = Path(a.file)
        ccid, uid, macro = zenuml_publish(c, a.page_id, src.read_text(encoding="utf-8"),
                                          a.name or src.stem, a.edition, a.update_id)
        print(f"<!-- ZenUML custom content {ccid} -->")
        print(macro)
    elif a.command == "drawio":
        src = Path(a.file)
        name = a.name or src.stem
        c.attach(a.page_id, src.read_bytes(), name, "application/vnd.jgraph.mxfile")
        width = 1000
        bin_ = find_drawio()
        if bin_:  # PNG preview used by search, export and page previews
            png = Path(tempfile.mkdtemp()) / f"{name}.png"
            subprocess.run([bin_, "-x", "-f", "png", "-o", str(png), str(src)], capture_output=True, timeout=120)
            if png.exists():
                c.attach(a.page_id, png.read_bytes(), f"{name}.png", "image/png")
                width = int.from_bytes(png.read_bytes()[16:20], "big")
        print(drawio_macro(name, width))


if __name__ == "__main__":
    main()
