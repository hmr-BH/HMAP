#!/usr/bin/env python3
"""semantic-surface.py — extract a project's semantic surface for the HMAP SCA protocol (M14).

Usage: python semantic-surface.py <project-root>

Stdlib-only, regex-based heuristics (TS/JS, Python, Swift declarations; other source
extensions contribute to reference counting only). Output = candidate lists; the
evaluator adjudicates every candidate against the exclusion rules in
scoring-rubric.md / ai-slop-signals.md. This tool never auto-penalizes.
"""
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".build", "venv", ".venv",
             "target", "__pycache__", ".next", "bin", "obj", ".idea", ".vscode",
             "DerivedData", "Pods", ".gradle", "out"}
COUNT_EXTS = {".ts", ".tsx", ".js", ".jsx", ".py", ".swift", ".go", ".rs",
              ".java", ".kt", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php"}

DECL = {
    ".ts": re.compile(r"^\s*export\s+(?:default\s+)?(interface|type|enum|class|function|const)\s+(\w+)"),
    ".tsx": re.compile(r"^\s*export\s+(?:default\s+)?(interface|type|enum|class|function|const)\s+(\w+)"),
    ".js": re.compile(r"^\s*export\s+(?:default\s+)?(class|function|const)\s+(\w+)"),
    ".jsx": re.compile(r"^\s*export\s+(?:default\s+)?(class|function|const)\s+(\w+)"),
    ".py": re.compile(r"^(?:class\s+(\w+)|def\s+(\w+))"),
    ".swift": re.compile(r"^\s*(?:public\s+|open\s+)?(struct|class|enum|protocol|func|typealias)\s+(\w+)"),
}
FIELD_RE = {
    "brace": re.compile(r"^\s*(\w+)\s*\??\s*:\s*[^=]"),          # TS interface/type member
    ".swift": re.compile(r"^\s*(?:public\s+)?(?:let|var)\s+(\w+)"),
    ".py": re.compile(r"^\s+(\w+)\s*[:=]"),                      # class-level member
}
ENUM_RE = {
    "brace": re.compile(r"""^\s*(\w+)\s*(?:=\s*["']([^"']*)["'])?\s*,?\s*(?://.*)?$"""),
    ".swift": re.compile(r"""^\s*case\s+(\w+)(?:\s*=\s*"([^"]*)")?"""),
    ".py": re.compile(r"""^\s+(\w+)\s*=\s*(?:["']([^"']*)["']|\w+)"""),
}
SKIP_WORDS = {"let", "var", "case", "default", "where", "if", "else", "return",
              "self", "nil", "none", "static", "import", "from", "for", "while"}
GENERIC_TOKENS = {"data", "info", "item", "manager", "service", "util", "utils", "helper",
                  "common", "base", "type", "config", "state", "view", "model", "entry",
                  "node", "object", "value", "result", "error", "params", "options",
                  "settings", "context", "handler", "controller", "provider", "factory",
                  "builder", "store", "cache", "client", "server", "api", "app", "core",
                  "main", "impl", "dto", "entity", "record", "module", "component"}
LEGIT_PAIRS = [("request", "response"), ("input", "output"), ("query", "command"),
               ("create", "update"), ("read", "write"), ("get", "set"), ("add", "remove"),
               ("start", "stop"), ("open", "close"), ("begin", "end"), ("load", "save"),
               ("encode", "decode"), ("import", "export"), ("source", "target")]
COMMON_VOCAB = {"local", "remote", "default", "none", "auto", "custom", "system", "user",
                "id", "url", "path", "type", "value", "key", "text", "file", "dir", "cache",
                "debug", "release", "true", "false", "null", "get", "set", "add", "read",
                "write", "open", "close", "start", "stop", "left", "right", "top", "bottom",
                "center", "small", "large", "new", "old", "first", "last", "next", "prev",
                "main", "sub", "root", "parent", "child", "asc", "desc", "raw", "full",
                "empty", "min", "max", "low", "high", "on", "off", "up", "down", "name",
                "error", "unknown", "loading", "loaded", "pending", "ready", "success",
                "failure", "cancel", "done", "ok", "warning", "info", "idle", "busy",
                "active", "inactive", "enabled", "disabled", "visible", "hidden",
                "light", "dark", "online", "offline"}
CAMEL = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+")
COMMENT_MARK = re.compile(r"//|#|/\*|\*/|^\s*\*|<!--")


def tokens(name):
    return [t.lower() for t in CAMEL.findall(name)]


def indent_of(ln):
    n = 0
    for ch in ln:
        if ch == " ":
            n += 1
        elif ch == "\t":
            n += 4
        else:
            break
    return n


def collect_files(root):
    return [p for p in root.rglob("*")
            if p.is_file() and p.suffix.lower() in COUNT_EXTS
            and not (set(p.parts) & SKIP_DIRS)]


def brace_body(lines, start_idx):
    """(line_idx, line) pairs from the opening brace to the matching close."""
    depth, body, started = 0, [], False
    for i in range(start_idx, min(start_idx + 500, len(lines))):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        if started:
            body.append((i, lines[i]))
            if depth <= 0:
                break
    return body


def py_body(lines, start_idx, base_indent):
    body = []
    for i in range(start_idx + 1, min(start_idx + 500, len(lines))):
        ln = lines[i]
        if ln.strip() and indent_of(ln) <= base_indent:
            break
        body.append((i, ln))
    return body


def extract(files):
    """symbols: name -> (kind, path, line_no). fields: (type, field) -> (path, line_no).
    enums: [(type, value_name, value_literal, line_idx, path)] — direct members only."""
    symbols, fields, enums = {}, {}, []
    seen_enum = set()
    for p in files:
        ext = p.suffix.lower()
        rx = DECL.get(ext)
        if rx is None:
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines):
            m = rx.match(ln)
            if not m:
                continue
            if ext == ".py":
                kind, name = ("class", m.group(1)) if m.group(1) else ("def", m.group(2))
            else:
                kind, name = m.group(1), m.group(2)
            if not name or name.startswith("_"):
                continue
            if kind in ("func", "def", "function") and indent_of(ln) > 0:
                continue  # functions: top-level only (methods pollute the SI-1 queue)
            symbols.setdefault(name, (kind, p, i + 1))
            if kind not in ("interface", "type", "enum", "class", "struct"):
                continue
            base = indent_of(ln)
            body = py_body(lines, i, base) if ext == ".py" else brace_body(lines, i)
            frx = FIELD_RE.get(ext, FIELD_RE["brace"])
            erx = ENUM_RE.get(ext, ENUM_RE["brace"])
            for bi, bln in body:
                bind = indent_of(bln)
                if not (base < bind <= base + 4):
                    continue  # direct members only — locals/nested types are noise
                if kind == "enum":
                    em = erx.match(bln)
                    if em and em.group(1) not in SKIP_WORDS:
                        key = (name, em.group(1), bi)
                        if key not in seen_enum:
                            seen_enum.add(key)
                            enums.append((name, em.group(1), em.group(2), bi, p))
                else:
                    fm = frx.match(bln)
                    if fm and fm.group(1) not in SKIP_WORDS \
                            and not (ext == ".swift" and fm.group(1) == "body"):
                        fields.setdefault((name, fm.group(1)), (p, bi + 1))
    return symbols, fields, enums


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = collect_files(root)
    texts = {}
    for p in files:
        try:
            texts[p] = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            texts[p] = ""
    symbols, fields, enums = extract(files)

    def refs(name):
        pat = re.compile(r"\b%s\b" % re.escape(name))
        return sum(len(pat.findall(t)) for t in texts.values())

    def field_reads(fname):
        pat = re.compile(r"\.%s\b" % re.escape(fname))
        return sum(len(pat.findall(t)) for t in texts.values())

    print("== SI-1 adjudication queue: top-15 most-referenced exported symbols ==")
    ranked = sorted(((refs(n), n, k, p, ln) for n, (k, p, ln) in symbols.items()),
                    reverse=True)[:15]
    for c, n, k, p, ln in ranked:
        print(f"  {c:5d} refs  {n}  ({k}, {p}:{ln})")

    print("\n== SI-2 candidates: declared fields with zero read sites ==")
    si2 = [(t, f, p, ln) for (t, f), (p, ln) in fields.items() if field_reads(f) == 0]
    for t, f, p, ln in si2[:40]:
        print(f"  {t}.{f}  ({p}:{ln})")
    if len(si2) > 40:
        print(f"  ... and {len(si2) - 40} more")

    print("\n== SI-3 candidates: type-name clusters sharing a domain token "
          "(>=4 chars, token in 2-8 type names) ==")
    names = [n for n, (k, _, _) in symbols.items()
             if k not in ("func", "def", "function", "const")]
    tok2names = {}
    for n in names:
        for t in set(tokens(n)):
            if len(t) >= 4 and t not in GENERIC_TOKENS:
                tok2names.setdefault(t, set()).add(n)
    shown = 0
    for t, ns in sorted(tok2names.items()):
        ns = sorted(ns)
        if not (2 <= len(ns) <= 8):
            continue  # big homogeneous naming families are not concept ghosting
        suspect = []
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                da, db = set(tokens(a)) - set(tokens(b)), set(tokens(b)) - set(tokens(a))
                if len(da) == 1 and len(db) == 1 and \
                        any({next(iter(da)), next(iter(db))} == set(pr) for pr in LEGIT_PAIRS):
                    continue  # legitimate affix pair, not competing authorities
                suspect.append((a, b))
        if not suspect:
            continue
        locs = " / ".join(f"{symbols[a][1].name}:{symbols[a][2]}" for a, _ in suspect[:3])
        print(f"  token \"{t}\": {', '.join(ns)}  ({locs})")
        shown += 1
        if shown >= 40:
            print("  ... more clusters omitted")
            break

    print("\n== SI-4 candidates: enum values outside common vocabulary, "
          "no comment within ±5 lines ==")
    si4 = []
    for tname, vname, vlit, li, p in enums:
        if tname.endswith("CodingKeys"):
            continue  # serialization mapping — explicit SI-4 exclusion
        word = (vlit or vname).lower()
        if len(word) < 3 or word in COMMON_VOCAB or "." in word:
            continue
        lines = texts[p].splitlines()
        lo, hi = max(0, li - 5), min(len(lines), li + 6)
        if any(COMMENT_MARK.search(lines[j]) for j in range(lo, hi)):
            continue
        si4.append((tname, vlit or vname, p, li + 1))
    for tname, v, p, ln in si4[:40]:
        print(f"  {tname}.\"{v}\"  ({p}:{ln})")
    if len(si4) > 40:
        print(f"  ... and {len(si4) - 40} more")

    print(f"\nScanned {len(files)} files: {len(symbols)} symbols, {len(fields)} fields, "
          f"{len(enums)} enum values. Candidates require human adjudication (M14 exclusions).")


if __name__ == "__main__":
    main()
