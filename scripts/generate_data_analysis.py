#!/usr/bin/env python3
"""Generate OKPy Data Analysis posts (insights + methodology guides).

Ported from StatFacts insight_generator / guide_generator.
Writes `app/content/posts/data-analysis/{id}.md` (lang: en, category: data-analysis).

Usage:
  python3 scripts/generate_data_analysis.py insights 3
  python3 scripts/generate_data_analysis.py guides 2
  python3 scripts/generate_data_analysis.py all 3
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import frontmatter
import yaml
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from content_quality import (  # noqa: E402
    GUIDE_MIN_CHARS,
    INSIGHT_MIN_CHARS,
    QUALITY_PROMPT_RULES,
    is_blocked_guide_id,
    is_blocked_insight_id,
)
from md_clean import prepare_guide_md, prepare_insight_md  # noqa: E402
from topic_queue_csv import resolve as resolve_queue_csv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")
load_dotenv()

POSTS_DIR = REPO_ROOT / "app" / "content" / "posts" / "data-analysis"
GCS_IMAGE_BASE = os.getenv(
    "GCS_IMAGE_BASE", "https://storage.googleapis.com/ok-project-assets/okpy"
).rstrip("/")
CATEGORY = "data-analysis"


def _claude_md(prompt: str) -> str:
    shared = REPO_ROOT.parent / "shared"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    from site_llm import generate_md_text

    return generate_md_text(prompt)


def _emit(**kwargs):
    try:
        from generation_result import emit_generation_result

        emit_generation_result(**kwargs)
    except ImportError:
        pass


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).strip()


def _post_exists(slug: str) -> bool:
    return (POSTS_DIR / f"{slug}.md").is_file()


def _effect_label(meta: dict) -> str:
    unit = str(meta.get("effect_unit") or "percent_relative").replace("_", " ")
    direction = str(meta.get("effect_direction") or "").strip()
    emin, emax = meta.get("effect_min"), meta.get("effect_max")
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
                lines.append(f"- [{name}]({url})" if url else f"- {name}")
            else:
                lines.append(f"- {src}")
        lines.append("")
    return "\n".join(lines)


def _rewrite_links(body: str) -> str:
    body = re.sub(r"\]\(/guide/([^)/#]+)\)", r"](/blog/\1)", body)
    body = re.sub(r"\]\(/insight/([^)/#]+?)(?:_en)?\)", r"](/blog/\1)", body)
    body = body.replace("StatFacts", "OKPy Data Analysis")
    body = body.replace("statfacts.net", "okpy.net")
    return body


def _write_okpy_post(
    *,
    slug: str,
    title: str,
    summary: str,
    post_date: str,
    body: str,
    cover: str = "",
    image_prompt: str = "",
) -> Path:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "title": title,
        "date": post_date,
        "category": CATEGORY,
        "slug": slug,
        "summary": summary or "",
        "lang": "en",
        "source": "data-analysis",
    }
    if cover:
        meta["cover"] = cover
    if image_prompt:
        meta["image_prompt"] = image_prompt
    path = POSTS_DIR / f"{slug}.md"
    path.write_text(
        f"---\n{_yaml_dump(meta)}\n---\n\n{body.strip()}\n", encoding="utf-8"
    )
    return path


def _normalize_categories(raw: str) -> str:
    cats = [c.strip() for c in (raw or "").split(",") if c.strip()]
    return ", ".join(cats) if cats else "business"


def generate_insight(row: dict[str, str]) -> bool:
    iid = (row.get("id") or "").strip().removesuffix("_en")
    topic = (row.get("topic") or iid).strip()
    intervention = (row.get("intervention") or "").strip()
    outcome = (row.get("outcome") or "").strip()
    effect_min = (row.get("effect_min") or "").strip()
    effect_max = (row.get("effect_max") or effect_min).strip()
    effect_unit = (row.get("effect_unit") or "percent_relative").strip()
    categories = _normalize_categories(row.get("categories", ""))
    confidence = (row.get("confidence") or "estimate").strip()
    keywords = (row.get("keywords") or "").strip()

    if is_blocked_insight_id(iid):
        print(f"⏭️ Blocked insight id: {iid}")
        return False
    if _post_exists(iid):
        print(f"⏭️ Exists: {iid}.md")
        return True

    print(f"🚀 [Data Analysis insight] {topic}...")
    feedback = ""
    last_err: Exception | None = None
    today = datetime.now().strftime("%Y-%m-%d")
    for attempt in range(3):
        feedback_block = f"\n[FIX PREVIOUS FAILURE]\n{feedback}\n" if feedback else ""
        prompt = f"""
