#!/usr/bin/env python3
"""모닝 루틴에서 오늘의 추천 상품을 넣고 페이지를 다시 굽는 도구.

예)
    python3 scripts/update.py wellness \\
        --name "아리프 EVA 소프트 폼롤러 + 운동 가이드 포스터" \\
        --price "40,400원" --price-note "첫 구매 쿠폰 28,900원" \\
        --note "운동 뒤 종아리 정리용" \\
        --url "https://link.coupang.com/re/AFFSDP?lptag=AF1928163&pageKey=...&itemId=...&subId=wellness_plz" \\
        --post "https://www.instagram.com/p/..." \\
        --keep 3

동작
- 새 상품을 맨 위 '오늘의 추천'으로 넣고, 기존 항목은 featured 를 해제한다.
- 같은 상품(같은 URL)이 이미 있으면 새 값으로 교체한다(중복 방지).
- --keep 개수만 남기고 오래된 항목을 자른다(기본 3).
- 링크에 해당 계정의 subId 가 없으면 실수를 막기 위해 멈춘다(--force 로 통과).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KST = timezone(timedelta(hours=9))
PAGES = ["wellness", "daily"]


def today_kst() -> str:
    return datetime.now(KST).date().isoformat()


def channel_id(data: dict) -> str:
    return data.get("handle", "").lstrip("@")


def check_subid(url: str, expected: str) -> str | None:
    query = parse_qs(urlparse(url).query)
    got = (query.get("subId") or [""])[0]
    if got == expected:
        return None
    if not got:
        return f"링크에 subId 가 없습니다(기대값 subId={expected})"
    return f"링크의 subId={got} 가 이 계정(subId={expected})과 다릅니다"


def main() -> int:
    parser = argparse.ArgumentParser(description="추천 상품을 추가하고 링크 페이지를 다시 만듭니다.")
    parser.add_argument("page", choices=PAGES)
    parser.add_argument("--name", required=True)
    parser.add_argument("--price", required=True)
    parser.add_argument("--price-note", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--url", required=True)
    parser.add_argument("--post", default="", help="인스타그램 게시물 URL")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (기본: 오늘 KST)")
    parser.add_argument("--keep", type=int, default=3, help="페이지에 남길 상품 수 (기본 3)")
    parser.add_argument("--force", action="store_true", help="subId 검사를 건너뛴다")
    args = parser.parse_args()

    path = DATA / f"{args.page}.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    problem = check_subid(args.url, channel_id(data))
    if problem:
        print(f"[중단] {problem}", file=sys.stderr)
        if not args.force:
            print("        확인 후 다시 실행하거나, 의도한 것이면 --force 를 붙이세요.", file=sys.stderr)
            return 2
        print("        --force 로 진행합니다.", file=sys.stderr)

    item = {
        "date": args.date or today_kst(),
        "name": args.name,
        "price": args.price,
        "note": args.note,
        "url": args.url,
        "featured": True,
    }
    if args.price_note:
        item["price_note"] = args.price_note
    if args.post:
        item["post"] = args.post

    items = [it for it in data.get("items", []) if it.get("url") != args.url]
    for it in items:
        it.pop("featured", None)
    items.insert(0, item)
    items = items[: max(1, args.keep)]
    data["items"] = items
    data["updated"] = item["date"]

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[저장] {path.relative_to(ROOT)} — {len(items)}개 항목")

    sys.path.insert(0, str(ROOT / "scripts"))
    import build  # noqa: E402  (같은 폴더의 생성기)

    for out in build.build():
        print("[생성]", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
