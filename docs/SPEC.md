# OKPy SPEC

개발 사양. 비즈니스 요건(목적·독자·하지 말 것·우선순위)은 기획서
`Google Drive AI/okpy/okpy 기획서.html`, 화면은 Claude Design 캔버스
「okpy 화면 설계」(https://claude.ai/artifact/7bip1U9tb2qEN3akuDjUgf).

- 운영: https://okpy.net · 저장소 `starful/okpy` · 로컬 `/opt/work/okpy`
- 런타임: Python 3.10 · Flask + Gunicorn · Jinja · Vanilla JS
- 데이터베이스 없음: 마크다운이 원본, 앱 시작 때 읽어 메모리에 캐시 (`CACHED_POSTS`)

## 1. 폴더 구조

```text
app/
  __init__.py            Flask 앱 · 라우트 · 글 캐시 · sitemap · redirects · visitlog 등록
  config.py              SITE_CONFIG (사이트 이름 · GA · AdSense · 카테고리 12개 라벨/설명)
  blog_categories.py     Hatena 태그 → 카테고리 매핑, PRESERVE_CATEGORIES
  home_data.py           홈 피드 (HOME_LATEST_LIMIT 4 · HOME_CAT_LIMIT 3) · 카드 표지 풀 · IT 트렌드
  related_posts.py       관련 글 3개 (같은 카테고리 가중치 + 인기 점수)
  career_mbti.py         MBTI 16유형 ↔ 커리어 글
  wall.py                월(Wall) 제출 검증 · 큐 · 승인 목록
  amazon_affiliate.py    Amazon JP 검색 링크 (카테고리별 검색어)
  a8_affiliate.py        (이름만 a8) 제휴 박스 컨텍스트
  json_utils.py
  content/posts/<category>/<slug>.md   글 원본 (614편)
  templates/             blog_index · blog_post · mbti_index · mbti_type · wall · about · privacy · contact
                         _story_card · _wall_card · _amazon_cta · _article_back_nav · header · footer
                         (detail · guide_detail · guide_list · index: 예전 템플릿, 라우트 없음)
  static/css/            style.css · blog.css · okpy.css
  static/js/             okpy.js · copy-code.js · toc-active.js · scroll-cue.js · visit_track.js …
  static/json/           career_mbti.json · mbti_careers.json · items_data.json
  static/guides/agentic-system.html   특집 (EN/JA/KO 인터랙티브)
script/                  예전 가이드/아이템 생성기 · build_data.py · fetch/optimize_images.py
scripts/
  generate_posts.py      새 글 생성 (Claude) + 표지 (Imagen) — 쓸 수 있는 카테고리: python · cloud · terraform ·
                         dev-method · data-analysis · eng-comms · ai-models · career
  batch_limits.py        카테고리별 개수 (CONTENT_LIMIT 기본 3, PYTHON_LIMIT · CLOUD_LIMIT … )
  content_quality.py     품질 게이트 (아래 4장)
  generate_data_analysis.py · rewrite_data_analysis_ja.py · fetch_data_analysis_images.py   데이터 분석 (영어 → 일본어)
  refresh_gsc_popular.py data/gsc_popular.json (관련 글 인기 점수)
  post_to_x.py           새 글 X 게시 (GitHub Actions)
  export_hatena_all.py · migrate_statfacts.py · migrate_starful_careers.py · reclassify_posts.py   이전 작업용
data/                    redirects.csv(271) · it_trends.json · wall_approved.json · gsc_popular.json · posted_to_x.json
                         · 토픽 CSV(guides · insights · data_analysis · dev_method · career) · a8/ (커밋됨)
visitkit/                HQ 이용자 보기용 익명 방문 로그 패키지
tests/                   test_api_smoke · test_wall · test_a8_affiliate · test_visitkit
Dockerfile · cloudbuild.yaml · deploy.sh · run.py
.github/workflows/post_to_x.yml
```

실행 중 생기는 `data/visitlog.sqlite3` · `data/wall_queue.json` 등은 커밋하지 않는다.

## 2. 라우트

| 경로 | 내용 |
|---|---|
| `/` | 홈: 특집 2 · IT 트렌드 · 월 3장 · 최신 4 · 토픽 12 · 토픽별 최신 3 (`career`는 최신·혼합 피드 제외 `HOME_FEED_EXCLUDE`) |
| `/category/<category>` | 카테고리 목록. 없는 키는 404 |
| `/blog/<slug>` | 기사. Markdown(tables · toc · fenced_code) → HTML, 중복 H1 제거, 코드 블록 복사 버튼, 목차, 관련 글 3, Amazon 박스 |
| `/category/career/mbti` · `/category/career/mbti/<code>` | MBTI 16유형 → 커리어 |
| `/guide/agentic-system` | 특집 정적 HTML |
| `/wall` (GET · POST) | 월. POST는 검증 후 큐에 저장 |
| `/guide` · `/guide/<path>` · `/item/<path>` | 예전 주소 → `/` 301 |
| (그 밖의 예전 경로) | `data/redirects.csv` (old_path → new_url) 301, Hatena 아카이브 → 카테고리 301 |
| `/sitemap.xml` · `/robots.txt` · `/ads.txt` | SEO · AdSense |
| `/about.html` · `/privacy.html` · `/contact` | 정책 페이지 |
| `/events` · `/hq/api/users` | visitkit (7장) |

## 3. 글 파일 형식 (front matter)

`app/content/posts/<category>/<slug>.md`

```yaml
---
title: 'AWS CDKで始めるInfrastructure as Code実践ガイド（aws-cdk-lib）'
date: 2026-11-17
category: python          # 폴더 이름과 같게
slug: aws-cdk-lib         # URL /blog/<slug>, 바꾸지 않음
summary: '...'            # 카드·메타 설명 (한두 문장)
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261117110221.jpg'   # 선택 (없으면 카테고리 표지 풀)
lang: ja                  # 선택 (없으면 ja). data-analysis 영어 초안은 en
seo_title: '...'          # 선택
seo_description: '...'    # 선택
description: '...'        # 선택
hatena_path: /entry/...   # Hatena에서 옮긴 글 (예전 주소)
source: ...               # 데이터 분석 원본 (StatFacts)
career_track: ...         # career 글
---
# 제목 (본문 H1은 렌더 때 제목과 같으면 제거)
```

- 614편 기준 키 사용: title · date · category · slug · summary 전부, cover 527, lang 343, hatena_path 271, source 150, career_track 116, seo_* 98
- 카테고리 12개 (`config.SITE_CONFIG["blog_categories"]`). 새 글은 8개(1장 generate_posts.py)만, `data-model` · `pmbok` · `agile-scrum` · `fit-journey`는 보관(새 글 없음)
- slug: 영어·일본어 혼합 가능 (Hatena 이전 글), 새 글은 영어 소문자 `-`
- 날짜는 본문을 고쳤을 때만 바꾼다 (`/opt/work/.cursor/rules/seo-safety.mdc`)

## 4. 품질 게이트 (`scripts/content_quality.py`)

| 규칙 | 값 |
|---|---|
| 최소 길이 | 가이드 3,500자 · 인사이트 1,800자 |
| H2 | 3개 이상 |
| 금지 문구 | `BANNED_PHRASES` (definitive guide · game-changing · unlock the secrets · in today's fast-paced · as an expert) |
| 틀 소제목 | `FORBIDDEN_HEADINGS` (what changes · final checklist …) |
| 차단 id | `guide_seed_*` · `guide_expand_*` · `insight_seed_*` |

## 5. 빌드 · 배포

- 로컬: `python run.py` → http://localhost:8080 · 테스트 `pytest -q`
- Docker: `python:3.10-slim`, 빌드 중 `script/build_data.py`(실패 무시), `gunicorn --workers 2 --threads 8 --timeout 120 app:app`
- `cloudbuild.yaml` (저장소에 있음; 프로젝트 `starful-258005`, us-central1):
  1. `okpy-repo/okpy:latest` 캐시 pull → build → push (Artifact Registry `us-central1-docker.pkg.dev/starful-258005/okpy-repo/okpy`)
  2. `gcloud run deploy okpy` — port 8080 · memory 512Mi · unauthenticated
     - env: `SITE_URL` · `ASSET_VERSION` · `GCS_IMAGE_BASE` · `ADSENSE_CLIENT_ID` · `GA_ID` · `STORE_BACKEND=firestore` · `FIRESTORE_COLLECTION=okpy`
     - secret: `VISITLOG_SECRET`
- 배포는 HQ 배포 (main 기준). `deploy.sh --deploy-only [--with-git --with-deploy]` 도우미
- 이미지: `gs://ok-project-assets/okpy/` (표지 프롬프트는 `/opt/work/sites.yaml`의 `gcs.prompt_template`)
- X 게시: `.github/workflows/post_to_x.yml` 매일 23:00 UTC (08:00 JST), secrets `X_API_KEY` · `X_API_SECRET` · `X_ACCESS_TOKEN` · `X_ACCESS_SECRET`

## 6. 설정값

| 이름 | 용도 | 기본 |
|---|---|---|
| `SITE_URL` | sitemap · canonical | https://okpy.net |
| `PORT` | 서버 포트 | 8080 |
| `GA_ID` | GA4 측정 ID | G-L7ZTNPYEF6 |
| `ADSENSE_CLIENT_ID` | AdSense | ca-pub-8780435268193938 |
| `GCS_IMAGE_BASE` | 표지 이미지 주소 | https://storage.googleapis.com/ok-project-assets/okpy |
| `ASSET_VERSION` | 정적 파일 캐시 버스터 | cloudbuild 값 |
| `AMAZON_JP_TAG` | Amazon 태그 | starful06-22 |
| `AFFILIATE_OKPY_ENABLED` (구 `A8_OKPY_ENABLED`) | Amazon 박스 on/off | 1 |
| `WALL_APPROVED_JSON` · `WALL_QUEUE_JSON` | 월 파일 위치 | data/ |
| `STORE_BACKEND` · `FIRESTORE_COLLECTION` · `VISITLOG_SECRET` | visitlog | sqlite (운영 firestore) |
| `CONTENT_LIMIT` · `PYTHON_LIMIT` · `CLOUD_LIMIT` · `TERRAFORM_LIMIT` · `ENG_COMMS_LIMIT` · `AI_MODELS_LIMIT` · `DEV_METHOD_LIMIT` · `DATA_ANALYSIS_LIMIT` · `CAREER_LIMIT` | 생성 개수 | 3 |
| `GEMINI_API_KEY` · `IMAGEN_MODEL` | 표지 생성 | imagen-4.0-fast-generate-001 |

`.env`는 커밋하지 않는다 (`.env.example` 참고).

## 7. HQ 연동

`/opt/work/sites.yaml`의 `okpy` 항목 (HQ가 읽음, 이 저장소에서 바꾸지 않음):

```yaml
- id: okpy
  path: okpy
  analytics: {gsc_site_url: "sc-domain:okpy.net", ga4_property_id: "422211768"}
  gcs: {bucket: ok-project-assets, prefix: okpy/, prompt_template: "..."}
  hq:
    office: datalab      # 1층 Data Lab
    order: 10
    enabled: true
    visitlog: true       # 이용자 보기 = visitkit
    content: okpy_posts  # 글쓰기: 카테고리 + 일본어 주제 1~3개
    automerge: true      # 리뷰 통과 시 자동 머지
```

- 글쓰기: HQ가 카테고리를 고르고 `scripts/generate_posts.py <category>`로 글·표지 생성 → 품질 검사 → PR
- visitlog: `register_visitlog(app, site_id="okpy", db_path=data/visitlog.sqlite3)` · HQ는 `GET /hq/api/users`를 Bearer 토큰으로 읽음
- URL별 숫자: HQ `app/url_stats.py`가 GSC/GA4에서 페이지별 조회·노출·CTR·순위를 가져옴 (제목 꼬리 「— OKPy」 제거)
- 회의: HQ `app/office/meeting.py`가 이 사이트의 이미 있는 글 목록 + 기획서 본문 + URL별 숫자 + 최근 회의 결정·실행 결과를 프롬프트에 넣음

## 8. 테스트

`pytest -q` — test_api_smoke(라우트) · test_wall · test_a8_affiliate · test_visitkit.
