#!/usr/bin/env python3
"""Copy live starful.biz career guides into okpy `career` posts.

Usage:
  python3 scripts/migrate_starful_careers.py
  python3 scripts/migrate_starful_careers.py --dry-run
  python3 scripts/migrate_starful_careers.py --force
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import frontmatter
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUT_DIR = REPO_ROOT / "app" / "content" / "posts" / "career"
JSON_DIR = REPO_ROOT / "app" / "static" / "json"
GCS_COVER = "https://storage.googleapis.com/ok-project-assets/okpy/career"

STARFUL_TITLE_RE = re.compile(
    r"(【Starful】|\s*[|｜]\s*Starful\s*$)",
    re.IGNORECASE,
)


def _starful_root() -> Path:
    return REPO_ROOT.parent / "starful.biz"


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()


def scrub_starful(text: str) -> str:
    if not text:
        return ""
    text = STARFUL_TITLE_RE.sub("", text)
    text = text.replace("Starfulの", "OKPyの")
    text = text.replace("Starfulが", "OKPyが")
    text = text.replace("Starful", "OKPy")
    return re.sub(r"[ \t]{2,}", " ", text).strip(" ｜|")


def rewrite_links(body: str) -> str:
    body = body.replace("https://starful.biz/career/", "/blog/")
    body = body.replace("https://www.starful.biz/career/", "/blog/")
    body = re.sub(r"\]\(/career/([^)/#]+)\)", r"](/blog/\1)", body)
    body = re.sub(
        r"\]\(/mbti/([A-Za-z]{4})\)",
        r"](/category/career/mbti/\1)",
        body,
    )
    body = body.replace("](/mbti)", "](/category/career/mbti)")
    return body


def existing_okpy_slugs() -> set[str]:
    posts = REPO_ROOT / "app" / "content" / "posts"
    slugs = set()
    for path in posts.rglob("*.md"):
        if "posts/career/" in str(path).replace("\\", "/"):
            continue
        try:
            post = frontmatter.load(path)
            slugs.add(str(post.get("slug") or path.stem).strip())
        except Exception:
            slugs.add(path.stem)
    return slugs


def migrate_posts(*, force: bool, dry_run: bool) -> int:
    src_root = _starful_root()
    contents = src_root / "app" / "contents"
    job_data_path = src_root / "app" / "static" / "json" / "job_data.json"
    jobs = json.loads(job_data_path.read_text(encoding="utf-8")).get("jobs") or []
    taken = existing_okpy_slugs()
    written = 0

    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        slug = str(job.get("id") or "").strip()
        src = contents / f"{slug}.md"
        if not slug or not src.is_file():
            print(f"skip missing md: {slug}")
            continue
        if slug in taken:
            raise SystemExit(f"slug collision with existing okpy post: {slug}")

        dest = OUT_DIR / f"{slug}.md"
        if dest.exists() and not force:
            written += 1
            continue

        raw = src.read_text(encoding="utf-8")
        post = frontmatter.loads(raw)
        title = scrub_starful(str(post.get("title") or job.get("title") or slug))
        summary = scrub_starful(
            str(
                job.get("meta_description")
                or post.get("description")
                or post.get("seo_description")
                or ""
            )
        )
        body = rewrite_links(scrub_starful(post.content or ""))
        meta = {
            "title": title,
            "date": str(job.get("published") or "2026-08-08"),
            "category": "career",
            "slug": slug,
            "summary": summary,
            "cover": f"{GCS_COVER}/{slug}.png",
            "lang": "ja",
            "career_track": str(job.get("category") or ""),
        }
        text = f"---\n{_yaml_dump(meta)}\n---\n\n{body.strip()}\n"
        if dry_run:
            print(f"would write {dest.name}")
        else:
            dest.write_text(text, encoding="utf-8")
        written += 1
    return written


def migrate_json(*, force: bool, dry_run: bool) -> None:
    src_json = _starful_root() / "app" / "static" / "json"
    if not dry_run:
        JSON_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("mbti_careers.json", "career_mbti.json"):
        src = src_json / name
        dest = JSON_DIR / name
        if dest.exists() and not force:
            continue
        text = scrub_starful(src.read_text(encoding="utf-8"))
        if dry_run:
            print(f"would write {dest}")
            continue
        dest.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    n = migrate_posts(force=args.force, dry_run=args.dry_run)
    migrate_json(force=args.force, dry_run=args.dry_run)
    print(f"career posts: {n}")


if __name__ == "__main__":
    main()
