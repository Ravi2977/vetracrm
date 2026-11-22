#!/usr/bin/env python3
"""
Site quality check — build ke baad chalao:   python3 src/check.py

Check karta hai: tag balance, duplicate id, toote internal links / #anchors,
<img> par width+height (layout shift se bachav), har page par 1 <h1>,
title (<= 65 chars) aur meta description (70-165 chars), canonical, purane URLs.
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "src", "google-apps-script", "node_modules", "assets"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
        "path", "rect", "circle"}
# Purane URLs jo kabhi nahi tootne chahiye
MUST_EXIST = ["/", "/features/", "/cloud-crm/", "/self-hosted-crm/", "/blog/", "/privacy.html", "/thanks.html"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.links, self.imgs = [], [], [], [], []
        self.h1 = 0
        self.title = ""
        self._in_title = False
        self.desc = None
        self.canonical = None
        self.robots = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        if tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"line {self.getpos()[0]}: unexpected </{tag}> (open: {self.stack[-1] if self.stack else None})")

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def url_to_file(url):
    path = url.split("#")[0].split("?")[0]
    if path.endswith("/"):
        path += "index.html"
    return os.path.join(ROOT, path.lstrip("/"))


def main():
    pages = {}
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(d, f)
                rel = "/" + os.path.relpath(full, ROOT).replace(os.sep, "/")
                url = rel[:-10] if rel.endswith("/index.html") else rel
                p = Page()
                p.feed(open(full, encoding="utf-8").read())
                pages[url or "/"] = p
    problems = []
    for url, p in sorted(pages.items()):
        err = lambda m: problems.append(f"{url}: {m}")
        for e in p.errors[:3]:
            err(e)
        if p.stack:
            err(f"unclosed tags {p.stack[:3]}")
        dup = {i for i in p.ids if p.ids.count(i) > 1}
        if dup:
            err(f"duplicate ids {sorted(dup)}")
        if p.h1 != 1:
            err(f"{p.h1} <h1> tags (expected 1)")
        for img in p.imgs:
            if not (img.get("width") and img.get("height")):
                err(f"<img src={img.get('src')}> missing width/height (layout shift)")
        noindex = "noindex" in p.robots
        if not noindex:
            t = p.title.strip()
            if not t or len(t) > 70:
                err(f"title length {len(t)} (aim <= 65): {t!r}")
            if not p.desc or not (70 <= len(p.desc) <= 165):
                err(f"meta description length {len(p.desc or '')} (aim 120-160)")
            if not p.canonical:
                err("missing canonical")
        for href in p.links:
            if href.startswith(("http", "mailto:", "tel:", "javascript:")):
                continue
            target, _, anchor = href.partition("#")
            if not target:
                if anchor and anchor not in p.ids:
                    err(f"broken in-page anchor #{anchor}")
                continue
            f = url_to_file(target)
            if not os.path.exists(f):
                err(f"broken link {href}")
                continue
            if anchor:
                turl = target if not target.endswith("index.html") else target[:-10]
                tp = pages.get(turl.rstrip("/") + "/" if turl.endswith("/") or turl == "" else turl) or pages.get(turl)
                if tp and anchor not in tp.ids:
                    err(f"broken anchor {href}")
    for u in MUST_EXIST:
        if not os.path.exists(url_to_file(u)):
            problems.append(f"MISSING old URL {u}")
    for line in problems:
        print("✗", line)
    print(f"\nChecked {len(pages)} pages: {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
