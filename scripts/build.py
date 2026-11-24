#!/usr/bin/env python3
"""정적 링크 페이지 생성기.

`data/wellness.json`, `data/daily.json` 을 읽어
`wellness/index.html`, `daily/index.html`, 루트 `index.html` 을 만든다.
(HTML은 데이터만 바꿔 `python3 scripts/build.py` 로 언제든 다시 만들 수 있다.)

갱신은 보통 `scripts/update.py` 를 쓰면 된다. 예:
    python3 scripts/update.py wellness \\
        --name "아리프 EVA 소프트 폼롤러" --price "40,400원" \\
        --price-note "첫 구매 쿠폰 28,900원" \\
        --url "https://link.coupang.com/re/AFFSDP?lptag=...&subId=wellness_plz" \\
        --note "운동 뒤 종아리 정리용" --post "https://www.instagram.com/p/..." \\
        --date 2026-11-25 --keep 3
"""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAGES = ["wellness", "daily"]
SITE_BASE = "https://mrleeshyun-cyber.github.io/links"
SITE_TITLE = "추천 링크 모음"
SITE_DESC = "@wellness_plz · @daily_1_percent_b 매일 아침 추천하는 제품 링크 모음"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def short_date(iso: str) -> str:
    """2026-11-25 -> 11/25"""
    try:
        y, m, d = iso.split("-")
    except ValueError:
        return iso
    return f"{int(m)}/{int(d)}"


def load(slug: str) -> dict:
    with (DATA / f"{slug}.json").open(encoding="utf-8") as fp:
        return json.load(fp)


def sorted_items(data: dict) -> list[dict]:
    items = list(data.get("items", []))
    items.sort(key=lambda it: (not it.get("featured", False), it.get("date", "")), reverse=False)
    items.sort(key=lambda it: it.get("date", ""), reverse=True)
    items.sort(key=lambda it: 0 if it.get("featured") else 1)
    return items


def head(title: str, desc: str, css_href: str, page_url: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#f2f5f9">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(page_url)}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{css_href}">
</head>"""


def disclosure_footer(data: dict, updated: str) -> str:
    return f"""<footer class="foot">
  <p class="disclosure">{esc(data.get("disclosure", ""))}</p>
  <p class="updated">쿠팡 링크는 제휴 링크이며, 가격·쿠폰은 올린 날 기준입니다 · 최근 업데이트 {esc(updated)}</p>
</footer>"""


def render_account_page(data: dict) -> str:
    slug = data["slug"]
    items = sorted_items(data)
    featured = next((it for it in items if it.get("featured")), None)
    if featured is None and items:
        featured = items[0]
    rest = [it for it in items if it is not featured]
    updated = max((it.get("date", "") for it in items), default="")

    page_url = f"{SITE_BASE}/{slug}/"
    rows = []
    for it in rest:
        rows.append(
            f"""      <li>
        <a class="row" href="{esc(it["url"])}" target="_blank" rel="nofollow sponsored noopener">
          <span class="row-body">
            <span class="row-date">{esc(short_date(it.get("date", "")))}</span>
            <span class="row-name">{esc(it["name"])}</span>
            <span class="row-price">{esc(it.get("price", ""))}</span>
          </span>
          <span class="row-arrow" aria-hidden="true">›</span>
        </a>
      </li>"""
        )
    rows_html = "\n".join(rows) if rows else '      <li><p class="note">지난 추천은 곧 올라옵니다.</p></li>'

    post_link = ""
    if featured and featured.get("post"):
        post_link = (
            f'\n  <a class="mini-link" href="{esc(featured["post"])}" target="_blank" '
            f'rel="noopener">인스타그램 게시물 보기</a>'
        )

    featured_html = ""
    if featured:
        price_note = featured.get("price_note", "")
        price_note_html = f'\n    <span class="price-note">{esc(price_note)}</span>' if price_note else ""
        featured_html = f"""<section class="card featured">
  <span class="badge">오늘의 추천 · {esc(short_date(featured.get("date", "")))}</span>
  <h2>{esc(featured["name"])}</h2>
  <p class="price">{esc(featured.get("price", ""))}{price_note_html}</p>
  <p class="note">{esc(featured.get("note", ""))}</p>
  <a class="cta" href="{esc(featured["url"])}" target="_blank" rel="nofollow sponsored noopener">쿠팡에서 보기</a>{post_link}
</section>"""

    insta = data.get("instagram")
    insta_top = (
        f'<a href="{esc(insta)}" target="_blank" rel="noopener">인스타그램</a>'
        if insta
        else ""
    )

    return f"""{head(data.get("title", SITE_TITLE), data.get("tagline", SITE_DESC), "../assets/style.css", page_url)}
<body class="theme-{esc(data.get("theme", slug))}">
<div class="wrap">
  <nav class="topbar">
    <a href="../">← 전체 링크</a>
    {insta_top}
  </nav>

  <header class="hero">
    <div class="avatar">{esc(data.get("avatar", "@"))}</div>
    <h1>{esc(data.get("handle", ""))}</h1>
    <p class="tagline">{esc(data.get("tagline", ""))}</p>
    <p class="intro">{esc(data.get("intro", ""))}</p>
  </header>

  <main>
    {featured_html}

    <section>
      <div class="section-title">
        <h3>지난 추천</h3>
        <span>최신순</span>
      </div>
      <ul class="list">
{rows_html}
      </ul>
    </section>
  </main>

  {disclosure_footer(data, short_date(updated))}
</div>
</body>
</html>
"""


def render_root(pages: list[dict]) -> str:
    cards = []
    for data in pages:
        items = sorted_items(data)
        latest = items[0]["name"] if items else ""
        desc = data.get("tagline", "")
        cards.append(
            f"""  <a class="account" href="{esc(data["slug"])}/">
    <span class="avatar">{esc(data.get("avatar", "@"))}</span>
    <span class="account-body">
      <span class="account-handle">{esc(data.get("handle", ""))}</span>
      <span class="account-desc">{esc(desc)}</span>
    </span>
    <span class="row-arrow" aria-hidden="true">›</span>
  </a>"""
        )
    cards_html = "\n".join(cards)
    all_dates = [it.get("date", "") for data in pages for it in data.get("items", [])]
    updated = max(all_dates, default="")
    disclosure = pages[0].get("disclosure", "") if pages else ""

    return f"""{head(SITE_TITLE, SITE_DESC, "assets/style.css", SITE_BASE + "/")}
<body class="theme-root">
<div class="wrap">
  <header class="hero">
    <div class="avatar">🔗</div>
    <h1>{esc(SITE_TITLE)}</h1>
    <p class="tagline">매일 아침 고른 추천템을 계정별로 모아 둡니다</p>
    <p class="intro">아래에서 보고 싶은 계정을 골라 주세요.</p>
  </header>

  <main>
{cards_html}
  </main>

  <footer class="foot">
    <p class="disclosure">{esc(disclosure)}</p>
    <p class="updated">쿠팡 링크는 제휴 링크이며, 가격·쿠폰은 올린 날 기준입니다 · 최근 업데이트 {esc(short_date(updated))}</p>
  </footer>
</div>
</body>
</html>
"""


def build() -> list[Path]:
    written = []
    datas = [load(slug) for slug in PAGES]
    for data in datas:
        out = ROOT / data["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_account_page(data), encoding="utf-8")
        written.append(out)
    root = ROOT / "index.html"
    root.write_text(render_root(datas), encoding="utf-8")
    written.append(root)
    return written


if __name__ == "__main__":
    for path in build():
        print("wrote", path.relative_to(ROOT))
