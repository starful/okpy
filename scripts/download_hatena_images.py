#!/usr/bin/env python3
"""Download Hatena Fotolife images referenced in okpy markdown posts."""

from __future__ import annotations

import glob
import os
import re
import time
import urllib.parse

import frontmatter
import requests

OKPY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(OKPY_ROOT, "app", "content", "posts")
IMAGES_DIR = os.path.join(OKPY_ROOT, "app", "static", "images", "posts")
LOCAL_PREFIX = "https://storage.googleapis.com/ok-project-assets/okpy"

FID_RE = re.compile(r"\[f:id:([^:\]]+):([^:\]]+):[^\]]+\]")
HATENA_CDN_RE = re.compile(
    r"https?://cdn(?:-ak)?\.f\.st-hatena\.com/images/fotolife/[^\"'\s)>]+",
    re.IGNORECASE,
)
HATENA_IMG_TAG_RE = re.compile(
    r'<img[^>]+src=["\'](https?://cdn(?:-ak)?\.f\.st-hatena\.com/images/fotolife/[^"\']+)["\'][^>]*/?>',
    re.IGNORECASE,
)


def image_id_from_fid(user: str, raw_id: str) -> str | None:
    num = re.sub(r"[^0-9]", "", raw_id)
    if len(num) < 14:
        return None
    return num


def cdn_urls(user: str, image_id: str) -> list[str]:
    ymd = image_id[:8]
    base = f"https://cdn-ak.f.st-hatena.com/images/fotolife/s/{user}/{ymd}/{image_id}"
    return [f"{base}.png", f"{base}.jpg", f"{base}.gif"]


def cdn_url_from_existing(url: str) -> tuple[str, str] | None:
    """Return (image_id, normalized_url) from a Hatena CDN URL."""
    path = urllib.parse.urlparse(url).path
    m = re.search(r"/fotolife/s/[^/]+/\d{8}/(\d{14,})\.(png|jpe?g|gif)$", path, re.I)
    if not m:
        return None
    image_id = m.group(1)
    ext = m.group(2).lower()
    if ext == "jpeg":
        ext = "jpg"
    return image_id, url.split("?")[0]


def local_path(image_id: str, ext: str = "png") -> str:
    return f"{LOCAL_PREFIX}/{image_id}.{ext}"


def disk_path(image_id: str, ext: str = "png") -> str:
    return os.path.join(IMAGES_DIR, f"{image_id}.{ext}")


def download_image(session: requests.Session, user: str, image_id: str) -> tuple[str, str] | None:
    """Download image; return (ext, local_web_path) or None."""
    for ext in ("png", "jpg", "gif"):
        target = disk_path(image_id, ext)
        if os.path.isfile(target) and os.path.getsize(target) > 0:
            return ext, local_path(image_id, ext)

    for url in cdn_urls(user, image_id):
        try:
            resp = session.get(url, timeout=30)
        except requests.RequestException as exc:
            print(f"  ⚠️  request failed {url}: {exc}")
            continue
        if resp.status_code != 200 or not resp.content:
            continue

        ctype = (resp.headers.get("content-type") or "").lower()
        if "jpeg" in ctype or url.endswith(".jpg"):
            ext = "jpg"
        elif "gif" in ctype or url.endswith(".gif"):
            ext = "gif"
        else:
            ext = "png"

        target = disk_path(image_id, ext)
        with open(target, "wb") as fh:
            fh.write(resp.content)
        return ext, local_path(image_id, ext)

    return None


