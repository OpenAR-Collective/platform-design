# Contributing

Thank you for helping design open infrastructure for the accounts receivable industry. This document covers every path from a five-minute observation to a full pull request. Read [START-HERE.md](START-HERE.md) first if you have not.

## The contribution we need most

Domain knowledge. The decisions in this repository describe how collections work; the people who can tell us where they are wrong are the people who run intake, work disputes, post payments, reconcile trust accounts, and answer regulator letters. That knowledge arrives as plain-language answers, not code, and it is credited: decisions shaped by a contribution carry a "Domain input from" line naming the contributor, with their permission.

## Four ways to contribute, easiest first

1. **Discord, for members.** Post an observation or answer in the #platform-design channel, and a maintainer converts it into an issue or a decision update. No GitHub account required. Discord access comes with free [Collective membership](https://join.openarcollective.org); invites are member-specific because onboarding sets real-name server nicknames and member permissions, so no public invite link exists. Members not yet on Discord can request a fresh invite by emailing membership@openarcollective.org.
2. **Issues.** Open a GitHub issue with one of the structured templates. "How we actually handle this" is the one for domain input; the others cover gaps, questions about a specific decision, and formal proposals. This requires a free GitHub account and nothing else.
3. **The web editor.** Click the pencil icon on any file in the GitHub interface, make your edit, and click "Propose changes." GitHub creates the fork, the branch, and the pull request for you. No terminal, no Git commands.
4. **Full pull request.** Clone, branch, edit, sign off, and open a PR. For contributors who work this way already.

## Decision file format

Every decision lives in one Markdown file under `decisions/`, named `ID-slug.md`. Front matter schema:

```yaml
---
id: HIVE-0010                # family prefix + four digits
title: "Short Decision Title"
status: Accepted             # Proposed | Accepted | Superseded | Rejected
area: hivear                 # shared | wax | hivear | module:<module-name>
version: 1.0                 # MAJOR.MINOR, see the version rules below
date: 2026-08-30             # date of the current version
supersedes: none             # a decision ID, or none
license: CC-BY-4.0
---
```

Rules:

- **IDs are permanent.** A new decision takes the next number in its family (SHARED, WAX, HIVE, or a module prefix of the form MOD-NAME, for example MOD-PURCHASE). IDs are never renumbered and never reused, even for rejected or superseded decisions. External references depend on this.
- **Every decision carries its own version** (`version: MAJOR.MINOR`). A proposal is 0.x; acceptance makes it 1.0. The major number changes when the `## Decision` section changes in substance. The minor number changes for substantive additions elsewhere in the file: reasoning, phasing, implications. Mechanical edits (link fixes, renames, typos) do not change the version, so the number tracks how settled a decision is rather than how often its file was touched. `date` is the date of the current version. Continuous integration fails a change to a `## Decision` section that does not raise the major number, and fails any version that goes backwards.
- **The repository has a version too, and decisions never move it.** Tags and [CHANGELOG.md](CHANGELOG.md) version the container: the front matter schema, the decision families, the validator, the templates. A new or revised decision is recorded in its own file and in the Git history, not in a repository version bump.
- **The onboarding process is editable like everything else.** The territory list lives in four files: START-HERE.md Step 3, the dropdowns in `.github/ISSUE_TEMPLATE/how-we-handle-this.yml` and `.github/ISSUE_TEMPLATE/report-a-gap.yml`, and the section headings in `skills/contributor-onboarding/references/probes.md`. Change all four in one pull request; the validator fails when they disagree. Feedback about the process goes through the "Improve the onboarding" issue form or a pull request against those files.
- **Every decision file has a `## Decision` section** stating the commitment in the first paragraph. Reasoning, alternatives considered, an Implementation Phasing section, and an Implications for Contributors section follow the pattern of the existing files.
- **Revising versus superseding.** Same question, refined answer: edit the file in place and raise the major version. Reversed answer or reframed question: a new decision file names the old ID in `supersedes`, and the old file's status changes to Superseded. The maintainer makes the call when it is close. Prior versions remain in the Git history, which is never rewritten.
- **Cross-references** use the decision's full name as link text, linking to the file by relative path, as the existing files do.
- **INDEX.md must stay in sync.** A PR adding or retitling a decision updates its line in [INDEX.md](INDEX.md).

## Writing standards

Continuous integration enforces these mechanically, so fixing them before pushing saves a round trip:

- No em dashes and no en dashes. Use commas, colons, semicolons, or restructured sentences.
- No sentences beginning with And, But, Or, So, Yet, or Nor.
- Straight quotes and apostrophes only. No arrows, bullets-as-characters, or other non-keyboard symbols.
- Oxford comma in lists of three or more.
- American English spelling.
- Future tense for planned work; present or past tense only for what exists or has happened.

## Sign-off (DCO)

Contributions are accepted under the Developer Certificate of Origin. Add a sign-off line to each commit, which `git commit -s` does automatically:

```
Signed-off-by: Your Name <you@example.com>
```

If you contributed through the web editor and forgot the sign-off, the Foundation's Open Source Policy allows a retroactive sign-off: post a comment on the pull request stating "I certify the contents of this contribution under the DCO, Signed-off-by: Your Name <you@example.com>" and a maintainer will proceed.

## Licensing

- **Prose in this repository** is contributed and published under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). By contributing, you agree your contribution is licensed the same way.
- **Code samples embedded in the prose** (interface sketches, SQL, schema fragments, C# snippets) are additionally available under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), matching the license the Wax and HiveAR codebases will carry, so that text can move between documentation and implementation without friction.
- Nothing in either license grants rights to the Foundation's names, logos, or other trademarks.

## AI-assisted contributions

Welcome, and expected: [START-HERE.md](START-HERE.md) is built for them. Two conditions. You are responsible for what you submit, which means reviewing AI-drafted text for accuracy before it goes in a PR, exactly as the Foundation's Open Source Policy requires for AI-assisted code. Second, claims about law or regulation (FDCPA, Regulation F, state licensing, and similar) must come from you or be flagged as needing verification; models assert regulatory requirements confidently and incorrectly.

## Guardrails

- **Antitrust.** Contributors come from competing companies. Describe operational mechanics; never share or solicit pricing, fee structures, contingency or commission rates, market or customer allocation, or statements about refusing to deal with particular parties. The Foundation's Antitrust Policy governs all community spaces, this repository included.
- **Confidentiality.** General practice only. No consumer data, no account-level detail, no client-identifying specifics, nothing covered by an agreement you have signed.
- **No legal advice.** Decision files describe what the platform records and supports. They are not legal or compliance advice, and contributions must not be framed as such.

## What happens to your contribution

A maintainer reads every submission. Domain input becomes an issue, feeds an open question, or updates a decision file, and you will be told which. Proposals and PRs get a review comment within a reasonable time; silence means backlog, not rejection, and a polite bump is welcome. Adoption authority rests with the Foundation, as [GOVERNANCE.md](GOVERNANCE.md) describes: community review informs every decision, and the Board or its designated delegates make it.

A note on the Wax decisions: the framework is deliberately stable and load-bearing, and [SHARED-0001](decisions/shared/SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md) commits to a high bar for changing it. Proposals touching `decisions/wax/` are welcome and should demonstrate command of the invariants they touch: name the decisions the proposal interacts with, state which properties (hash chain integrity, event immutability, schema ownership, module boundaries) it preserves, and argue the case. The HiveAR domain layer and [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) are where exploration is most wanted.
