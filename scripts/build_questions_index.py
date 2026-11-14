#!/usr/bin/env python3
"""Build the index of open design questions, and mark questions with answers.

The questions-index workflow runs this script with a token in GH_TOKEN or
GITHUB_TOKEN. It uses only the Python standard library.

  python3 scripts/build_questions_index.py build --out DIR
      Reads every open issue labeled open-question and writes three files
      into DIR: QUESTIONS.md, one line per question; questions/AREA.md, the
      same lines for each area label in .github/labels.yml; and
      questions.json, the same data for tools. The files hold no timestamps,
      so an unchanged set of questions gives identical files and the
      workflow commits nothing. A question whose comments hold an answer
      block but which lacks the has-answer label gains it.

  python3 scripts/build_questions_index.py mark-answer
      Reads the issue_comment event from the file that GITHUB_EVENT_PATH
      names. When a new comment on an open-question issue holds an answer
      block, the issue gains the has-answer label. Comment text is read here
      and nowhere else; no step of the workflow passes it to a shell.

An answer block is a comment containing "ANSWER to #", the first words of
the block that START-HERE.md asks an assistant to write.

For a test without the network, build --issues-json FILE reads the issues
from FILE, a JSON list of issue objects shaped as the GraphQL query below
returns them, and changes no labels.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS_PATH = os.path.join(ROOT, ".github", "labels.yml")
INDEX_BRANCH = "questions-index"
QUESTION_LABEL = "open-question"
HAS_ANSWER_LABEL = "has-answer"
ANSWER_MARK = "ANSWER to #"
LINE_FORMAT = "number | territory | who can answer | effort | topic | answers so far | related questions | title"

LABEL_LINE_RE = re.compile(r'^(- |  )(name|color|description): "([^"\\]*)"$')
RELATED_START_RE = re.compile(r"^(#{1,6}\s*Related questions\b|\*\*Related questions\b)", re.I)
SECTION_START_RE = re.compile(r"^(#{1,6}\s|\*\*[^*]+\*\*)")
ISSUE_REF_RE = re.compile(r"(?<![\w/&])#(\d+)\b")

QUERY = """
query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 50, after: $after, states: OPEN, labels: ["open-question"]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        body
        labels(first: 50) { nodes { name } }
        comments(first: 100) { totalCount nodes { body } }
      }
    }
  }
}
"""


def read_labels(path=LABELS_PATH):
    """The entries of .github/labels.yml in file order, as dicts."""
    labels = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            m = LABEL_LINE_RE.match(raw.rstrip("\n"))
            if not m:
                continue
            if m.group(1) == "- ":
                labels.append({})
            if labels:
                labels[-1][m.group(2)] = m.group(3)
    return labels


def api_token():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Set GH_TOKEN or GITHUB_TOKEN to a token that can read issues.")
    return token


def call(url, payload=None):
    """Send a request to the GitHub API and return the decoded JSON reply."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="GET" if data is None else "POST", headers={
        "Authorization": "Bearer " + api_token(),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "questions-index",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:1000]
        sys.exit(f"GitHub API request failed with HTTP {e.code}: {detail}")


def fetch_issues(repo):
    """Every open issue labeled open-question, as GraphQL issue objects."""
    owner, name = repo.split("/", 1)
    url = os.environ.get("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")
    nodes, after = [], None
    while True:
        reply = call(url, {"query": QUERY, "variables": {"owner": owner, "name": name, "after": after}})
        if reply.get("errors"):
            sys.exit("GitHub GraphQL query failed: " + json.dumps(reply["errors"])[:1000])
        page = reply["data"]["repository"]["issues"]
        nodes += [n for n in page["nodes"] if n]
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


def add_label(repo, number, label):
    base = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    call(f"{base}/repos/{repo}/issues/{number}/labels", {"labels": [label]})


def related_numbers(body, own):
    """The issue numbers listed in the body's related questions section.

    The section starts at a "Related questions" heading, as the issue form
    writes it, or at a bold "Related questions." lead-in, as the seeded
    questions write it, and ends at the next heading or bold lead-in.
    """
    found, inside = [], False
    for line in (body or "").splitlines():
        text = line.strip()
        if RELATED_START_RE.match(text):
            inside = True
            continue
        if inside and SECTION_START_RE.match(text):
            break
        if inside:
            for m in ISSUE_REF_RE.finditer(text):
                n = int(m.group(1))
                if n != own and n not in found:
                    found.append(n)
    return sorted(found)


def question(node, areas):
    """One index entry from a GraphQL issue object."""
    names = [l["name"] for l in node["labels"]["nodes"]]

    def facet(prefix):
        return sorted(n[len(prefix):] for n in names if n.startswith(prefix))

    slugs = [s for s in areas if "area:" + s in names]
    slugs += sorted(s for s in facet("area:") if s not in areas)
    comments = node["comments"]
    return {
        "number": node["number"],
        "title": " ".join(node["title"].split()),
        "areas": slugs,
        "territories": [areas.get(s, s) for s in slugs],
        "answer": facet("answer:"),
        "effort": facet("effort:"),
        "topics": facet("topic:"),
        "lob": facet("lob:"),
        "answers": sum(1 for c in comments["nodes"] if c and ANSWER_MARK in (c.get("body") or "")),
        "comments": comments["totalCount"],
        "related": related_numbers(node.get("body"), node["number"]),
        "labels": sorted(names),
    }


