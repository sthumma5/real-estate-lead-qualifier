"""Shared utilities for the lead qualifier."""

import os
from pathlib import Path


def load_env(path: str = ".env") -> None:
    """Load .env — handles UTF-8, UTF-16, and Windows CP-1252 encodings."""
    p = Path(path)
    if not p.exists():
        return
    for enc in ("utf-8-sig", "utf-16", "utf-8", "cp1252"):
        try:
            for line in p.read_text(encoding=enc).splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
            return
        except Exception:
            continue
