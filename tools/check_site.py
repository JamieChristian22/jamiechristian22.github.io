"""Offline structural checks; remote image delivery and visual layout are not tested."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = {}
        self.ids = set()
        self.links = []
        self.images = []
        self.filters = 0
        self.projects = 0
        self.visuals = 0
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.tags[tag] = self.tags.get(tag, 0) + 1
        a = dict(attrs)
        if a.get("id"):
            if a["id"] in self.ids:
                self.errors.append("Duplicate ID: " + a["id"])
            self.ids.add(a["id"])
        if tag == "a":
            href = a.get("href")
            if not href: self.errors.append("Anchor missing href")
            else: self.links.append(href)
            if "project-visual" in (a.get("class") or "").split(): self.visuals += 1
        if tag == "img":
            self.images.append(a)
            if not a.get("src") or not a.get("alt"): self.errors.append("Image missing src or alt")
            if a.get("loading") != "lazy": self.errors.append("Project image missing lazy loading")
            if not (a.get("width") and a.get("height")): self.errors.append("Image missing dimensions")
        if tag == "button" and "data-filter" in a:
            self.filters += 1
            if a.get("type") != "button" or a.get("aria-pressed") not in {"true", "false"}:
                self.errors.append("Filter lacks type or aria-pressed")
        if tag == "article" and "data-category" in a:
            self.projects += 1
            if a["data-category"] not in {"business","data","cloud"}:
                self.errors.append("Unknown category")

html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
p = PageParser()
p.feed(html)
for tag in ("html","head","body","main","nav","h1","title"):
    if p.tags.get(tag,0) < 1: p.errors.append("Missing "+tag)
if p.tags.get("h1") != 1: p.errors.append("Expected exactly one h1")
if p.projects != 9: p.errors.append("Expected 9 cards, found "+str(p.projects))
if p.filters != 4: p.errors.append("Expected 4 filters, found "+str(p.filters))
if p.visuals != 8 or len(p.images) != 8: p.errors.append("Expected 8 GitHub-backed screenshots")
for href in p.links:
    if href.startswith("#") and href[1:] not in p.ids: p.errors.append("Missing anchor "+href)
    if href.startswith("http") and urlparse(href).scheme != "https": p.errors.append("Insecure URL "+href)
for a in p.images:
    url = a.get("src", "")
    parsed = urlparse(url)
    pieces = parsed.path.strip("/").split("/")
    if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
        p.errors.append("Unexpected screenshot source "+url)
    if len(pieces)<5 or pieces[0]!="JamieChristian22" or pieces[2]!="main":
        p.errors.append("Screenshot does not link to portfolio source "+url)
    if not re.search(r"\.(png|jpg|jpeg|svg|webp)$",unquote(parsed.path),re.I):
        p.errors.append("Screenshot has unsupported extension "+url)
print("HTML:",p.projects,"projects,",p.filters,"filters,",len(p.images),"visuals,",len(p.links),"links")
for err in p.errors: print("FAIL:",err)
if p.errors: raise SystemExit(1)
print("PASS: structure, local links, accessible image markup and screenshot sources")
print("LIMIT: no live visual layout or remote asset check")
