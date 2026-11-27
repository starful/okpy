#!/usr/bin/env python3
"""Generate OKPy blog MD under writable categories.

Writable: python, cloud, terraform, dev-method, data-analysis, eng-comms, ai-models, career.
data-analysis drafts are English (lang: en); Japanese is a separate convert step.
Usage:
  python3 scripts/generate_posts.py python
  python3 scripts/generate_posts.py data-analysis
  python3 scripts/generate_posts.py career
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
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
    career_limit,
    cloud_limit,
    data_analysis_limit,
    dev_method_limit,
    eng_comms_limit,
    python_limit,
    terraform_limit,
)
from topic_queue_csv import resolve as resolve_queue_csv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")
load_dotenv()

POSTS_DIR = REPO_ROOT / "app" / "content" / "posts"
IMAGES_DIR = REPO_ROOT / "app" / "static" / "images" / "posts"
CATEGORIES = (
    "python", "cloud", "terraform", "dev-method",
    "data-analysis", "eng-comms", "ai-models", "career",
)
# okadmin topic bank id (underscore) → blog category / posts folder (hyphen)
QUEUE_BANK = {
    "python": "python",
    "cloud": "cloud",
    "terraform": "terraform",
    "dev-method": "dev_method",
    "data-analysis": "data_analysis",
    "eng-comms": "eng_comms",
    "ai-models": "ai_models",
    "career": "career",
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
    "dev-method": "Topic",
    "data-analysis": "Topic",
    "eng-comms": "Topic",
    "ai-models": "Topic",
    "career": "Topic",
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
    """True when an existing post stem looks like the same topic (ASCII fold).

    Japanese-only filenames strip to empty / tiny stems — those must NOT match
    (``"" in needle`` is always True in Python and caused false "already written").
    """
    needle = re.sub(r"[^a-z0-9]+", "", topic.lower())
    if len(needle) < 4:
        return False
    d = POSTS_DIR / category
    if not d.is_dir():
        return False
    for p in d.glob("*.md"):
        stem = re.sub(r"[^a-z0-9]+", "", p.stem.lower())
        # Skip CJK-only / tiny stems (e.g. "ai") — too weak for containment checks.
        if len(stem) < 4:
            continue
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
    if category == "dev-method":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
カテゴリ「開発方法論」の記事を Markdown のみで書いてください。
テーマ: 「{topic}」

要件:
- 必ず日本語のみ（韓国語禁止）
- 先頭は `# タイトル` の H1
- 概念、現場での進め方、メリット・注意点、小さな実践例、FAQ 3件
- 目安 3500〜6500文字
- 前置き不要。H1から開始
"""
    if category == "career":
        return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
カテゴリ「Career」のIT職種ガイドを Markdown のみで書いてください。
テーマ: 「{topic}」

要件:
- 必ず日本語のみ（韓国語禁止）
- 先頭は `# タイトル` の H1
- 年収帯の目安、必要スキル、未経験からのロードマップ、面接で聞かれやすいこと、FAQ 3件
- 目安 3500〜6500文字
- 前置き不要。H1から開始
"""
    if category == "data-analysis":
        return f"""You are the editor of OKPy's Business Analysis section.
Write an ENGLISH insight / methodology article in Markdown only.
Topic: "{topic}"

