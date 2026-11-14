#!/usr/bin/env python3
"""Open design question issues from local Markdown drafts.

Usage:
  python3 scripts/seed_design_questions.py DRAFT... --map FILE
      (--precheck COMMAND | --skip-precheck) [--apply]
      [--repo OWNER/NAME] [--labels FILE] [--pause SECONDS]

Each DRAFT is a Markdown file, or a folder whose .md files are drafts. A
draft starts with front matter between two "---" lines holding at least a
title and labels, for example:

  ---
  title: "When an automatic payment fails, how often should it be retried?"
  labels: ["open-question", "area:payments", "effort:quick"]
  ---

Everything after the front matter is the issue body. A draft's id is the
id key in its front matter, or else its file name without .md. A body
links another draft with the token #{id}, and the script replaces each
token with that draft's issue number.

Without --apply the script changes nothing and reports what it would do.
With --apply it:
  1. creates or updates every label in .github/labels.yml, and never
     deletes one;
  2. opens one issue per draft that the map file does not already hold, in
     sorted order of draft id, replacing the tokens it already can, and
     records each new issue number in the map file at once;
  3. replaces every remaining token with the real issue number and edits
     each issue whose body changes.

The map file (--map) is a JSON object from draft id to issue number. A
rerun skips the drafts it holds, so an interrupted run can simply be
started again. The script stops before opening anything when a token names
no draft, when a draft uses a label that .github/labels.yml lacks, when a
draft's title matches an existing issue that the map does not hold, or
when the precheck command fails, and it exits with an error if any token
is left in an issue. It never prints an email address.

--precheck COMMAND is an optional command run against the drafts before
anything is created; it must exit 0. The draft paths are appended to the
command, a batch at a time. Give --skip-precheck to run without one.

Opening many issues at once starts many index rebuilds. To avoid that,
disable the questions index workflow while seeding and run it once after:
  gh workflow disable questions-index.yml
  python3 scripts/seed_design_questions.py ... --apply
  gh workflow enable questions-index.yml
  gh workflow run questions-index.yml

Requires the GitHub CLI (gh), signed in with permission to create labels
and issues, and only the Python standard library.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LABELS = os.path.join(ROOT, ".github", "labels.yml")
DEFAULT_REPO = "OpenAR-Collective/platform-design"
TOKEN_RE = re.compile(r"#\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
LABEL_LINE_RE = re.compile(r'^(- |  )(name|color|description): "([^"\\]*)"$')
ISSUE_URL_RE = re.compile(r"/issues/(\d+)\s*$")
PRECHECK_BATCH = 50


def say(text=""):
    """Print, with any email address replaced."""
    print(EMAIL_RE.sub("[email address]", str(text)), flush=True)


def stop(text):
    say("Stopped: " + text)
    sys.exit(1)


def read_labels(path):
    labels = []
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = LABEL_LINE_RE.match(line)
            if not m or (m.group(1) == "- ") != (m.group(2) == "name") or (m.group(1) == "  " and not labels):
                stop(f"{path}:{n} is not a label line; run scripts/validate.py")
            if m.group(1) == "- ":
                labels.append({})
            labels[-1][m.group(2)] = m.group(3)
    for label in labels:
        if set(label) != {"name", "color", "description"}:
            stop(f"label {label.get('name')!r} in {path} lacks a color or description")
    return labels


def front_value(raw, where):
    raw = raw.strip()
    if raw.startswith(("[", '"')):
        try:
            return json.loads(raw)
        except ValueError:
            stop(f"{where}: write the value as a double-quoted string or a list of them")
    return raw


def read_draft(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        stop(f"{path} has no front matter")
    meta, end = {}, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", lines[i])
        if m:
            meta[m.group(1)] = front_value(m.group(2), f"{path}, {m.group(1)}")
    if end is None:
        stop(f"{path}: the front matter never ends")
    title, labels = meta.get("title"), meta.get("labels")
    if not isinstance(title, str) or not title.strip():
        stop(f"{path} has no title")
    if not isinstance(labels, list) or not labels or not all(isinstance(x, str) for x in labels):
        stop(f"{path} needs labels, as a list of quoted names")
    draft_id = str(meta.get("id") or os.path.splitext(os.path.basename(path))[0])
    body = "\n".join(lines[end + 1:]).strip("\n") + "\n"
    return {"id": draft_id, "path": path, "title": title.strip(), "labels": labels, "body": body}


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, n) for n in sorted(os.listdir(p)) if n.endswith(".md")]
        elif os.path.isfile(p) and p.endswith(".md"):
            files.append(p)
        else:
            stop(f"{p} is not a Markdown draft or a folder of them")
    if not files:
        stop("no drafts found")
    return files


def split_command(command):
    if os.name != "nt":
        return shlex.split(command)
    parts = shlex.split(command, posix=False)
    return [p[1:-1] if len(p) > 1 and p[0] == p[-1] == '"' else p for p in parts]


def run_precheck(command, files):
    argv = split_command(command)
    if not argv:
        stop("the precheck command is empty")
    for start in range(0, len(files), PRECHECK_BATCH):
        try:
            result = subprocess.run(argv + files[start:start + PRECHECK_BATCH], capture_output=True,
                                    text=True, encoding="utf-8", errors="replace")
        except OSError as e:
            stop(f"could not run the precheck command: {e}")
        for text in (result.stdout + result.stderr).splitlines():
            say("  " + text)
        if result.returncode != 0:
            stop(f"the precheck command exited with {result.returncode}; nothing was created")
    say("The precheck command passed.")


def gh(*args, required=True):
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        if required:
            stop(f"could not run gh, the GitHub CLI: {e}")
        return subprocess.CompletedProcess(args, 127, "", f"could not run gh, the GitHub CLI: {e}")
    if required and result.returncode != 0:
        stop(f"gh {args[0]} {args[1]} failed: {result.stderr.strip()}")
    return result


def gh_with_body(body, *args):
    """Run gh with the body in a temporary file passed as --body-file."""
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        return gh(*args, "--body-file", path)
    finally:
        os.remove(path)


def resolve(body, numbers):
    return TOKEN_RE.sub(lambda m: f"#{numbers[m.group(1)]}" if m.group(1) in numbers else m.group(0), body)


def load_map(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not all(isinstance(v, int) for v in data.values()):
        stop(f"{path} is not a map from draft id to issue number")
    return data


def save_map(path, numbers):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(dict(sorted(numbers.items())), fh, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


def sync_labels(repo, labels, apply):
    result = gh("label", "list", "--repo", repo, "--limit", "1000", "--json", "name,color,description",
                required=apply)
    if result.returncode != 0:
        say("Could not read the repository's labels, so the label plan is unknown: " + result.stderr.strip())
        return
    current = {l["name"].lower(): l for l in json.loads(result.stdout)}
    unchanged = 0
    for label in labels:
        have = current.get(label["name"].lower())
        if have is None:
            say(f"{'Creating' if apply else 'Would create'} label {label['name']}.")
            if apply:
                gh("label", "create", label["name"], "--repo", repo,
                   "--color", label["color"], "--description", label["description"])
        elif have["color"].lower() != label["color"].lower() or (have.get("description") or "") != label["description"]:
            say(f"{'Updating' if apply else 'Would update'} label {label['name']}.")
            if apply:
                gh("label", "edit", have["name"], "--repo", repo,
                   "--color", label["color"], "--description", label["description"])
        else:
            unchanged += 1
    say(f"{unchanged} labels already match .github/labels.yml.")


def check_titles(repo, drafts, numbers, apply):
    """Stop when a draft not in the map has the title of an existing issue."""
    result = gh("issue", "list", "--repo", repo, "--state", "all", "--limit", "5000", "--json", "number,title",
                required=apply)
    if result.returncode != 0:
        say("Could not list the existing issues, so titles were not compared: " + result.stderr.strip())
        return
    existing = {i["title"].strip(): i["number"] for i in json.loads(result.stdout)}
    for d in drafts:
        if d["id"] not in numbers and d["title"] in existing:
            stop(f"draft {d['id']} has the title of issue #{existing[d['title']]}, which the map does not hold. "
                 f'If that issue came from this draft, add "{d["id"]}": {existing[d["title"]]} to the map; '
                 "otherwise change the title")


def main():
    ap = argparse.ArgumentParser(description="Open design question issues from Markdown drafts. "
                                 "Without --apply, nothing is changed.")
    ap.add_argument("drafts", nargs="+", help="draft files, or folders of them")
    ap.add_argument("--map", required=True, help="JSON file from draft id to issue number, read and kept up to date")
    ap.add_argument("--precheck", metavar="COMMAND",
                    help="an optional command run against the drafts before anything is created; it must exit 0")
    ap.add_argument("--skip-precheck", action="store_true", help="run without a precheck command")
    ap.add_argument("--apply", action="store_true", help="create the labels and issues; without it, only report")
    ap.add_argument("--repo", default=DEFAULT_REPO, help=f"OWNER/NAME (default {DEFAULT_REPO})")
    ap.add_argument("--labels", default=DEFAULT_LABELS, help="the label file (default .github/labels.yml)")
    ap.add_argument("--pause", type=float, default=8.0,
                    help="seconds to wait after each issue is opened or edited (default 8), to stay under "
                         "GitHub's limits on creating content")
    args = ap.parse_args()
    if bool(args.precheck) == args.skip_precheck:
        ap.error("give --precheck COMMAND, or --skip-precheck to run without one")

    say("Applying changes." if args.apply else "Dry run: nothing will change. Add --apply to act.")
    labels = read_labels(args.labels)
    label_names = {l["name"] for l in labels}
    files = collect(args.drafts)
    drafts = sorted((read_draft(f) for f in files), key=lambda d: d["id"])
    numbers = load_map(args.map)

    ids = {d["id"] for d in drafts}
    if len(ids) < len(drafts):
        stop("two drafts share an id")
    if len({d["title"] for d in drafts}) < len(drafts):
        stop("two drafts share a title")
    for d in drafts:
        unknown = [x for x in d["labels"] if x not in label_names]
        if unknown:
            stop(f"{d['id']} uses labels that .github/labels.yml lacks: {', '.join(unknown)}")
        missing = sorted({t for t in TOKEN_RE.findall(d["body"]) if t not in ids and t not in numbers})
        if missing:
            stop(f"{d['id']} links drafts that do not exist: {', '.join(missing)}")
    if args.precheck:
        run_precheck(args.precheck, [d["path"] for d in drafts])

    sync_labels(args.repo, labels, args.apply)
    check_titles(args.repo, drafts, numbers, args.apply)

    todo = [d for d in drafts if d["id"] not in numbers]
    say(f"{len(drafts)} drafts: {len(drafts) - len(todo)} already opened, {len(todo)} to open.")
    for d in todo:
        if not args.apply:
            say(f"Would open {d['id']}: {d['title']}")
            continue
        out = gh_with_body(resolve(d["body"], numbers), "issue", "create", "--repo", args.repo,
                           "--title", d["title"], *[a for x in d["labels"] for a in ("--label", x)]).stdout.strip()
        m = ISSUE_URL_RE.search(out)
        if not m:
            stop(f"could not read the new issue number for {d['id']} from gh")
        numbers[d["id"]] = int(m.group(1))
        save_map(args.map, numbers)
        say(f"Opened #{numbers[d['id']]} for {d['id']}: {d['title']}")
        time.sleep(args.pause)

    linked = [d for d in drafts if TOKEN_RE.search(d["body"])]
    if not args.apply:
        say(f"Would fill in the links of the {len(linked)} drafts that link others, once every issue has a number.")
        say("Every link between drafts names a draft, so none would be left unreplaced.")
        return
    # Fill the tokens into each issue's current body rather than rewriting it
    # from the draft, so that a rerun never undoes a later edit to an issue.
    for d in linked:
        number = numbers[d["id"]]
        current = json.loads(gh("issue", "view", str(number), "--repo", args.repo, "--json", "body").stdout)["body"]
        body = resolve(current, numbers)
        left = sorted(set(TOKEN_RE.findall(body)))
        if left:
            stop(f"#{number} ({d['id']}) links drafts with no issue: {', '.join(left)}")
        if body == current:
            continue
        gh_with_body(body, "issue", "edit", str(number), "--repo", args.repo)
        say(f"Filled in the links of #{number} ({d['id']}).")
        time.sleep(args.pause)
    say(f"Done. {len(drafts)} design questions are open, and every link between them is filled in.")


if __name__ == "__main__":
    main()
