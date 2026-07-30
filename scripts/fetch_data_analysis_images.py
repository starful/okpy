#!/usr/bin/env python3
"""Generate Imagen covers for data-analysis posts missing local/GCS images.

Reads `image_prompt` from `app/content/posts/data-analysis/*.md`,
saves to `app/static/images/posts/{slug}.jpg`, uploads to okpy GCS,
updates `cover` frontmatter.

Usage:
  python3 scripts/fetch_data_analysis_images.py
  python3 scripts/fetch_data_analysis_images.py --force
  DATA_ANALYSIS_IMAGE_LIMIT=5 python3 scripts/fetch_data_analysis_images.py
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import frontmatter
import yaml
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
POSTS_DIR = REPO_ROOT / "app" / "content" / "posts" / "data-analysis"
IMAGES_DIR = REPO_ROOT / "app" / "static" / "images" / "posts"
GCS_BUCKET = os.getenv("GCS_BUCKET", "gs://ok-project-assets/okpy").rstrip("/")
GCS_IMAGE_BASE = os.getenv(
    "GCS_IMAGE_BASE", "https://storage.googleapis.com/ok-project-assets/okpy"
).rstrip("/")
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "imagen-4.0-fast-generate-001")

load_dotenv(REPO_ROOT / ".env")
load_dotenv()


def _limit() -> int:
    raw = os.getenv("DATA_ANALYSIS_IMAGE_LIMIT", "").strip()
    if raw.isdigit():
        return max(0, int(raw))
    return 50


def _yaml_dump(meta: dict) -> str:
    return yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).strip()


def _upload(path: Path) -> bool:
    dest = f"{GCS_BUCKET}/{path.name}"
    try:
        subprocess.run(
            ["gcloud", "storage", "cp", str(path), dest],
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
        print(f"  upload skipped: {exc}")
        return False


def _generate(slug: str, prompt: str, *, force: bool) -> bool:
    out = IMAGES_DIR / f"{slug}.jpg"
    if out.exists() and not force:
        print(f"⏭️  skip exists: {slug}.jpg")
        _upload(out)
        return True
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        print("❌ GEMINI_API_KEY missing")
        return False
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        enhanced = (
            f"{prompt} Editorial infographic illustration, clean modern style, "
            "high quality, no text, no watermark, no logos."
        )
        response = client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=enhanced,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/jpeg",
                person_generation="allow_adult",
            ),
        )
        if not response.generated_images:
            print(f"⚠️  no image: {slug}")
            return False
        img_bytes = response.generated_images[0].image.image_bytes
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img_bytes)
        print(f"✅ {slug}.jpg ({len(img_bytes) // 1024}KB)")
        _upload(out)
        return True
    except Exception as exc:
        print(f"❌ {slug}: {exc}")
        return False


def _pending(limit: int, *, force: bool) -> list[Path]:
    if not POSTS_DIR.is_dir():
        return []
    out: list[Path] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        post = frontmatter.load(path)
        prompt = str(post.get("image_prompt") or "").strip()
        if len(prompt) < 10:
            continue
        slug = str(post.get("slug") or path.stem)
        local = IMAGES_DIR / f"{slug}.jpg"
        if local.exists() and not force:
            continue
        out.append(path)
        if len(out) >= limit:
            break
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    lim = args.limit or _limit()
    targets = _pending(lim, force=args.force)
    print(f"🖼️  data-analysis images: {len(targets)} (limit={lim})")
    if not targets:
        print("✅ nothing to do")
        return 0
    ok = 0
    for path in targets:
        post = frontmatter.load(path)
        meta = dict(post.metadata)
        slug = str(meta.get("slug") or path.stem)
        prompt = str(meta.get("image_prompt") or "")
        if _generate(slug, prompt, force=args.force):
            meta["cover"] = f"{GCS_IMAGE_BASE}/{slug}.jpg"
            path.write_text(
                f"---\n{_yaml_dump(meta)}\n---\n\n{(post.content or '').strip()}\n",
                encoding="utf-8",
            )
            ok += 1
    print(f"🎉 generated/updated {ok}/{len(targets)}")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    raise SystemExit(main())
