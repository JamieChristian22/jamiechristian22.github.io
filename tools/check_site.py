"""Offline structural checks for the portfolio landing page."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: dict[str, int] = {}
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.filters = 0
        self.projects = 0
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.tags[tag] = self.tags.get(tag, 0) + 1
        a = dict(attrs)
        if a.get("id"):
            if a["id"] in self.ids:
                self.errors.append(f"Duplicate id: {a['id']}")
            self.ids.add(a["id"])
        if tag == "a":
            href = a.get("href")
            if not href:
                self.errors.append("Anchor with no href")
            else:
                self.links.append(href)
        if tag == "button" and "data-filter" in a:
            self.filters += 1
            if a.get("type") != "button":
                self.errors.append("Filter button missing type=button")
        if tag == "article" and "data-category" in a:
            self.projects += 1


root = Path(__file__).resolve().parents[1]
page = root / "index.html"
parser = PageParser()
parser.feed(page.read_text(encoding="utf-8"))

for tag in ("html", "head", "body", "main", "nav", "h1", "title"):
    if parser.tags.get(tag, 0) < 1:
        parser.errors.append(f"Missing required element: {tag}")
if parser.tags.get("h1") != 1:
    parser.errors.append("Expected exactly one top-level h1")
if parser.projects != 9:
    parser.errors.append(f"Expected 9 featured project cards, found {parser.projects}")
if parser.filters != 4:
    parser.errors.append(f"Expected 4 category filters, found {parser.filters}")
for href in parser.links:
    if href.startswith("#") and href[1:] not in parser.ids:
        parser.errors.append(f"Missing local anchor target: {href}")
    if href.startswith("http") and urlparse(href).scheme != "https":
        parser.errors.append(f"External link is not HTTPS: {href}")

print(f"HTML review: {parser.projects} projects, {parser.filters} filter buttons, {len(parser.links)} links")
if parser.errors:
    for err in parser.errors:
        print("FAIL:", err)
    raise SystemExit(1)
print("PASS: offline HTML structure, filter controls and local anchors")
print("LIMIT: this check does not verify JavaScript in a browser, external URLs or Pages hosting")
