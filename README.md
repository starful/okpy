# OKPy

Technical blog for **[okpy.net](https://okpy.net)** — Python library guides and cloud (AWS/GCP/Azure) comparisons. Markdown in-repo, no database.

| | |
|--|--|
| **Live** | [https://okpy.net](https://okpy.net) |
| **GitHub** | [starful/okpy](https://github.com/starful/okpy) |
| **Hub ID** | `okpy` |
| **GA4** | Property `422211768` · GSC `sc-domain:okpy.net` |

## Content categories

| Category | URL | Generator |
|----------|-----|-----------|
| `python` | `/category/python` | `scripts/generate_posts.py python` |
| `cloud` | `/category/cloud` | `scripts/generate_posts.py cloud` |
| `terraform` | `/category/terraform` | `scripts/generate_posts.py terraform` |
| `data-analysis` | `/category/data-analysis` | StatFacts migrate + `scripts/rewrite_data_analysis_ja.py` |

Archive categories (`dev-method`, `data-model`, `pmbok`, `agile-scrum`, `fit-journey`) are display-only.

Posts live in `app/content/posts/<category>/<slug>.md` with YAML frontmatter (`title`, `date`, `category`, `slug`, `summary`, optional `cover`/`lang`).

### StatFacts → Data Analysis

```bash
python3 scripts/migrate_statfacts.py          # EN import (insights + guides)
DATA_ANALYSIS_JA_LIMIT=3 python3 scripts/rewrite_data_analysis_ja.py  # EN→JA batch
```

okadmin Content job **Data Analysis EN→JA**, or pipeline with `CONTENT_PIPELINE_WITH_JA=1`.

## Tech stack

- **Backend:** Flask
- **Content:** Markdown → build step as needed
- **Infra:** Cloud Run (`deploy.sh`, `cloudbuild.yaml`)
- **Images:** GCS `ok-project-assets/okpy/` · Imagen prompt template in `sites.yaml`

## OK Admin pipeline

Separate limits: `PYTHON_LIMIT`, `CLOUD_LIMIT`, `TERRAFORM_LIMIT` (fallback: `CONTENT_LIMIT`). Each runs `scripts/generate_posts.py <category>`.

## Local run

```bash
cd /opt/work/okpy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open [http://localhost:8080](http://localhost:8080).

## SEO: redirects from legacy Hatena

Copy `data/redirects.csv.example` → `data/redirects.csv`:

```csv
old_path,new_url
/entry/old-slug,https://okpy.net/blog/new-slug
```

Restart the app after changes.

## Deploy

```bash
chmod +x deploy.sh
./deploy.sh --deploy-only
./deploy.sh --deploy-only --with-git --with-deploy
```

Defaults: `PROJECT_NAME=okpy`, `SERVICE_URL=https://okpy.net`.

## DNS note

`okpy.net` can point to Cloud Run or Hatena — not both on the same host without a proxy. Typical migration: run on Cloud Run, fill `redirects.csv`, then switch DNS.

## Tests

```bash
python -m pytest tests/ -q
```

## OK Admin

Hub **Content** tab for generation · **Git** tab Ship prep / **Deploy** tab from `main`.

## Related

- [OK Admin](../okadmin/README.md) · [WORK_ROOT](../README.md)
