#!/usr/bin/env python3
"""Import StatFacts insights + guides into okpy as data-analysis EN posts.

Usage:
  python3 scripts/migrate_statfacts.py
  python3 scripts/migrate_statfacts.py --dry-run
  STATFACTS_ROOT=/opt/work/statfacts python3 scripts/migrate_statfacts.py --force
"""
from __future__ import annotations

import argparse
import os
import re
from datetime import date
from pathlib import Path

import frontmatter
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUT_DIR = REPO_ROOT / "app" / "content" / "posts" / "data-analysis"
CATEGORY = "data-analysis"
GCS_STATFACTS = os.getenv(
    "STATFACTS_GCS_BASE",
    "https://storage.googleapis.com/ok-project-assets/statfacts",
).rstrip("/")


def _statfacts_root() -> Path:
    env = os.getenv("STATFACTS_ROOT", "").strip()
    if env:
        return Path(env)
    return REPO_ROOT.parent / "statfacts"


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()


def _rewrite_links(body: str) -> str:
    body = re.sub(r"\]\(/guide/([^)/#]+)\)", r"](/blog/\1)", body)
    body = re.sub(r"\]\(/insight/([^)/#]+?)(?:_en)?\)", r"](/blog/\1)", body)
    body = body.replace("https://statfacts.net/guide/", "https://okpy.net/blog/")
    body = body.replace("https://statfacts.net/insight/", "https://okpy.net/blog/")
    return body


def _effect_label(meta: dict) -> str:
    unit = str(meta.get("effect_unit") or "percent_relative").replace("_", " ")
    direction = str(meta.get("effect_direction") or "").strip()
    emin = meta.get("effect_min")
    emax = meta.get("effect_max")
    if emin is None and emax is None:
        return ""
    if emin is not None and emax is not None:
        span = f"{emin}–{emax}"
    else:
        span = str(emin if emin is not None else emax)
    bits = [span, unit]
    if direction:
        bits.append(direction)
    return " ".join(bits)


def _insight_snapshot(meta: dict) -> str:
    rows = []
    if meta.get("intervention"):
        rows.append(f"| Intervention | {meta['intervention']} |")
    if meta.get("outcome"):
        rows.append(f"| Outcome | {meta['outcome']} |")
    effect = _effect_label(meta)
    if effect:
        rows.append(f"| Effect | {effect} |")
    if meta.get("confidence"):
        rows.append(f"| Confidence | `{meta['confidence']}` |")
    if meta.get("sample_context"):
        rows.append(f"| Context | {meta['sample_context']} |")
    if not rows:
        return ""
    lines = ["## Effect snapshot", "", "| | |", "|--|--|", *rows, ""]
    sources = meta.get("sources") or []
    if isinstance(sources, list) and sources:
        lines.append("### Sources")
        lines.append("")
        for src in sources:
            if isinstance(src, dict):
                name = src.get("name") or src.get("url") or "source"
                url = src.get("url") or ""
                if url:
                    lines.append(f"- [{name}]({url})")
                else:
                    lines.append(f"- {name}")
            else:
                lines.append(f"- {src}")
        lines.append("")
    return "\n".join(lines)


def _cover_for_insight(meta: dict, slug: str) -> str:
    thumb = str(meta.get("thumbnail") or "").strip()
    if thumb.startswith("http"):
        return thumb
    # Prefer GCS public URL for StatFacts assets
    return f"{GCS_STATFACTS}/{slug}.jpg"


def _write_post(
    *,
    slug: str,
    title: str,
    summary: str,
    post_date: str,
    body: str,
    cover: str = "",
    force: bool = False,
    dry_run: bool = False,
) -> str:
    out = OUT_DIR / f"{slug}.md"
    if out.exists() and not force:
        return "skip"
    meta = {
        "title": title,
        "date": post_date,
        "category": CATEGORY,
        "slug": slug,
        "summary": summary or "",
        "lang": "en",
        "source": "statfacts",
    }
    if cover:
        meta["cover"] = cover
    text = f"---\n{_yaml_dump(meta)}\n---\n\n{body.strip()}\n"
    if dry_run:
        return "dry"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return "write"


def _migrate_insights(root: Path, *, force: bool, dry_run: bool) -> dict[str, int]:
    counts = {"write": 0, "skip": 0, "dry": 0, "err": 0}
    content = root / "app" / "content"
    for path in sorted(content.glob("*_en.md")):
        try:
            post = frontmatter.load(path)
            meta = dict(post.metadata)
            slug = str(meta.get("id") or path.stem).removesuffix("_en")
            title = str(meta.get("title") or slug)
            summary = str(meta.get("summary") or meta.get("hook") or "")
            post_date = str(meta.get("date") or date.today().isoformat())
            snapshot = _insight_snapshot(meta)
            body = _rewrite_links((post.content or "").strip())
            if snapshot:
                body = f"{snapshot}\n{body}" if body else snapshot
            cover = _cover_for_insight(meta, slug)
            status = _write_post(
                slug=slug,
                title=title,
                summary=summary,
                post_date=post_date,
                body=body,
                cover=cover,
                force=force,
                dry_run=dry_run,
            )
            counts[status] = counts.get(status, 0) + 1
        except Exception as exc:
            counts["err"] += 1
            print(f"❌ insight {path.name}: {exc}")
    return counts


def _migrate_guides(root: Path, *, force: bool, dry_run: bool) -> dict[str, int]:
    counts = {"write": 0, "skip": 0, "dry": 0, "err": 0}
    guides = root / "app" / "content" / "guides"
    if not guides.is_dir():
        return counts
    for path in sorted(guides.glob("*.md")):
        try:
            post = frontmatter.load(path)
            meta = dict(post.metadata)
            slug = str(meta.get("id") or path.stem)
            title = str(meta.get("title") or slug)
            summary = str(meta.get("summary") or "")
            post_date = str(meta.get("date") or date.today().isoformat())
            body = _rewrite_links((post.content or "").strip())
            status = _write_post(
                slug=slug,
                title=title,
                summary=summary,
                post_date=post_date,
                body=body,
                cover="",
                force=force,
                dry_run=dry_run,
            )
            counts[status] = counts.get(status, 0) + 1
        except Exception as exc:
            counts["err"] += 1
            print(f"❌ guide {path.name}: {exc}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing posts")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--insights-only", action="store_true")
    parser.add_argument("--guides-only", action="store_true")
    args = parser.parse_args()

    root = _statfacts_root()
    if not root.is_dir():
        raise SystemExit(f"StatFacts root not found: {root}")

    print(f"📦 StatFacts → okpy data-analysis from {root}")
    totals = {"write": 0, "skip": 0, "dry": 0, "err": 0}
    if not args.guides_only:
        c = _migrate_insights(root, force=args.force, dry_run=args.dry_run)
        print(f"  insights: {c}")
        for k, v in c.items():
            totals[k] = totals.get(k, 0) + v
    if not args.insights_only:
        c = _migrate_guides(root, force=args.force, dry_run=args.dry_run)
        print(f"  guides:   {c}")
        for k, v in c.items():
            totals[k] = totals.get(k, 0) + v
    print(f"✅ done: {totals} → {OUT_DIR}")


if __name__ == "__main__":
    main()
