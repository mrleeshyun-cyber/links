# 추천 링크 모음 (인스타 고정 링크)

`@wellness_plz`, `@daily_1_percent_b` 두 인스타그램 계정의 프로필 링크용 페이지입니다.
인스타 프로필에는 아래 주소를 **한 번만** 걸어 두면, 이후 상품은 이 저장소의 데이터만 갱신해서 바꿉니다.

| 계정 | 고정 링크 |
| --- | --- |
| `@wellness_plz` | https://mrleeshyun-cyber.github.io/links/wellness/ |
| `@daily_1_percent_b` | https://mrleeshyun-cyber.github.io/links/daily/ |
| 안내(루트) | https://mrleeshyun-cyber.github.io/links/ |

## 구조

```
index.html            루트 안내 페이지 (계정 선택)
wellness/index.html   @wellness_plz 페이지
daily/index.html      @daily_1_percent_b 페이지
data/wellness.json    페이지 내용(상품 목록) — 여기만 고치면 됩니다
data/daily.json
assets/style.css      공통 스타일 (모바일 우선, 링크트리 스타일)
scripts/build.py      JSON → HTML 생성기
scripts/update.py     새 상품 추가 + 생성 한 번에
```

HTML은 JSON에서 만들어지는 결과물이라 직접 고치지 않습니다.

## 매일 갱신하는 방법

```bash
# 1) 새 상품 넣고 페이지 다시 굽기 (subId 검사 포함)
python3 scripts/update.py wellness \
  --name "아리프 EVA 소프트 폼롤러 + 운동 가이드 포스터" \
  --price "40,400원" --price-note "첫 구매 쿠폰 28,900원" \
  --note "운동 뒤 종아리 정리용" \
  --url "https://link.coupang.com/re/AFFSDP?lptag=AF1928163&pageKey=8717815555&itemId=25321180945&subId=wellness_plz" \
  --post "https://www.instagram.com/p/DgJFkvoEue0/" \
  --keep 3

# 2) 확인 후 올리기
git add -A && git commit -m "chore: 2026-11-26 wellness 추천 갱신" && git push
```

- `--keep` 만큼만 남기고 오래된 상품은 자동으로 정리됩니다(기본 3).
- `subId` 가 그 계정 값과 다르면 실수를 막기 위해 멈춥니다(의도한 경우 `--force`).
- 상품만 손으로 고치고 싶으면 `data/*.json` 을 편집한 뒤 `python3 scripts/build.py`.

## 상태

- GitHub Pages: `main` 브랜치 루트(`/`) 배포.
- 가격·쿠폰은 올린 날 기준이며, 페이지 하단에 쿠팡파트너스 대가성 문구를 표시합니다.
