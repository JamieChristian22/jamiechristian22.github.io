"""Offline validation of self-hosted portfolio and interactive project cards."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    "assets/business-analyst.png",
    "assets/product-manager.png",
    "assets/project-coordinator.png",
    "assets/data-analyst.png",
    "assets/business-intelligence.png",
    "assets/cybersecurity.png",
    "assets/cloud-engineering.png",
    "assets/aws-security.svg",
}
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags={}
        self.ids=set()
        self.links=[]
        self.images=[]
        self.filters=0
        self.cards=0
        self.errors=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        self.tags[tag]=self.tags.get(tag,0)+1
        name=d.get("id")
        if name:
            if name in self.ids:self.errors.append("Duplicate id "+name)
            self.ids.add(name)
        if tag=="a":
            if not d.get("href"):self.errors.append("Anchor missing href")
            else:self.links.append(d["href"])
        if tag=="img":
            self.images.append(d)
            if not d.get("src") or not d.get("alt"):self.errors.append("Image missing src or alt")
            if d.get("loading")!="lazy":self.errors.append("Project image missing loading=lazy")
            if not d.get("width") or not d.get("height"):self.errors.append("Image missing dimensions")
        if tag=="article" and "data-category" in d:self.cards+=1
        if tag=="button" and "data-filter" in d:
            self.filters+=1
            if d.get("type")!="button" or d.get("aria-pressed") not in ("true","false"):
                self.errors.append("Filter missing accessibility attributes")
p=Inspector()
p.feed((ROOT/"index.html").read_text(encoding="utf-8"))
for tag in ("html","head","body","main","nav","h1","title"):
    if p.tags.get(tag,0)<1:p.errors.append("Missing "+tag)
if p.tags.get("h1")!=1:p.errors.append("Expected one H1")
if p.cards!=9:p.errors.append("Expected nine project cards")
if p.filters!=4:p.errors.append("Expected four category filters")
if len(p.images)!=8:p.errors.append("Expected eight project image elements")
seen=set()
for element in p.images:
    src=element.get("src","")
    seen.add(src)
    if src not in EXPECTED:
        p.errors.append("Unexpected image "+src)
        continue
    target=ROOT/src
    if not target.is_file():
        p.errors.append("Missing "+src)
        continue
    if target.stat().st_size<1000:p.errors.append("Empty or tiny image "+src)
    header=target.read_bytes()[:512]
    if src.endswith(".png") and not header.startswith(bytes.fromhex("89504e470d0a1a0a")):
        p.errors.append("Invalid PNG header "+src)
    if src.endswith(".svg") and b"<svg" not in header:
        p.errors.append("Invalid SVG "+src)
if seen!=EXPECTED:p.errors.append("Local asset list mismatch")
for href in p.links:
    if href.startswith("#") and href[1:] not in p.ids:p.errors.append("Missing fragment "+href)
    if href.startswith("http") and urlparse(href).scheme!="https":
        p.errors.append("Non-HTTPS external link "+href)
print("Projects:",p.cards,"filters:",p.filters,"local images:",len(p.images),"links:",len(p.links))
for e in p.errors:print("FAIL:",e)
if p.errors:raise SystemExit(1)
print("PASS: HTML structure, local asset integrity, image accessibility, filter attributes, local anchors")
print("LIMIT: no mobile/browser audit, external URL check, or runtime cloud verification")
