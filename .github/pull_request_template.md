<!-- Thank you. The checklist below is what review looks for; completing it honestly is the fastest path to a merge. Domain input without a file change is welcome too: the "How we actually handle this" issue template is the lighter path. -->

## What this changes and why

<!-- The problem, the change, and the real-world consequence it serves. -->

## Interacting decisions

<!-- Every decision ID this touches, contradicts, or depends on. If it contradicts an adopted decision, say so explicitly and argue the case. Write "none" only if you have checked INDEX.md. -->

## If this touches decisions/wax/

<!-- Wax is deliberately stable and load-bearing. Name the invariants this touches (hash chain integrity, event immutability, schema ownership, module boundaries) and why each survives. Delete this section for HiveAR, shared, and module changes. -->

## Version bumps

<!-- For each decision file changed: none, minor, or major, and why. Major is required when the Decision section changes in substance; CI checks that one. Mechanical edits take none. -->

## Checklist

- [ ] I read the decisions neighboring this change, not just the file I edited.
- [ ] New or retitled decisions have a matching line in INDEX.md, and front matter follows CONTRIBUTING.md.
- [ ] `python3 scripts/validate.py --base main` passes locally, or I am relying on CI to tell me.
- [ ] No pricing, rates, market or customer allocation, consumer data, or client-confidential information.
- [ ] Claims about law or regulation are flagged for verification, not asserted.
- [ ] Commits are signed off (DCO). If I forgot, I will post the retroactive sign-off comment per CONTRIBUTING.md.
- [ ] I license this contribution under CC BY 4.0 (prose) and Apache 2.0 (embedded code samples).
