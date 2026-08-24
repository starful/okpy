#!/usr/bin/env python3
"""Build A8 広告掲載URL CSV files for OKPy (program ID + URL, no header)."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_ROOT = ROOT / "app" / "content" / "posts"
OUT_DIR = ROOT / "data" / "a8"
BASE = "https://okpy.net"

# category → (program_id, csv_filename)
PROGRAMS = {
    "neuro_dive": {
        "program_id": "s00000019630003",
        "categories": ("data-analysis", "ai-models", "data-model"),
        "csv": "a8-neuro-dive-placement-urls.csv",
    },
    "pro_jin": {
        "program_id": "s00000020853002",
        "categories": ("eng-comms", "fit-journey"),
        "csv": "a8-pro-jin-placement-urls.csv",
    },
}


def _slugs_in_category(category: str) -> list[str]:
    folder = POSTS_ROOT / category
    if not folder.is_dir():
        return []
    # slug = filename without .md (matches site URL /blog/<slug>)
    return sorted(p.stem for p in folder.glob("*.md"))


def _write_csv(path: Path, program_id: str, urls: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = sorted(dict.fromkeys(urls))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for url in unique:
            writer.writerow([program_id, url])


def main() -> None:
    for key, meta in PROGRAMS.items():
        urls: list[str] = []
        for cat in meta["categories"]:
            urls.append(f"{BASE}/category/{cat}")
            for slug in _slugs_in_category(cat):
                urls.append(f"{BASE}/blog/{slug}")
        out = OUT_DIR / meta["csv"]
        _write_csv(out, meta["program_id"], urls)
        print(f"Wrote {out} ({len(set(urls))} rows, program={meta['program_id']}, key={key})")


if __name__ == "__main__":
    main()