Requirements:
- English only (this draft will be translated to Japanese later)
- Start with `# Title` H1 (question or effect-size framing when possible)
- Include an effect snapshot table (intervention, metric, effect size, confidence, context)
- Cite plausible sources as links; do not invent precise stats — say "reported range" when unsure
- Practical takeaway for PMs / analysts
- About 2500–4500 words
- No preamble. Start at H1
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
        "dev-method": "software process diagrams and sticky notes, soft indigo accents",
        "data-analysis": "A/B test charts and effect-size bars, soft olive accents",
        "eng-comms": "engineer explaining with everyday business analogies, soft teal charcoal accents",
        "ai-models": "comparing abstract neural network blocks and balance scales, soft slate blue accents",
        "career": "IT career path roadmap and craft tools, soft taupe accents",
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
    # prose only: tables (| … |), list bullets, quotes, images and HTML made summaries like "| | | |--|" (2026-11-27)
    lines = [ln.strip() for ln in body.splitlines()
             if ln.strip() and not ln.lstrip().startswith(("#", "|", "-", "*", ">", "!", "<", "```"))
             and not re.match(r"^\s*\d+\.\s", ln)]
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

    summary = _summary_from_body(body, topic)
    cover_line = f"cover: {cover!r}\n" if cover else ""
    body_text = body.strip()
    # Insert the cover image right after the H1 when the body has no image yet
    if cover and "![" not in body_text:
        lines = body_text.splitlines()
        insert_at = 0
        for idx, ln in enumerate(lines):
            if ln.startswith("# "):
                insert_at = idx + 1
                break
        lines.insert(insert_at, f"\n![cover]({cover})\n")
        body_text = "\n".join(lines).lstrip("\n")

    lang = "en" if category == "data-analysis" else "ja"
    extra = "ja_pending: true\nsource: hq-draft\n" if lang == "en" else ""
    fm = (
        "---\n"
        f"title: {title!r}\n"
        f"date: {date.today().isoformat()}\n"
        f"category: {category}\n"
        f"slug: {slug}\n"
        f"summary: {summary!r}\n"
        f"{cover_line}"
        f"lang: {lang}\n"
        f"{extra}"
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
            "dev-method": dev_method_limit(),
            "data-analysis": data_analysis_limit(),
            "eng-comms": eng_comms_limit(),
            "ai-models": ai_models_limit(),
            "career": career_limit(),
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
    print(f"__OKADMIN_GENERATION_RESULT__{json.dumps(payload, ensure_ascii=False)}", flush=True)
    if failed:
        print(f"❌ {failed} failed")
        return {"ok": False, **payload}
    print(f"🎉 done generated={generated}")
    return {"ok": True, **payload}


def list_en_data_analysis(limit: int = 20) -> list[Path]:
    """English Business Analysis drafts waiting for Japanese conversion."""
    d = POSTS_DIR / "data-analysis"
    if not d.is_dir():
        return []
    out: list[Path] = []
    for path in sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^lang:\s*en\s*$", text) or "ja_pending: true" in text:
            out.append(path)
            if len(out) >= limit:
                break
    return out


def translate_data_analysis_to_ja(path: Path) -> Path:
    """Convert one EN data-analysis post to Japanese in place."""
    import frontmatter

    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    if str(post.get("lang") or "").lower() == "ja" and not post.get("ja_pending"):
        return path
    body = (post.content or "").strip()
    title = str(post.get("title") or path.stem)
    prompt = f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
次の英語 Business Analysis 記事を自然な日本語に翻訳・ローカライズしてください。

要件:
- 出力は Markdown 本文のみ（YAML frontmatter は書かない）
- 先頭は `# 日本語タイトル` の H1
- 表・リンク・数値はそのまま活かし、説明文を日本語に
- 韓国語禁止
- 前置き不要

英語タイトル: {title}

英語本文:
{body[:12000]}
"""
    ja = (_claude_md(prompt) or "").strip()
    if ja.startswith("```"):
        ja = re.sub(r"^```(?:markdown)?\s*", "", ja)
        ja = re.sub(r"\s*```$", "", ja)
    if not ja:
        raise RuntimeError(f"JA translate failed: {path.name}")
    ja_title = _title_from_body(ja, title)
    ja_summary = _summary_from_body(ja, ja_title)
    cover = post.get("cover")
    cover_line = f"cover: {cover!r}\n" if cover else ""
    fm = (
        "---\n"
        f"title: {ja_title!r}\n"
        f"date: {post.get('date') or date.today().isoformat()}\n"
        f"category: data-analysis\n"
        f"slug: {post.get('slug') or path.stem}\n"
        f"summary: {ja_summary!r}\n"
        f"{cover_line}"
        "lang: ja\n"
        f"source: {post.get('source') or 'hq-draft'}\n"
        "---\n\n"
    )
    path.write_text(fm + ja.strip() + "\n", encoding="utf-8")
    return path


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
