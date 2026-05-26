#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from urllib.parse import quote

BASE = "https://chinese-museum.vercel.app"
MAX_URLS_PER_SITEMAP = 500


def slugify(s: str) -> str:
    return quote((s or "unknown").strip().replace(" ", "-"), safe="-")


def render_urlset(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main() -> int:
    data = json.loads(Path("data/artifacts.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()
    urls = [f"  <url>\n    <loc>{BASE}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>"]

    museums = sorted({str(d.get("所属博物馆名称", "")).strip() for d in data if str(d.get("所属博物馆名称", "")).strip()})
    for m in museums:
        urls.append(f"  <url>\n    <loc>{BASE}/#museum-{slugify(m)}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>")

    chunks = [urls[i:i + MAX_URLS_PER_SITEMAP] for i in range(0, len(urls), MAX_URLS_PER_SITEMAP)]
    if len(chunks) == 1:
        Path("sitemap.xml").write_text(render_urlset(chunks[0]), encoding="utf-8")
    else:
        sitemap_files = []
        for i, chunk in enumerate(chunks, start=1):
            name = f"sitemap-{i}.xml"
            Path(name).write_text(render_urlset(chunk), encoding="utf-8")
            sitemap_files.append(name)
        index = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join([f"  <sitemap><loc>{BASE}/{name}</loc></sitemap>" for name in sitemap_files])
            + "\n</sitemapindex>\n"
        )
        Path("sitemap.xml").write_text(index, encoding="utf-8")

    print(f"generated sitemap with {len(urls)} urls in {len(chunks)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