def line(q):
    answers = f"{q['answers']} answer" + ("" if q["answers"] == 1 else "s")
    related = ", ".join(f"#{n}" for n in q["related"]) or "none"
    return " | ".join([
        f"- #{q['number']}",
        "; ".join(q["territories"]) or "unlabeled",
        ", ".join(q["answer"]) or "unlabeled",
        ", ".join(q["effort"]) or "unlabeled",
        ", ".join("topic:" + t for t in q["topics"]) or "no topic",
        answers,
        "related " + related,
        q["title"],
    ])


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build(args):
    repo = args.repo
    areas = {}
    for label in read_labels():
        name = label.get("name", "")
        if name.startswith("area:"):
            areas[name[len("area:"):]] = label.get("description", name)
    if args.issues_json:
        with open(args.issues_json, encoding="utf-8") as fh:
            nodes = json.load(fh)
    else:
        nodes = fetch_issues(repo)
    questions = sorted((question(n, areas) for n in nodes), key=lambda q: q["number"])

    if not args.issues_json:
        for q in questions:
            if q["answers"] and HAS_ANSWER_LABEL not in q["labels"]:
                add_label(repo, q["number"], HAS_ANSWER_LABEL)
                q["labels"] = sorted(q["labels"] + [HAS_ANSWER_LABEL])
                print(f"Labeled #{q['number']} {HAS_ANSWER_LABEL}.")

    issue_url = f"https://github.com/{repo}/issues/N"
    raw_area = f"https://raw.githubusercontent.com/{repo}/{INDEX_BRANCH}/questions/AREA.md"
    area_rows, area_json = [], []
    for slug, territory in areas.items():
        count = sum(1 for q in questions if slug in q["areas"])
        area_rows.append(f"- {territory}: area:{slug}, {count} open, [questions/{slug}.md](questions/{slug}.md)")
        area_json.append({"label": "area:" + slug, "territory": territory, "file": f"questions/{slug}.md", "open": count})
    unsorted = sum(1 for q in questions if not any(s in areas for s in q["areas"]))
    if unsorted:
        area_rows.append(f"- Not yet in a territory: {unsorted} open, listed only in this file")

    out = args.out
    qdir = os.path.join(out, "questions")
    if os.path.isdir(qdir):
        for name in os.listdir(qdir):
            if name.endswith(".md"):
                os.remove(os.path.join(qdir, name))

    lines = [line(q) for q in questions]
    write(os.path.join(out, "QUESTIONS.md"), "\n".join([
        "# Open design questions",
        "",
        "This file lists every open issue labeled open-question, one line each. It is rebuilt automatically from the issues, so change an issue rather than this file. START-HERE.md on the main branch explains how to answer a question.",
        "",
        f"Each line reads: {LINE_FORMAT}. The issue for number N is {issue_url}.",
        "",
        "## Territories",
        "",
        f"Each territory's lines are also in a file of their own, short enough to paste: {raw_area}, where AREA is the area label without its area: prefix.",
        "",
        *area_rows,
        "",
        "## Questions",
        "",
        *(lines or ["There are no open design questions right now."]),
        "",
    ]))
    for slug, territory in areas.items():
        mine = [line(q) for q in questions if slug in q["areas"]]
        write(os.path.join(qdir, slug + ".md"), "\n".join([
            f"# Open design questions: {territory}",
            "",
            f"The open issues labeled open-question and area:{slug}, one line each, rebuilt automatically from the issues. Each line reads: {LINE_FORMAT}. The issue for number N is {issue_url}, and QUESTIONS.md on this branch lists every territory.",
            "",
            *(mine or ["No open design question carries this label right now."]),
            "",
        ]))
    write(os.path.join(out, "questions.json"), json.dumps({
        "repository": repo,
        "line_format": LINE_FORMAT,
        "areas": area_json,
        "questions": questions,
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote the index of {len(questions)} open design questions to {out}.")


def mark_answer(args):
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        sys.exit("GITHUB_EVENT_PATH is not set; mark-answer runs inside the workflow.")
    with open(path, encoding="utf-8") as fh:
        event = json.load(fh)
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    names = {l.get("name") for l in issue.get("labels") or []}
    if event.get("action") != "created" or not issue or issue.get("pull_request"):
        print("Not a new comment on an issue; nothing to do.")
    elif QUESTION_LABEL not in names:
        print(f"Issue #{issue['number']} is not labeled {QUESTION_LABEL}; nothing to do.")
    elif HAS_ANSWER_LABEL in names:
        print(f"Issue #{issue['number']} is already labeled {HAS_ANSWER_LABEL}.")
    elif ANSWER_MARK not in (comment.get("body") or ""):
        print(f"The new comment on #{issue['number']} holds no answer block.")
    else:
        add_label(args.repo, issue["number"], HAS_ANSWER_LABEL)
        print(f"Labeled #{issue['number']} {HAS_ANSWER_LABEL}.")


def main():
    ap = argparse.ArgumentParser(description="Build the design question index, or mark a question that has an answer.")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "OpenAR-Collective/platform-design"),
                    help="OWNER/NAME of the repository (default: GITHUB_REPOSITORY)")
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="write QUESTIONS.md, questions/AREA.md, and questions.json")
    b.add_argument("--out", required=True, help="folder to write the index into")
    b.add_argument("--issues-json", help="read issues from this file instead of the API, for testing")
    sub.add_parser("mark-answer", help="label the issue of a new answer comment has-answer")
    args = ap.parse_args()
    if args.command == "build":
        build(args)
    else:
        mark_answer(args)


if __name__ == "__main__":
    main()