def extract_summary_from_body(body: str, title: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        if line.startswith("!["):
            continue
        if line.startswith("<"):
            continue
        if FID_RE.search(line):
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[*_`#>]", "", line).strip()
        if len(line) > 20:
            return line[:160] + ("…" if len(line) > 160 else "")
    return title[:120]


def replace_fid(text: str, user: str, mapping: dict[str, str]) -> str:
    def repl(match: re.Match) -> str:
        u, raw_id = match.group(1), match.group(2)
        image_id = image_id_from_fid(u, raw_id)
        if not image_id:
            return ""
        local = mapping.get(image_id)
        if not local:
            return ""
        return f"![image]({local})"

    return FID_RE.sub(repl, text)


def replace_hatena_urls(text: str, mapping: dict[str, str]) -> str:
    def repl_url(match: re.Match) -> str:
        url = match.group(0)
        parsed = cdn_url_from_existing(url)
        if not parsed:
            return url
        image_id, _ = parsed
        return mapping.get(image_id, url)

    text = HATENA_CDN_RE.sub(repl_url, text)

    def repl_tag(match: re.Match) -> str:
        url = match.group(1)
        parsed = cdn_url_from_existing(url)
        if not parsed:
            return match.group(0)
        image_id, _ = parsed
        local = mapping.get(image_id)
        if not local:
            return match.group(0)
        return f"![image]({local})"

    return HATENA_IMG_TAG_RE.sub(repl_tag, text)


def collect_references(text: str) -> list[tuple[str, str]]:
    """Return list of (user, image_id). user may be empty for CDN-only refs."""
    refs: list[tuple[str, str]] = []
    seen: set[str] = set()

    for match in FID_RE.finditer(text):
        user, raw_id = match.group(1), match.group(2)
        image_id = image_id_from_fid(user, raw_id)
        if image_id and image_id not in seen:
            seen.add(image_id)
            refs.append((user, image_id))

    for url in HATENA_CDN_RE.findall(text):
        parsed = cdn_url_from_existing(url)
        if parsed and parsed[0] not in seen:
            seen.add(parsed[0])
            refs.append(("", parsed[0]))

    return refs


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "okpy-image-migrator/1.0"})

    md_files = sorted(glob.glob(os.path.join(POSTS_DIR, "**", "*.md"), recursive=True))
    print(f"📚 Scanning {len(md_files)} markdown files...")

    all_refs: dict[str, str] = {}  # image_id -> user
    for path in md_files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for user, image_id in collect_references(text):
            all_refs.setdefault(image_id, user or "starful")

    print(f"🖼️  Found {len(all_refs)} unique Hatena image references")

    mapping: dict[str, str] = {}
    downloaded = 0
    skipped = 0
    failed: list[str] = []

    for i, (image_id, user) in enumerate(sorted(all_refs.items()), 1):
        result = download_image(session, user, image_id)
        if result:
            _, local = result
            mapping[image_id] = local
            downloaded += 1
            if i % 50 == 0:
                print(f"  [{i}/{len(all_refs)}] downloaded {downloaded}")
        else:
            failed.append(image_id)
        time.sleep(0.05)

    already = sum(
        1
        for image_id in all_refs
        if any(os.path.isfile(disk_path(image_id, ext)) for ext in ("png", "jpg", "gif"))
    )
    print(f"✅ Downloaded/verified: {len(mapping)} (on disk: {already})")
    if failed:
        print(f"⚠️  Failed ({len(failed)}): {', '.join(failed[:10])}{'…' if len(failed) > 10 else ''}")

    updated_files = 0
    cover_added = 0
    summary_fixed = 0

    for path in md_files:
        with open(path, encoding="utf-8") as fh:
            post = frontmatter.load(fh)

        body = post.content
        metadata = dict(post.metadata)
        original_body = body
        original_summary = str(metadata.get("summary") or "")

        body = replace_fid(body, "starful", mapping)
        body = replace_hatena_urls(body, mapping)

        summary = original_summary
        if FID_RE.search(summary) or "f.st-hatena.com" in summary:
            for match in FID_RE.finditer(summary):
                image_id = image_id_from_fid(match.group(1), match.group(2))
                if image_id and image_id in mapping:
                    summary = ""
                    break
            if not summary or "f.st-hatena.com" in summary:
                summary = extract_summary_from_body(body, str(metadata.get("title") or ""))
                summary_fixed += 1

        if summary != original_summary:
            metadata["summary"] = summary

        first_image = re.search(r"!\[[^\]]*\]\((/static/images/posts/[^)]+)\)", body)
        if first_image and not metadata.get("cover"):
            metadata["cover"] = first_image.group(1)
            cover_added += 1

        body = re.sub(r"\n{3,}", "\n\n", body)

        if body != original_body or metadata != post.metadata:
            post.metadata = metadata
            post.content = body.strip() + "\n"
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(frontmatter.dumps(post))
            updated_files += 1

    print(f"📝 Updated {updated_files} markdown files")
    print(f"   cover added: {cover_added}, summary fixed: {summary_fixed}")
    print(f"📁 Images directory: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