You are an OKPy Data Analysis editor (okpy.net). Write one English insight article as markdown
about effect sizes / benchmarks for product, growth, and analytics teams.

Use these CSV facts exactly in frontmatter (do not change effect_min/max or unit):
- id: {iid}
- intervention: {intervention}
- outcome: {outcome}
- effect_min: {effect_min}
- effect_max: {effect_max}
- effect_unit: {effect_unit}
- categories: [{categories}]
- confidence: {confidence}
- topic/keywords context: {topic} / {keywords}

{QUALITY_PROMPT_RULES}
{feedback_block}
[Output format — STRICT]
Start with YAML frontmatter delimited by --- lines, then markdown body.
Do NOT use markdown code fences anywhere.

Required frontmatter keys:
id, lang: en, title (question form), categories (yaml list), intervention, outcome,
effect_min, effect_max, effect_unit, effect_direction (increase or decrease),
sample_context (who/when this applies), confidence, date: "{today}",
summary (one line), hook (punchy one line), thumbnail: "/static/images/posts/{iid}.jpg",
image_prompt (one line for Imagen: editorial illustration, no text, no logos),
sources (list of 1–2 items with lowercase keys name and url — real organizations only)

Body: invent unique ## headings for THIS intervention (at least 3). Cover the effect,
when it tends to apply, caveats, and a concrete takeaway.

Keep effect ranges consistent with frontmatter. Tone: concise, cite-style.
Minimum {INSIGHT_MIN_CHARS} characters in body.
"""
        try:
            raw = _claude_md(prompt)
            prepared = prepare_insight_md(
                raw,
                insight_id=iid,
                fallback_title=topic,
                fallback_intervention=intervention,
                fallback_outcome=outcome,
                fallback_summary=topic,
                fallback_image_prompt=f"Editorial illustration about {topic}, no text, no logos",
            )
            post = frontmatter.loads(prepared)
            meta = dict(post.metadata)
            body = _rewrite_links((post.content or "").strip())
            snapshot = _insight_snapshot(meta)
            if snapshot:
                body = f"{snapshot}\n{body}" if body else snapshot
            cover = f"{GCS_IMAGE_BASE}/{iid}.jpg"
            _write_okpy_post(
                slug=iid,
                title=str(meta.get("title") or topic),
                summary=str(meta.get("summary") or meta.get("hook") or topic),
                post_date=str(meta.get("date") or today),
                body=body,
                cover=cover,
                image_prompt=str(meta.get("image_prompt") or ""),
            )
            print(f"✅ [Done] {iid}.md")
            return True
        except Exception as e:
            last_err = e
            feedback = str(e)
            print(f"⚠️  insight attempt {attempt + 1} failed: {e}")
    print(f"❌ [Failed] {iid}: {last_err}")
    return False


def generate_guide(guide_id: str, topic: str, keywords: str) -> bool:
    if is_blocked_guide_id(guide_id):
        print(f"⏭️ Blocked guide id: {guide_id}")
        return False
    if _post_exists(guide_id):
        print(f"⏭️ Exists: {guide_id}.md")
        return True

    print(f"🚀 [Data Analysis guide] {topic}...")
    feedback = ""
    last_err: Exception | None = None
    today = datetime.now().strftime("%Y-%m-%d")
    for attempt in range(2):
        feedback_block = f"\n[FIX PREVIOUS FAILURE]\n{feedback}\n" if feedback else ""
        prompt = f"""
You are an editorial writer for OKPy Data Analysis (okpy.net), covering effect-size
benchmarks, A/B testing methodology, and measurement for product/growth teams.

Write a practical English methodology guide.

[Topic]
- Subject: {topic}
- SEO keywords: {keywords}

{QUALITY_PROMPT_RULES}
{feedback_block}
[Output format — STRICT]
Start with YAML frontmatter, then markdown body. No code fences.

---
lang: en
title: "Clear SEO title about {topic}"
summary: "Two-sentence summary on one line."
date: "{today}"
---

