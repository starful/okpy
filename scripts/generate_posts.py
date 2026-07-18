#!/usr/bin/env python3
"""Generate OKPy blog MD under app/content/posts/{python,cloud,terraform}/.

One Gemini call per topic. Reads TOPIC_QUEUE_* CSVs from okadmin.
Usage:
  python3 scripts/generate_posts.py python
  python3 scripts/generate_posts.py cloud
  python3 scripts/generate_posts.py terraform
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from batch_limits import cloud_limit, python_limit, terraform_limit  # noqa: E402
from topic_queue_csv import resolve as resolve_queue_csv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")
load_dotenv()

POSTS_DIR = REPO_ROOT / "app" / "content" / "posts"
CATEGORIES = ("python", "cloud", "terraform")

COLUMN = {
    "python": "lib_name",
    "cloud": "Topic",
    "terraform": "Topic",
}


def _slugify(text: str) -> str:
    s = unicodedata.normalize("NFKC", (text or "").strip()).lower()
    s = re.sub(r"[^a-z0-9\u3040-\u30ff\u3400-\u9fff]+", "-", s, flags=re.I)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = f"post-{int(time.time())}"
    # Prefer ASCII-ish slug when possible
    ascii_s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return (ascii_s or s)[:80]


def _existing_slugs(category: str) -> set[str]:
    d = POSTS_DIR / category
    if not d.is_dir():
        return set()
    return {p.stem for p in d.glob("*.md")}


def _topic_already_covered(category: str, topic: str) -> bool:
    needle = re.sub(r"[^a-z0-9]+", "", topic.lower())
    if not needle:
        return False
    d = POSTS_DIR / category
    if not d.is_dir():
        return False
    for p in d.glob("*.md"):
        stem = re.sub(r"[^a-z0-9]+", "", p.stem.lower())
        if needle in stem or stem in needle:
            return True
    return False


def _prompt(category: str, topic: str) -> str:
    if category == "python":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
Pythonライブラリ「{topic}」の実践ガイドを Markdown のみで書いてください。

要件:
- 必ず日本語のみ（韓国語禁止）
- 先頭は `# タイトル` の H1
- TL;DR（3行）、概要、インストール、基本サンプル、注意点、FAQ 3件
- 実務で使えるコード例を含める
- 目安 4000〜7000文字
- 前置き・挨拶は不要。H1から開始
"""
    if category == "cloud":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
テーマ: 「{topic}」
AWS / GCP / Azure を横断比較する記事を Markdown のみで書いてください。

要件:
- 必ず日本語のみ
- 先頭は `# タイトル` の H1
- 比較表を2つ以上
- 料金・運用・ユースケース・選び方・FAQ 3件
- 目安 5000〜8000文字
- 前置き不要。H1から開始
"""
    return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
Terraform テーマ「{topic}」の実践ガイドを Markdown のみで書いてください。

要件:
- 必ず日本語のみ
- 先頭は `# タイトル` の H1
- 概念、HCL例、state、モジュール、注意点、FAQ 3件
- AWS/GCP/Azure との関係があれば簡潔に触れる
- 目安 4000〜7000文字
- 前置き不要。H1から開始
"""


def _setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY missing")
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    return genai.GenerativeModel(model_name)


def _generate_body(model, category: str, topic: str) -> str | None:
    prompt = _prompt(category, topic)
    last_err = ""
    for attempt in range(2):
        try:
            res = model.generate_content(prompt)
            text = (res.text or "").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:markdown)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            if text:
                return text
        except Exception as exc:
            last_err = str(exc)
            time.sleep(5 * (attempt + 1))
    print(f"  generate failed: {last_err}", flush=True)
    return None


def _summary_from_body(body: str, fallback: str) -> str:
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.startswith("#")]
    text = " ".join(lines[:3])
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 160:
        text = text[:157] + "…"
    return text or fallback


def _title_from_body(body: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return re.sub(r"\*+", "", m.group(1)).strip()
    return fallback


def _write_md(category: str, topic: str, body: str) -> Path:
    title = _title_from_body(body, topic)
    slug = _slugify(topic)
    existing = _existing_slugs(category)
    base = slug
    n = 2
    while slug in existing:
        slug = f"{base}-{n}"
        n += 1

    out_dir = POSTS_DIR / category
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.md"

    # Strip duplicate H1 if present — keep body after first heading block
    summary = _summary_from_body(body, topic)
    fm = (
        "---\n"
        f"title: {title!r}\n"
        f"date: {date.today().isoformat()}\n"
        f"category: {category}\n"
        f"slug: {slug}\n"
        f"summary: {summary!r}\n"
        "lang: ja\n"
        "---\n\n"
    )
    path.write_text(fm + body.strip() + "\n", encoding="utf-8")
    return path


def _read_queue(category: str, limit: int) -> list[str]:
    default = REPO_ROOT / "data" / f"{category}.csv"
    csv_path = resolve_queue_csv(category, str(default))
    col = COLUMN[category]
    topics: list[str] = []
    if not os.path.isfile(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return topics
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            topic = (row.get(col) or "").strip()
            if not topic:
                continue
            if _topic_already_covered(category, topic):
                continue
            topics.append(topic)
            if len(topics) >= limit:
                break
    return topics


def generate_category(category: str, limit: int | None = None) -> dict:
    if category not in CATEGORIES:
        raise SystemExit(f"unknown category: {category}")
    if limit is None:
        limit = {
            "python": python_limit(),
            "cloud": cloud_limit(),
            "terraform": terraform_limit(),
        }[category]

    topics = _read_queue(category, limit)
    print(f"🚀 okpy {category}: {len(topics)} pending (limit {limit})")
    if not topics:
        print("✅ No pending topics")
        return {"ok": True, "generated": 0, "failed": 0, "topics": 0}

    model = _setup_gemini()
    generated = failed = 0
    for topic in topics:
        print(f"→ {topic}", flush=True)
        body = _generate_body(model, category, topic)
        if not body:
            failed += 1
            continue
        path = _write_md(category, topic, body)
        print(f"  saved {path.relative_to(REPO_ROOT)}", flush=True)
        generated += 1
        time.sleep(0.5)

    # Structured marker for okadmin pipeline_runner
    payload = {
        "step": category,
        "topics": len(topics),
        "generated": generated,
        "failed": failed,
        "ok": failed == 0,
    }
    import json

    print(f"__OKADMIN_GENERATION_RESULT__{json.dumps(payload, ensure_ascii=False)}", flush=True)
    if failed:
        print(f"❌ {failed} failed")
        return {"ok": False, **payload}
    print(f"🎉 done generated={generated}")
    return {"ok": True, **payload}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("category", choices=CATEGORIES)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    result = generate_category(args.category, limit=args.limit)
    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
