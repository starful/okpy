#!/usr/bin/env python3
"""Replace starful career covers with OKPy editorial 16:9 JPEGs.

Usage:
  python3 scripts/generate_career_covers.py --limit 2
  python3 scripts/generate_career_covers.py
  python3 scripts/generate_career_covers.py --force
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import time
from io import BytesIO
from pathlib import Path

import frontmatter
import yaml
from dotenv import load_dotenv
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
POSTS_DIR = REPO_ROOT / "app" / "content" / "posts" / "career"
IMAGES_DIR = REPO_ROOT / "app" / "static" / "images" / "posts" / "career"
GCS_BUCKET = os.getenv("GCS_BUCKET", "gs://ok-project-assets/okpy").rstrip("/")
GCS_PREFIX = f"{GCS_BUCKET}/career"
GCS_IMAGE_BASE = os.getenv(
    "GCS_IMAGE_BASE", "https://storage.googleapis.com/ok-project-assets/okpy"
).rstrip("/")
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "gemini-3.1-flash-image")

load_dotenv(REPO_ROOT / ".env")
load_dotenv()

TRACK_THEME = {
    "ai-data": "data, models, and research notebooks, muted teal-gray accents",
    "cloud-infra": "cloud infrastructure and servers, soft blue-gray accents",
    "cyber-security": "locks, shields, and network nodes, muted charcoal accents",
    "design": "layout grids, pencils, and interface frames, warm taupe accents",
    "engineering": "code, circuits, and tools, graphite green-gray accents",
    "product-management": "roadmaps, sticky notes, and flow arrows, warm brown accents",
    "marketing": "charts and campaign boards, muted terracotta accents",
    "content-strategy": "documents and editorial marks, warm paper accents",
}


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).strip()


def _topic(title: str, slug: str) -> str:
    short = re.split(r"[｜|：:]", title or "")[0].strip()
    short = re.sub(r"(完全ガイド|とは？|になるには)$", "", short).strip(" ？?")
    role = slug.replace("_", " ")
    return short or role


def _prompt(title: str, slug: str, track: str) -> str:
    theme = TRACK_THEME.get(track, "IT career and craft, warm taupe accents")
    topic = _topic(title, slug)
    return (
        "Editorial tech blog cover illustration, warm paper cream background, "
        "soft graphite sketch style, abstract composition about "
        f"{topic} ({theme}), "
        "no text, no letters, no logos, no watermark, no brand names, "
        "clean 16:9 composition, muted charcoal accents"
    )


def _optimize_jpeg(raw: bytes, out_path: Path) -> None:
    with Image.open(BytesIO(raw)) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((1200, 800), Image.LANCZOS)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "JPEG", quality=82, optimize=True)


def _upload(local_path: Path) -> bool:
    dest = f"{GCS_PREFIX}/{local_path.name}"
    try:
        subprocess.run(
            ["gcloud", "storage", "cp", str(local_path), dest],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"  upload skipped: {exc}", flush=True)
        return False


def _generate_bytes(prompt: str) -> bytes:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=IMAGEN_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )
    parts = (response.candidates or [None])[0]
    if not parts or not parts.content:
        raise RuntimeError("empty response")
    for part in parts.content.parts or []:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            return inline.data
    raise RuntimeError("no image in response")


def _write_cover(path: Path, url: str) -> None:
    post = frontmatter.load(path)
    meta = dict(post.metadata)
    meta["cover"] = url
    path.write_text(
        f"---\n{_yaml_dump(meta)}\n---\n\n{(post.content or '').strip()}\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--slug", action="append", default=[])
    args = parser.parse_args()

    posts = sorted(POSTS_DIR.glob("*.md"))
    if args.slug:
        wanted = set(args.slug)
        posts = [p for p in posts if p.stem in wanted]
    if args.limit:
        posts = posts[: args.limit]

    print(f"career covers: {len(posts)} force={args.force}", flush=True)
    ok = 0
    for i, path in enumerate(posts, 1):
        post = frontmatter.load(path)
        slug = str(post.get("slug") or path.stem)
        out = IMAGES_DIR / f"{slug}.jpg"
        url = f"{GCS_IMAGE_BASE}/career/{slug}.jpg"
        if out.exists() and not args.force:
            print(f"[{i}/{len(posts)}] skip exists {slug}.jpg", flush=True)
            if str(post.get("cover") or "") != url:
                _write_cover(path, url)
            ok += 1
            continue
        prompt = _prompt(
            str(post.get("title") or slug),
            slug,
            str(post.get("career_track") or ""),
        )
        try:
            raw = _generate_bytes(prompt)
            _optimize_jpeg(raw, out)
            uploaded = _upload(out)
            _write_cover(path, url)
            note = "uploaded" if uploaded else "local only"
            print(f"[{i}/{len(posts)}] {slug}.jpg ({out.stat().st_size // 1024}KB, {note})", flush=True)
            ok += 1
        except Exception as exc:
            print(f"[{i}/{len(posts)}] FAIL {slug}: {exc}", flush=True)
            time.sleep(2)
            continue
        time.sleep(0.4)
    print(f"done {ok}/{len(posts)}", flush=True)
    return 0 if ok == len(posts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
