#!/usr/bin/env python3
"""Rewrite data-analysis EN posts to Japanese (in place).

Picks posts under app/content/posts/data-analysis/ with lang=en (or missing JA),
rewrites title/summary/body via Claude CLI subscription, sets lang=ja.

Usage:
  python3 scripts/rewrite_data_analysis_ja.py
  DATA_ANALYSIS_JA_LIMIT=3 python3 scripts/rewrite_data_analysis_ja.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import frontmatter
import yaml
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
POSTS_DIR = REPO_ROOT / "app" / "content" / "posts" / "data-analysis"

load_dotenv(REPO_ROOT / ".env")
load_dotenv()


def _limit() -> int:
    for key in ("DATA_ANALYSIS_JA_LIMIT", "JA_LIMIT", "CONTENT_LIMIT"):
        raw = os.getenv(key, "").strip()
        if raw.isdigit():
            return max(0, int(raw))
    return 3


def _pending(limit: int) -> list[Path]:
    if not POSTS_DIR.is_dir():
        return []
    out: list[Path] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        post = frontmatter.load(path)
        lang = str(post.get("lang") or "").strip().lower()
        if lang == "ja":
            continue
        # Treat missing/en/other as rewrite candidates (migrated StatFacts are en)
        out.append(path)
        if len(out) >= limit:
            break
    return out


def _strip_fence(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _claude(prompt: str) -> str:
    shared = REPO_ROOT.parent / "shared"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    from site_llm import generate_md_text

    return generate_md_text(prompt)


def _prompt(meta: dict, body: str) -> str:
    title = meta.get("title") or meta.get("slug") or "untitled"
    summary = meta.get("summary") or ""
    return f"""あなたは日本語の技術ブログ「OKPy」の編集者です。
次の英語記事を、OKPyの Data Analysis カテゴリ向けに自然な日本語の技術ブログ記事へ書き直してください。

要件:
- 出力は Markdown 本文のみ（フロントマターや ``` フェンス禁止）
- 先頭に `# {{日本語タイトル}}` を1行置く
- その直後の段落を記事サマリーとして書く（後で summary に使うので、1〜2文）
- 効果サイズ・出典・表・見出し構造はできるだけ保つ
- 「StatFacts」への言及は「OKPy Data Analysis」または一般的な表現に置き換えてよい
- 内部リンク `/blog/...` はそのまま残す
- 誇張せず、計測・実験の文脈で書く

英語タイトル: {title}
英語サマリー: {summary}

--- 英語本文 ---
{body}
"""


def _parse_title_summary(body_ja: str, fallback_title: str, fallback_summary: str) -> tuple[str, str, str]:
    lines = body_ja.splitlines()
    title = fallback_title
    summary = fallback_summary
    rest_start = 0
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip() or fallback_title
        rest_start = 1
        while rest_start < len(lines) and not lines[rest_start].strip():
            rest_start += 1
        # First non-empty paragraph after H1 → summary
        para: list[str] = []
        i = rest_start
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith("#"):
                break
            para.append(lines[i].strip())
            i += 1
        if para:
            summary = " ".join(para)
            rest_start = i
    body = "\n".join(lines[rest_start:]).strip()
    return title, summary, body


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()


def _rewrite_one(path: Path) -> str:
    post = frontmatter.load(path)
    meta = dict(post.metadata)
    body_en = (post.content or "").strip()
    if not body_en:
        return f"skip empty: {path.name}"

    raw = _strip_fence(_claude(_prompt(meta, body_en)))
    title, summary, body_ja = _parse_title_summary(
        raw,
        str(meta.get("title") or path.stem),
        str(meta.get("summary") or ""),
    )
    if not body_ja:
        body_ja = raw

    meta["title"] = title
    meta["summary"] = summary
    meta["lang"] = "ja"
    meta["category"] = "data-analysis"
    if not meta.get("slug"):
        meta["slug"] = path.stem

    text = f"---\n{_yaml_dump(meta)}\n---\n\n{body_ja.strip()}\n"
    path.write_text(text, encoding="utf-8")
    return f"✅ {path.name}"


def main() -> None:
    lim = _limit()
    targets = _pending(lim)
    print(
        f"🇯🇵 data-analysis EN→JA: {len(targets)} post(s) (limit={lim})"
    )
    if not targets:
        print("✅ No pending EN data-analysis posts.")
        print("__OKADMIN_GENERATION_RESULT__{\"rewritten\":0,\"pending\":0}")
        return

    ok = 0
    failures = 0
    for path in targets:
        try:
            print(_rewrite_one(path))
            ok += 1
        except Exception as exc:
            failures += 1
            print(f"❌ {path.name}: {exc}")

    remaining = len(_pending(10_000))
    print(
        f"🎉 rewritten={ok} failed={failures} still_pending≈{remaining}"
    )
    print(
        f'__OKADMIN_GENERATION_RESULT__{{"rewritten":{ok},"failed":{failures},"pending":{remaining}}}'
    )
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
