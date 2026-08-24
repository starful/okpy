#!/usr/bin/env python3
"""OKPy wrapper — delegates to hub program-unit A8 CSV generator.

Preferred:
  python3 /opt/work/data/a8/generate_placement_urls.py --program neuro_dive
  python3 /opt/work/data/a8/generate_placement_urls.py --program pro_jin
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parents[2] / "data" / "a8" / "generate_placement_urls.py"
OKPY_PROGRAMS = ("neuro_dive", "pro_jin")


def main() -> None:
    if not HUB.is_file():
        raise SystemExit(f"Hub generator not found: {HUB}")
    args = sys.argv[1:]
    if not args:
        for key in OKPY_PROGRAMS:
            subprocess.check_call([sys.executable, str(HUB), "--program", key])
        return
    subprocess.check_call([sys.executable, str(HUB), *args])


if __name__ == "__main__":
    main()
