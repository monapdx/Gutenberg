#!/usr/bin/env python3
"""
build_site.py — Static Project Gutenberg directory generator

Reads category JSON files from ./data/
Outputs static HTML into ./site/

Add a new category:
- Drop a new *.json file into data/
- Re-run: python build_site.py
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "site"
CATEGORIES_DIR = OUT_DIR / "categories"

IGNORE_JSON_FILES = {"main-categories.json"}

SITE_TITLE = "Public Domain Directory"
SITE_TAGLINE = "Browse Project Gutenberg by category"

COVER_WIDTH_PX = 120
PREFER_MEDIUM_COVERS = True

# ----------------------------
# Models
# ----------------------------

@dataclass
class Book:
    href: str
    title: str
    author: str
    downloads: Optional[int]
    cover_small: Optional[str]
    cover_medium: Optional[str]


# ----------------------------
# Helpers
# ----------------------------

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9\-]+", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "category"


def title_from_filename(stem: str) -> str:
    return stem.replace("_", " ").replace("-", " ").title()


def parse_downloads(extra: str) -> Optional[int]:
    if not extra:
        return None
    m = re.search(r"([\d,]+)\s*downloads", extra.lower())
    if not m:
        return None
    return int(m.group(1).replace(",", ""))


def upgrade_cover(url: str) -> str:
    if not url:
        return url
    if PREFER_MEDIUM_COVERS:
        url = url.replace(".cover.small.jpg", ".cover.medium.jpg")
    return url


def is_book_row(row: Dict[str, Any]) -> bool:
    return (
        isinstance(row, dict)
        and "link href" in row
        and "title" in row
        and row.get("link href", "").startswith("http")
    )


def load_books(json_path: Path) -> List[Book]:
    raw = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
    books: Dict[str, Book] = {}

    for row in raw:
        if not is_book_row(row):
            continue

        cover_small = row.get("cover-thumb src", "").strip() or None
        cover_medium = upgrade_cover(cover_small) if cover_small else None

        downloads = parse_downloads(row.get("extra", ""))

        book = Book(
            href=row["link href"].strip(),
            title=row.get("title", "").strip(),
            author=row.get("subtitle", "").strip(),
            downloads=downloads,
            cover_small=cover_small,
            cover_medium=cover_medium,
        )

        books[book.href] = book  # de-dupe by URL

    return sorted(
        books.values(),
        key=lambda b: (b.downloads is None, -(b.downloads or 0), b.title.lower()),
    )


def discover_category_files() -> List[Path]:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Missing data folder: {DATA_DIR}")

    return sorted(
        p for p in DATA_DIR.glob("*.json")
        if p.name not in IGNORE_JSON_FILES
    )


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


# ----------------------------
# CSS (REVERTED VERSION)
# ----------------------------

def base_css() -> str:
    return f"""
:root {{
  --border: rgba(0,0,0,0.15);
  --muted: rgba(0,0,0,0.6);
}}

body {{
  margin: 0;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  line-height: 1.35;
}}

a {{ color: inherit; }}

.container {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px;
}}

.header {{
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 12px;
  margin-bottom: 16px;
}}

.brand {{
  font-weight: 800;
}}

.tagline {{
  color: var(--muted);
  font-size: 0.95rem;
}}

.nav {{
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}}

.pill {{
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 10px;
  text-decoration: none;
  font-size: 0.9rem;
}}

.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}}

.card {{
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  grid-template-columns: {COVER_WIDTH_PX}px 1fr;
  gap: 12px;
}}

.cover {{
  width: {COVER_WIDTH_PX}px;
  border-radius: 8px;
  border: 1px solid var(--border);
}}

.meta h3 {{
  margin: 0 0 6px;
  font-size: 1rem;
}}

.meta .author {{
  margin: 0 0 8px;
  color: var(--muted);
}}

.meta .downloads {{
  color: var(--muted);
  font-size: .9rem;
}}

.footer {{
  margin-top: 24px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: .9rem;
}}

.categories {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}}

.cat-card {{
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
}}

.cat-title {{
  font-weight: 700;
  margin: 0 0 6px;
}}

.cat-sub {{
  color: var(--muted);
  margin: 0;
  font-size: .9rem;
}}
""".strip()


# ----------------------------
# HTML pages
# ----------------------------

def page_shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_escape(title)}</title>
<style>{base_css()}</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>
"""


def index_page(categories: List[Tuple[str, str, int]]) -> str:
    cards = "\n".join(
        f"""
<a class="cat-card" href="categories/{slug}.html">
  <div class="cat-title">{html_escape(label)}</div>
  <div class="cat-sub">{count} titles</div>
</a>
""".strip()
        for label, slug, count in categories
    )

    body = f"""
<div class="header">
  <div>
    <div class="brand">{SITE_TITLE}</div>
    <div class="tagline">{SITE_TAGLINE}</div>
  </div>
</div>

<div class="categories">
{cards}
</div>

<div class="footer">
Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""".strip()

    return page_shell(SITE_TITLE, body)


def category_page(label: str, slug: str, books: List[Book]) -> str:
    items = []

    for b in books:
        cover_url = b.cover_medium or b.cover_small or ""
        cover_html = (
            f'<img class="cover" src="{html_escape(cover_url)}" loading="lazy">'
            if cover_url else ""
        )

        downloads = (
            f'<div class="downloads">{b.downloads:,} downloads</div>'
            if b.downloads is not None else ""
        )

        items.append(f"""
<div class="card">
  <a href="{html_escape(b.href)}" target="_blank">{cover_html}</a>
  <div class="meta">
    <h3><a href="{html_escape(b.href)}" target="_blank">{html_escape(b.title)}</a></h3>
    <div class="author">{html_escape(b.author)}</div>
    {downloads}
  </div>
</div>
""".strip())

    body = f"""
<div class="header">
  <div>
    <div class="brand"><a href="../index.html">{SITE_TITLE}</a></div>
    <div class="tagline">{label} · {len(books)} titles</div>
  </div>
  <div class="nav">
    <a class="pill" href="../index.html">Home</a>
  </div>
</div>

<div class="grid">
{''.join(items)}
</div>

<div class="footer">
Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
""".strip()

    return page_shell(f"{label} — {SITE_TITLE}", body)


# ----------------------------
# Build
# ----------------------------

def build():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    CATEGORIES_DIR.mkdir(parents=True)

    category_files = discover_category_files()
    categories_index: List[Tuple[str, str, int]] = []

    for json_path in category_files:
        label = title_from_filename(json_path.stem)
        slug = slugify(json_path.stem)

        books = load_books(json_path)

        html = category_page(label, slug, books)
        (CATEGORIES_DIR / f"{slug}.html").write_text(html, encoding="utf-8")

        categories_index.append((label, slug, len(books)))

    categories_index.sort(key=lambda t: t[0].lower())
    (OUT_DIR / "index.html").write_text(index_page(categories_index), encoding="utf-8")

    print("✅ Site generated:", OUT_DIR)


if __name__ == "__main__":
    build()
