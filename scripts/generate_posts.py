#!/usr/bin/env python3
"""Generate OKPy blog MD under app/content/posts/{python,cloud,terraform,eng-comms,ai-models}/.

One Claude CLI call per topic. Reads TOPIC_QUEUE_* CSVs from okadmin.
Cover images still use Imagen (GEMINI_API_KEY) when available.
Usage:
  python3 scripts/generate_posts.py python
  python3 scripts/generate_posts.py cloud
  python3 scripts/generate_posts.py terraform
  python3 scripts/generate_posts.py eng-comms
  python3 scripts/generate_posts.py ai-models
"""
from __future__ import annotations

import argparse
import base64
import csv
import os
import re
import subprocess
import sys
import time
import unicodedata
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from batch_limits import (  # noqa: E402
    ai_models_limit,
    cloud_limit,
    eng_comms_limit,
    python_limit,
    terraform_limit,
)
from topic_queue_csv import resolve as resolve_queue_csv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")
load_dotenv()

POSTS_DIR = REPO_ROOT / "app" / "content" / "posts"
IMAGES_DIR = REPO_ROOT / "app" / "static" / "images" / "posts"
CATEGORIES = ("python", "cloud", "terraform", "eng-comms", "ai-models")
# okadmin topic bank id (underscore) → blog category / posts folder (hyphen)
QUEUE_BANK = {
    "python": "python",
    "cloud": "cloud",
    "terraform": "terraform",
    "eng-comms": "eng_comms",
    "ai-models": "ai_models",
}
GCS_IMAGE_BASE = os.getenv(
    "GCS_IMAGE_BASE", "https://storage.googleapis.com/ok-project-assets/okpy"
).rstrip("/")
GCS_BUCKET = os.getenv("GCS_BUCKET", "gs://ok-project-assets/okpy")
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "imagen-4.0-fast-generate-001")

COLUMN = {
    "python": "lib_name",
    "cloud": "Topic",
    "terraform": "Topic",
    "eng-comms": "Topic",
    "ai-models": "Topic",
}


def _claude_md(prompt: str) -> str:
    """MD text via Claude CLI subscription (not Claude API)."""
    _shared = Path(__file__).resolve().parents[2] / "_shared"
    if str(_shared) not in sys.path:
        sys.path.insert(0, str(_shared))
    from site_llm import generate_md_text

    return generate_md_text(prompt)


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
    if category == "eng-comms":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
カテゴリ「エンジニアのコミュニケーション」の記事を Markdown のみで書いてください。
テーマ（状況）: 「{topic}」

要件:
- 必ず日本語のみ（韓国語禁止）
- 先頭は `# タイトル` の H1
- 構成は必ず次を含める:
  1. 状況（非エンジニアからの要望）
  2. たとえ（日常・ビジネスの比喩）
  3. 提案の型（受け取り→たとえ→言い換え→段階案）
  4. ミーティングで使える一文（引用ブロック）
  5. 例外（このたとえを使わない／肯定すべきケース）
  6. まとめ表（相手の言葉 / たとえ / 返し）
