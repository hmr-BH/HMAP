#!/usr/bin/env python3
"""cp-detect.py — HMAP M5 copy-paste candidate detector.

Finds exact Type-1 clone candidates: sliding windows of N normalized lines
(indentation stripped; blank and comment-only lines removed) that occur in
>=2 locations. Output is a CANDIDATE list — a human must still review and
merge near-duplicates (same structure, only identifiers/literals differ)
into groups. Group definition: all instances of one template = 1 group.

Usage:
    python cp-detect.py <root> [--ext .py,.ts,.swift] [--window 6]
                        [--exclude node_modules,.git,dist] [--max-groups 50]

Stdlib only. Exit code 0 always (this is a reporter, not a gate).
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict

DEFAULT_EXCLUDE = {
    "node_modules", ".git", "dist", "build", "venv", ".venv", "target",
    "__pycache__", ".next", "obj", "bin", ".idea", ".vscode",
}
DEFAULT_EXT = ".py,.js,.jsx,.ts,.tsx,.java,.swift,.go,.rs,.c,.cc,.cpp,.h,.hpp,.cs,.rb,.php,.kt,.kts,.m,.scala,.lua,.pl,.sh"
COMMENT_PREFIXES = ("//", "#", "/*", "*/", "*", "--", ";", '"""', "'''")


def normalize(line: str):
    """Return the normalized code line, or None to skip it."""
    s = line.strip()
    if not s:
        return None
    for p in COMMENT_PREFIXES:
        if s.startswith(p):
            return None
    return s


def iter_source_files(root: str, exts, exclude):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dirpath, fn)


def main() -> int:
    ap = argparse.ArgumentParser(description="HMAP M5 copy-paste candidate detector")
    ap.add_argument("root", help="project root directory")
    ap.add_argument("--ext", default=DEFAULT_EXT, help="comma-separated extensions")
    ap.add_argument("--window", type=int, default=6, help="window size in normalized lines (default 6, SIG Type-1)")
    ap.add_argument("--exclude", default=",".join(sorted(DEFAULT_EXCLUDE)))
    ap.add_argument("--max-groups", type=int, default=50)
    args = ap.parse_args()

    exts = {e.strip() for e in args.ext.split(",") if e.strip()}
    exclude = {e.strip() for e in args.exclude.split(",") if e.strip()}

    windows = defaultdict(list)  # hash -> [(file, start_line)]
    for path in iter_source_files(args.root, exts, exclude):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                raw = f.readlines()
        except OSError:
            continue
        lines = [(i + 1, t) for i, l in enumerate(raw) if (t := normalize(l))]
        for i in range(len(lines) - args.window + 1):
            chunk = tuple(t for _, t in lines[i : i + args.window])
            h = hashlib.sha1("\n".join(chunk).encode("utf-8")).hexdigest()
            windows[h].append((path, lines[i][0]))

    groups = {h: locs for h, locs in windows.items() if len(locs) >= 2}
    print(f"CP candidate groups: {len(groups)} (window={args.window})")
    for h, locs in sorted(groups.items(), key=lambda kv: -len(kv[1]))[: args.max_groups]:
        print(f"\n--- group: {len(locs)} instances ---")
        for path, ln in locs[:20]:
            print(f"  {path}:{ln}")
    print(
        "\nReminder: these are exact-match CANDIDATES. Merge near-duplicates "
        "(same structure, different identifiers/literals) during manual review; "
        "one template = one group. Systemic = >=3 groups AND every change must "
        "sync >=2 call sites."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
