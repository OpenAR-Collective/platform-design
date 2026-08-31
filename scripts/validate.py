#!/usr/bin/env python3
"""Deterministic checks for the design decisions repository.

Run from the repository root: python3 scripts/validate.py
Exit code 0 means all blocking checks passed. Warnings never block.

Blocking checks: front matter schema, ID format and uniqueness, ID matching
the filename, version format and its coupling to status, the required
Decision section, banned characters, sentences beginning with coordinating
conjunctions, resolvable relative links, INDEX.md staying in sync with the
decision files, and the onboarding territory list agreeing across the four
files that carry it.

With --base <git ref>, the script also compares every changed decision file
against that ref: a version may not go backwards, and a change to the
Decision section must raise the major version. Continuous integration passes
the pull request's base branch; run it locally as
python3 scripts/validate.py --base main before opening a pull request.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECISIONS_DIR = os.path.join(ROOT, "decisions")

REQUIRED_KEYS = ["id", "title", "status", "area", "version", "date", "supersedes", "license"]
VERSION_RE = re.compile(r"^(\d+)\.(\d+)$")
STATUS_VALUES = {"Proposed", "Accepted", "Superseded", "Rejected"}
# Module abbreviations: add a new module here when its folder and README are created.
MODULE_PREFIXES = ["PURCHASE", "UNSECURED"]
ID_RE = re.compile(r"^(SHARED|WAX|HIVE|MOD-(" + "|".join(MODULE_PREFIXES) + r"))-\d{4}$")

BANNED_CHARS = {
    "\u2014": "em dash",
    "\u2013": "en dash",
    "\u2018": "curly apostrophe (left)",
    "\u2019": "curly apostrophe (right)",
    "\u201c": "curly quote (left)",
    "\u201d": "curly quote (right)",
    "\u2026": "ellipsis character",
    "\u2192": "arrow",
    "\u2190": "arrow",
    "\u21d2": "arrow",
    "\u2022": "bullet character",
    "\u00a0": "non-breaking space",
}
CONJUNCTION_RE = re.compile(r"(?:^|(?<=[.!?] )|(?<=[.!?]  ))(And|But|Or|So|Yet|Nor) [a-z]")

errors = []
warnings = []


def err(path, line, msg):
    errors.append(f"{os.path.relpath(path, ROOT)}:{line}: {msg}")


def warn(path, line, msg):
    warnings.append(f"{os.path.relpath(path, ROOT)}:{line}: {msg}")


def parse_front_matter(lines, path):
    if not lines or lines[0].strip() != "---":
        err(path, 1, "missing front matter")
        return {}, 0
    fm = {}
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fm, i
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    err(path, 1, "unterminated front matter")
    return fm, 0


def prose_lines(lines, fm_end):
    """Yield (line_number, text) for style checking, skipping fenced code."""
    in_fence = False
    for n, line in enumerate(lines[fm_end:], start=fm_end + 1):
        stripped = line.lstrip("> ").strip() if line.startswith(">") else line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield n, line


def check_file(path, ids_seen, decision_paths):
    lines = open(path, encoding="utf-8").read().split("\n")
    is_decision = os.path.commonpath([path, DECISIONS_DIR]) == DECISIONS_DIR and not path.endswith("README.md")
    if lines and lines[0].strip() == "---":
        fm, fm_end = parse_front_matter(lines, path)
    else:
        fm, fm_end = {}, 0
        if is_decision:
            err(path, 1, "missing front matter")

    if is_decision:
        for key in REQUIRED_KEYS:
            if key not in fm:
                err(path, 1, f"front matter missing required key: {key}")
        fid = fm.get("id", "")
        if fid:
            if not ID_RE.match(fid):
                err(path, 1, f"id {fid!r} does not match FAMILY-NNNN")
            if fid in ids_seen:
                err(path, 1, f"duplicate id {fid}, also in {ids_seen[fid]}")
            ids_seen[fid] = os.path.relpath(path, ROOT)
            if not os.path.basename(path).startswith(fid + "-"):
                err(path, 1, f"filename does not begin with id {fid}")
        if fm.get("status") and fm["status"] not in STATUS_VALUES:
            err(path, 1, f"status {fm['status']!r} not one of {sorted(STATUS_VALUES)}")
        if fm.get("version"):
            vm = VERSION_RE.match(fm["version"])
            if not vm:
                err(path, 1, f"version {fm['version']!r} is not MAJOR.MINOR")
            else:
                major = int(vm.group(1))
                status = fm.get("status")
                if status == "Proposed" and major != 0:
                    err(path, 1, f"a Proposed decision carries a 0.x version, not {fm['version']}")
                if status in ("Accepted", "Superseded") and major < 1:
                    err(path, 1, f"an {status} decision carries version 1.0 or higher, not {fm['version']}")
        body = "\n".join(lines[fm_end:])
        if "\n## Decision" not in body:
            err(path, fm_end + 1, "missing required section: ## Decision")
        for section in ("## Implementation Phasing", "## Implications For Contributors"):
            if section not in body:
                warn(path, fm_end + 1, f"recommended section absent: {section}")

    for n, line in prose_lines(lines, fm_end):
        for ch, name in BANNED_CHARS.items():
            if ch in line:
                err(path, n, f"banned character: {name}")
        if not line.lstrip().startswith("|"):
            m = CONJUNCTION_RE.search(line.lstrip("> #-*0123456789. "))
            if m:
                err(path, n, f"sentence begins with a conjunction: {m.group(1)!r}")

    # Relative Markdown links must resolve.
    for n, line in enumerate(lines, start=1):
        for m in re.finditer(r"\]\(([^)#\s]+\.md)(#[^)]*)?\)", line):
            target = m.group(1)
            if target.startswith("http"):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(resolved):
                err(path, n, f"broken link: {target}")


def check_index(decision_paths):
    index_path = os.path.join(ROOT, "INDEX.md")
    if not os.path.exists(index_path):
        errors.append("INDEX.md: file missing")
        return
    index = open(index_path, encoding="utf-8").read()
    for rel in decision_paths:
        if rel not in index:
            errors.append(f"INDEX.md: no entry links to {rel}")


TERRITORY_SOURCES = {
    "START-HERE.md": "start-here",
    ".github/ISSUE_TEMPLATE/how-we-handle-this.yml": "form",
    ".github/ISSUE_TEMPLATE/report-a-gap.yml": "form",
    "skills/contributor-onboarding/references/probes.md": "probes",
}


def territories_in(path, kind):
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    if kind == "start-here":
        m = re.search(r"### Step 3: Territory\n(.*?)\n\n(?=[A-Z])", text, flags=re.S)
        block = m.group(1) if m else ""
        items = re.findall(r"^\d+\. (.+)$", block, flags=re.M)
    elif kind == "form":
        m = re.search(r"id: territory\n.*?options:\n((?:        - [^\n]+\n)+)", text, flags=re.S)
        items = re.findall(r"^        - (.+)$", m.group(1), flags=re.M) if m else []
    else:
        items = re.findall(r"^## \d+\. (.+)$", text, flags=re.M)
    return [i.strip() for i in items if i.strip() != "Something else"]


def check_territories():
    lists = {path: territories_in(path, kind) for path, kind in TERRITORY_SOURCES.items()}
    reference_path = "START-HERE.md"
    reference = lists[reference_path]
    if not reference:
        errors.append(f"{reference_path}: could not read the Step 3 territory list")
        return
    for path, items in lists.items():
        if items != reference:
            missing = [t for t in reference if t not in items]
            extra = [t for t in items if t not in reference]
            detail = []
            if missing:
                detail.append("missing " + ", ".join(repr(t) for t in missing))
            if extra:
                detail.append("extra " + ", ".join(repr(t) for t in extra))
            if not detail:
                detail.append("same territories in a different order")
            errors.append(f"{path}: territory list disagrees with {reference_path} ({'; '.join(detail)})")


def parse_version(text):
    m = re.search(r"^version:\s*(\d+)\.(\d+)\s*$", text, flags=re.M)
    return (int(m.group(1)), int(m.group(2))) if m else None


def decision_section(text):
    """The text of the Decision section with whitespace collapsed, or None."""
    m = re.search(r"\n## Decision[^\n]*\n(.*?)(?=\n## |\Z)", text, flags=re.S)
    return " ".join(m.group(1).split()) if m else None


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def check_version_bumps(base_ref):
    """Compare changed decision files against base_ref (working tree vs merge base)."""
    try:
        merge_base = git("merge-base", base_ref, "HEAD").strip()
        status = git("diff", "--name-status", "-M", merge_base, "--", "decisions")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        errors.append(f"version check: could not compare against {base_ref}: {e}")
        return
    for line in status.splitlines():
        parts = line.split("\t")
        code = parts[0][0]
        if code == "M":
            old_path = new_path = parts[1]
        elif code == "R":
            old_path, new_path = parts[1], parts[2]
        else:
            continue
        if os.path.basename(new_path) == "README.md":
            continue
        full = os.path.join(ROOT, new_path)
        if not os.path.exists(full):
            continue
        old_text = git("show", f"{merge_base}:{old_path}")
        new_text = open(full, encoding="utf-8").read()
        old_v, new_v = parse_version(old_text), parse_version(new_text)
        if old_v is None or new_v is None:
            continue
        if new_v < old_v:
            err(full, 1, f"version went backwards: {old_v[0]}.{old_v[1]} to {new_v[0]}.{new_v[1]}")
        old_d, new_d = decision_section(old_text), decision_section(new_text)
        if old_d and new_d and old_d != new_d and new_v[0] <= old_v[0]:
            err(full, 1, f"Decision section changed without a major version bump (still {new_v[0]}.{new_v[1]})")


def main():
    ap = argparse.ArgumentParser(description="Validate the design decisions repository.")
    ap.add_argument("--base", metavar="REF", help="git ref to compare changed decision files against")
    args = ap.parse_args()
    ids_seen = {}
    decision_paths = []
    md_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
        for f in filenames:
            if f.endswith(".md"):
                full = os.path.join(dirpath, f)
                md_files.append(full)
                if os.path.commonpath([full, DECISIONS_DIR]) == DECISIONS_DIR and f != "README.md":
                    decision_paths.append(os.path.relpath(full, ROOT))
    for path in sorted(md_files):
        check_file(path, ids_seen, decision_paths)
    check_index(sorted(decision_paths))
    check_territories()
    if args.base:
        check_version_bumps(args.base)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(md_files)} files checked, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