- 説教調を避け、現場で使える話し方にする
- 目安 2500〜4500文字
- 前置き不要。H1から開始
"""
    if category == "ai-models":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
テーマ: 「{topic}」
GPT / Claude / Gemini など主要LLMを横断比較する記事を Markdown のみで書いてください。
（cloudカテゴリの AWS vs GCP vs Azure と同じ型。ツールやエージェント構築のハウツーではない）

要件:
- 必ず日本語のみ（韓国語禁止）
- 先頭は `# タイトル` の H1（モデル名をタイトルに含める。可能なら検証年月）
- 各モデルの概要セクション
- 比較表を2つ以上（機能・品質観点・コスト帯・用途など）
- 料金感・運用・ユースケース・選び方・FAQ 3件
- モデル名・料金は変わりうる旨を冒頭で短く注記
- 特定ベンダーの宣伝調を避ける
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


def _cover_prompt(category: str, topic: str) -> str:
    theme = {
        "python": "Python programming and libraries, soft green-gray accents",
        "cloud": "multi-cloud infrastructure comparison, soft blue-gray accents",
        "terraform": "Infrastructure as Code, blueprints and modules, soft terracotta accents",
        "eng-comms": "engineer explaining with everyday business analogies, soft teal charcoal accents",
        "ai-models": "comparing abstract neural network blocks and balance scales, soft slate blue accents",
    }.get(category, "technology")
    return (
        "Editorial tech blog cover illustration, warm paper cream background, "
        "soft graphite sketch style, abstract composition about "
        f"{topic} ({theme}), "
        "no text, no logos, no watermark, clean 16:9 composition, muted charcoal accents"
    )


def _generate_body(category: str, topic: str) -> str | None:
    prompt = _prompt(category, topic)
    last_err = ""
    for attempt in range(2):
        try:
            text = (_claude_md(prompt) or "").strip()
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


def _optimize_cover_jpeg(raw: bytes, out_path: Path) -> None:
    from PIL import Image

    with Image.open(BytesIO(raw)) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((1200, 800), Image.LANCZOS)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "JPEG", quality=82, optimize=True)


def _upload_cover_to_gcs(local_path: Path) -> bool:
    """Best-effort public upload; returns True on success."""
    try:
        dest = f"{GCS_BUCKET.rstrip('/')}/{local_path.name}"
        subprocess.run(
            ["gcloud", "storage", "cp", str(local_path), dest],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["gsutil", "acl", "ch", "-u", "AllUsers:R", dest],
            check=False,
            capture_output=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"  cover upload skipped: {exc}", flush=True)
        return False


def _generate_cover(category: str, topic: str) -> str | None:
    """Generate an Imagen cover, save locally, upload to GCS. Returns public URL."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  cover skipped: GEMINI_API_KEY missing", flush=True)
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=_cover_prompt(category, topic),
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/png",
            ),
        )
        img_bytes = response.generated_images[0].image.image_bytes
        if isinstance(img_bytes, str):
            img_bytes = base64.b64decode(img_bytes)

        name = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        out_path = IMAGES_DIR / name
        _optimize_cover_jpeg(img_bytes, out_path)
        uploaded = _upload_cover_to_gcs(out_path)
        url = f"{GCS_IMAGE_BASE}/{name}"
        if uploaded:
            print(f"  cover {name}", flush=True)
        else:
            print(f"  cover saved locally {out_path.relative_to(REPO_ROOT)} (upload later)", flush=True)
        return url
    except Exception as exc:
        print(f"  cover generation failed: {exc}", flush=True)
        return None


def _write_md(category: str, topic: str, body: str, cover: str | None = None) -> Path:
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
    cover_line = f"cover: {cover!r}\n" if cover else ""
    body_text = body.strip()
    if cover and "![" not in body_text:
        lines = body_text.splitlines()
        insert_at = 0
        for idx, ln in enumerate(lines):
            if ln.startswith("# "):
                insert_at = idx + 1
                break
        lines.insert(insert_at, f"\n![cover]({cover})\n")
        body_text = "\n".join(lines).lstrip("\n")

    fm = (
        "---\n"
        f"title: {title!r}\n"
        f"date: {date.today().isoformat()}\n"
        f"category: {category}\n"
        f"slug: {slug}\n"
        f"summary: {summary!r}\n"
        f"{cover_line}"
        "lang: ja\n"
        "---\n\n"
    )
    path.write_text(fm + body_text + "\n", encoding="utf-8")
    return path


def _read_queue(category: str, limit: int) -> list[str]:
    bank = QUEUE_BANK.get(category, category)
    default = REPO_ROOT / "data" / f"{bank}.csv"
    csv_path = resolve_queue_csv(bank, str(default))
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
            "eng-comms": eng_comms_limit(),
            "ai-models": ai_models_limit(),
        }[category]

    topics = _read_queue(category, limit)
    print(f"🚀 okpy {category}: {len(topics)} pending (limit {limit})")
    if not topics:
        print("✅ No pending topics")
        return {"ok": True, "generated": 0, "failed": 0, "topics": 0}

    generated = failed = 0
    for topic in topics:
        print(f"→ {topic}", flush=True)
        body = _generate_body(category, topic)
        if not body:
            failed += 1
            continue
        cover = _generate_cover(category, topic)
        path = _write_md(category, topic, body, cover=cover)
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
