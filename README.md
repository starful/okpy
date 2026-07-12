# OKPy

Technical blog for **okpy.net** — Python library guides and AWS/GCP/Azure comparisons.

Content is **Markdown in the repo** (no database). Posts are served by Flask on Cloud Run.

## Topics

| Category | Source (generation) | URL |
|----------|---------------------|-----|
| `python` | `hatena/csv/python.csv` → `unified_poster.py py` | `/category/python` |
| `cloud` | `hatena/csv/cloud.csv` → `unified_poster.py cloud` | `/category/cloud` |

Sunday auto job (`/opt/work/ops/auto_register.sh`) can publish to Hatena; for **okpy.net**, add exported Markdown under `app/content/posts/`.

## Post format

Create `app/content/posts/<slug>.md`:

```yaml
---
title: "記事タイトル"
date: 2026-04-29
category: python   # or cloud
slug: my-post-slug
summary: "一覧用の短い説明"
---
```

Body: Markdown (Japanese). H1 in body is optional; `title` in frontmatter is used for SEO.

## Local run

```bash
cd /opt/work/okpy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://localhost:8080

## SEO: 301 from old Hatena paths

Copy `data/redirects.csv.example` → `data/redirects.csv`:

```csv
old_path,new_url
/entry/old-slug,https://okpy.net/blog/new-slug
```

`old_path` is the path only (e.g. Hatena entry path). Restart app after changes.

## Deploy

```bash
chmod +x deploy.sh
./deploy.sh --deploy-only
```

With git push:

```bash
./deploy.sh --deploy-only --with-git --with-deploy
```

Defaults: `PROJECT_NAME=okpy`, `SERVICE_URL=https://okpy.net` (see `cloudbuild.yaml`).

## DNS note

`okpy.net` can point to Cloud Run **or** Hatena — not both on the same host without a proxy. Typical migration:

1. Run blog on Cloud Run (subdomain or path)
2. Fill `data/redirects.csv` for moved articles
3. Shift DNS when ready

## Tests

```bash
python -m pytest tests/ -q
```
