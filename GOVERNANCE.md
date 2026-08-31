# Governance

## Who decides

Decision authority for this repository, and for all repositories of The Open Accounts Receivable Collective Foundation, rests with the Foundation: its Board of Directors and the delegates the Board designates. Community proposals, reviews, and discussion inform every decision. They do not themselves decide. This division is deliberate and is part of the Foundation's anti-capture design: no contributor, employer, or sponsor can buy or flood their way into the platform's architecture.

## Roles

- **Maintainers** review contributions, merge changes, convert community input into issues and decision updates, and recommend adoption or rejection to the Foundation. The founding maintainer is Rob Grafrath, the Foundation's Board Chair. Additional maintainers and a technical committee will be designated as the project grows.
- **Contributors** are everyone else who participates: through Discord, issues, interviews, or pull requests. No employer affiliation is required or disqualifying. Contributors with commercial interests in the AR industry are welcome; disclosed interest is preferred over disengaged distance.

## Decision lifecycle

1. **Proposed.** A proposal arrives as an issue or a pull request. A PR adding a decision file carries `status: Proposed` and a 0.x version in its front matter.
2. **Review.** Maintainers and the community review in public: consistency with [PRINCIPLES.md](PRINCIPLES.md), interaction with existing decisions, and domain accuracy.
3. **Adopted or rejected.** The Foundation adopts by merging with `status: Accepted` at version 1.0, or declines with a written reason on the PR or issue. When a rejection reveals a durable constraint, that constraint is added to the affected decision file's reasoning so it is visible to future contributors and their tools.
4. **Revised or superseded.** A refined answer to the same question is revised in place with a major version bump. A reversed answer or a reframed question arrives as a new decision file naming the old ID in `supersedes`, and the old file's status changes to Superseded. The maintainer makes the call when it is close. Prior versions remain in the Git history, which is never rewritten.

## The Wax bar

Per [SHARED-0001](decisions/shared/SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md), Wax is designed to stabilize early, and the cost of a change increases as it moves down the stack. Changes to `decisions/wax/` therefore face a deliberately higher review threshold than HiveAR domain or module decisions, and require explicit treatment of the invariants they touch. This is a property of the architecture, not a judgment about contributors.

## Related Foundation policies

The Foundation's Board-adopted policies govern this repository and all community spaces: the Open Source Policy (licensing, DCO, repository standards), the Antitrust Policy, the Trademark Policy, the Anti-Capture Policy, and the Community Programs and Standards Policy. Where this document and a Board-adopted policy differ, the policy controls. Policy texts are published at [openarcollective.org](https://openarcollective.org).