[Body requirements]
1. Hook intro (2–3 sentences) for PMs, growth, or analysts.
2. Use unique H2/H3 sections tailored to THIS topic (at least 3 H2s), bullets, and a short table if helpful.
3. Link concepts to reading OKPy Data Analysis insight cards (effect ranges, confidence, sample_context).
4. Minimum {GUIDE_MIN_CHARS} characters.
5. Prefer internal links like /blog/how-to-read-benchmarks when relevant.

Tone: precise, no hype. Do not invent specific study citations.
"""
        try:
            raw = _claude_md(prompt)
            prepared = prepare_guide_md(
                raw, guide_id=guide_id, fallback_title=topic, fallback_summary=topic
            )
            post = frontmatter.loads(prepared)
            meta = dict(post.metadata)
            body = _rewrite_links((post.content or "").strip())
            _write_okpy_post(
                slug=guide_id,
                title=str(meta.get("title") or topic),
                summary=str(meta.get("summary") or topic),
                post_date=str(meta.get("date") or today),
                body=body,
            )
            print(f"✅ [Done] {guide_id}.md")
            return True
        except Exception as e:
            last_err = e
            feedback = str(e)
            print(f"⚠️  guide attempt {attempt + 1} failed: {e}")
    print(f"❌ [Failed] {guide_id}: {last_err}")
    return False


def _insight_tasks(limit: int) -> list[dict[str, str]]:
    csv_path = resolve_queue_csv("insights", str(REPO_ROOT / "data" / "insights.csv"))
    if not os.path.isfile(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return []
    tasks: list[dict[str, str]] = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if len(tasks) >= limit:
                break
            iid = (row.get("id") or "").strip().removesuffix("_en")
            if not iid or iid.startswith("#") or is_blocked_insight_id(iid):
                continue
            if _post_exists(iid):
                continue
            if not (row.get("intervention") or "").strip():
                continue
            tasks.append(dict(row))
    return tasks


def _guide_tasks(limit: int) -> list[tuple[str, str, str]]:
    csv_path = resolve_queue_csv("guides", str(REPO_ROOT / "data" / "guides.csv"))
    if not os.path.isfile(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return []
    tasks: list[tuple[str, str, str]] = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if len(tasks) >= limit:
                break
            gid = (row.get("id") or "").strip()
            if not gid or gid.startswith("#") or is_blocked_guide_id(gid):
                continue
            if _post_exists(gid):
                continue
            topic = (row.get("topic_en") or gid).strip()
            keywords = (row.get("keywords") or "").strip()
            tasks.append((gid, topic, keywords))
    return tasks


def _run_insights(limit: int, *, dry_run: bool) -> int:
    tasks = _insight_tasks(limit)
    if dry_run:
        print(f"🔔 [dry-run] {len(tasks)} insight(s)")
        for row in tasks:
            print(f"   {row.get('id')}.md")
        _emit(step="insights", topics=len(tasks), generated=0, skipped=len(tasks))
        return 0
    if not tasks:
        print("✨ No new insights to generate.")
        _emit(step="insights", topics=0, generated=0)
        return 0
    ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        for fut in concurrent.futures.as_completed(
            [ex.submit(generate_insight, row) for row in tasks]
        ):
            if fut.result():
                ok += 1
    failed = len(tasks) - ok
    _emit(step="insights", topics=len(tasks), generated=ok, failed=failed)
    return 1 if failed else 0


def _run_guides(limit: int, *, dry_run: bool) -> int:
    tasks = _guide_tasks(limit)
    if dry_run:
        print(f"🔔 [dry-run] {len(tasks)} guide(s)")
        for gid, topic, _ in tasks:
            print(f"   {gid}.md — {topic}")
        _emit(step="guides", topics=len(tasks), generated=0, skipped=len(tasks))
        return 0
    if not tasks:
        print("✨ No new guides to generate.")
        _emit(step="guides", topics=0, generated=0)
        return 0
    ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        for fut in concurrent.futures.as_completed(
            [ex.submit(generate_guide, *t) for t in tasks]
        ):
            if fut.result():
                ok += 1
    failed = len(tasks) - ok
    _emit(step="guides", topics=len(tasks), generated=ok, failed=failed)
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind",
        nargs="?",
        default="insights",
        choices=("insights", "guides", "all"),
    )
    parser.add_argument("limit", nargs="?", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    rc = 0
    if args.kind in ("insights", "all"):
        rc |= _run_insights(args.limit, dry_run=args.dry_run)
    if args.kind in ("guides", "all"):
        rc |= _run_guides(args.limit, dry_run=args.dry_run)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
