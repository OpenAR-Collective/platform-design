---
id: SHARED-0007
title: "DevOps and Contribution Lifecycle"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 7: DevOps and Contribution Lifecycle

## Decision

The Foundation operates a unified DevOps and contribution lifecycle across the Wax framework, the HiveAR platform, and all module repositories under Foundation control. The lifecycle covers code contribution, continuous integration, testing, documentation, release packaging, distribution, issue tracking, security disclosure, and long-term support. Every Foundation-controlled software repository follows this lifecycle.

## Rationale

A unified lifecycle gives contributors a single mental model regardless of which repository they engage with, and it keeps operational overhead low for a resource-constrained Foundation. One set of templates, one continuous integration baseline, one release pattern, and one support model are cheaper to maintain than a patchwork that scales with the number of repositories.

This decision sits at the boundary of architecture and operational process. It is captured here for centralized reference rather than scattered across separate operational documents. It does not attempt to be a full specification: detailed specs for each subsystem will follow in their own documents as the development effort begins, anchored on the commitments made here.

## Repository Structure, Branching, and Versioning

The Wax framework, the HiveAR platform, and each delivered module are maintained in separate repositories under the Foundation's GitHub organization. Wax and HiveAR follow independent semantic version trains because they are distinct products with distinct stability profiles. The stability gradient established elsewhere in this document means Wax ossifies first and HiveAR follows. Independent version trains make this stability difference explicit and let each product release on its own cadence.

Branching follows the trunk-based pattern. Each repository has a single long-lived main branch that serves as the source of truth for the next release. Feature work happens on short-lived branches and merges back to main through pull request. When a release is cut, a release branch is created from the tagged commit (for example, release/v1.0). The release branch receives only backport patches; new feature work continues on main. This pattern avoids the integration ambiguity that arises from a permanent develop branch and keeps main as the canonical reference for AI-assisted development tools.

Versions follow semantic versioning. Major version bumps signal breaking changes or significant new architectural commitments, minor versions signal additive functionality, and patch versions signal bug and security fixes.

## Code Contribution Flow

External contributions follow the standard fork-and-pull-request model. Every commit must carry a Developer Certificate of Origin sign-off, consistent with the Foundation's licensing posture. Pull requests are reviewed against the architectural conventions defined throughout this document, including the naming conventions in [Wax Design Decision 5](../wax/WAX-0005-naming-conventions.md). The merge gate requires a passing continuous integration run, at least one maintainer approval, and resolution of any reviewer-requested changes. Direct commits to main by maintainers are permitted only for trivial fixes such as documentation typos or configuration files, and even those must still pass continuous integration.

## Continuous Integration and AI Tooling Baseline

GitHub Actions is the continuous integration platform. Each repository's pipeline includes, at minimum, a build stage, a test stage, and a lint stage. The lint stage incorporates the AI-powered naming linter defined in [Wax Design Decision 5](../wax/WAX-0005-naming-conventions.md).

AI tooling in the continuous integration pipeline follows a reusable pattern established by the naming linter: a prompt file containing the relevant context, a GitHub Actions workflow invoking GitHub Models via the actions/ai-inference action, and a verdict cache file where applicable. Future AI-assisted continuous integration tooling reuses this pattern rather than introducing alternative integrations. Specific applications discussed in this decision include documentation drift detection, training material generation, and test generation assistance.

## Testing Strategy

Each repository maintains unit, integration, and regression test suites. Unit tests cover individual components in isolation. Integration tests cover the interaction of components within a process boundary, including database interactions against a real PostgreSQL instance. Regression tests cover specific bugs after they are fixed to prevent recurrence.

Test coverage is an expectation for new contributions, with thresholds and exact mechanics deferred to the contribution policy specification. AI-assisted test generation is permitted and encouraged as a productivity aid, but the human contributor remains responsible for the correctness, scope, and quality of the tests committed. Generated tests are reviewed with the same scrutiny as hand-written tests.

## Documentation and Training Materials Lifecycle

Documentation lives in the repository alongside the code it describes, following the docs-as-code pattern. A documentation drift detection workflow, built on the AI tooling baseline, runs on pull requests and flags significant code changes that lack corresponding documentation updates. The reviewer remains the final judge of whether documentation changes are required for a given change.

Onboarding and training materials are generated by AI tooling from the current state of the codebase and documentation. The generated materials are published to the GitHub Wiki of the relevant repository on a periodic cadence rather than per-commit. The Foundation website links to the repository wikis as the canonical onboarding destination. If volume or formatting requirements grow beyond what GitHub Wiki supports comfortably, migration to a static documentation site (Docusaurus, MkDocs, or similar) is anticipated as future work.

## Release Packaging, Distribution, and Changelogs

Releases are distributed as pre-compiled installers covering the deployment paths identified in Wax Design Decision 6: Windows Server (MSI), Linux (deb and rpm), and Docker images for containerized deployments. Installer artifacts are published to GitHub Releases and mirrored on the Foundation website. Each artifact is accompanied by a published checksum. Signed artifacts and a supply chain attestation approach are deliverable goals that require dedicated operational attention as the release model matures, including signing key custody.

Each release ships with a changelog written in the Keep a Changelog format or a similar structured form. Changelogs are written by humans, with AI assistance permitted, rather than auto-generated. They are user-facing communication and require editorial judgment about what matters to operators upgrading the platform.

## Issue Tracking, Bug Reporting, and Security Disclosure

Each repository uses GitHub Issues for bug reports and feature requests, with templates that guide reporters through the information needed for triage. Discussions that are not yet actionable issues use GitHub Discussions where enabled.

Security vulnerabilities follow a separate disclosure path that does not route through public issues. Each repository carries a SECURITY.md file at the root explaining the disclosure procedure. The primary channel is GitHub Security Advisories, which provides private vulnerability reporting through the GitHub user interface. A monitored security email address provides an alternative channel for reporters who do not use GitHub. Publication of a PGP key on the Foundation website for sensitive reports is a deliverable goal.

The Foundation commits to acknowledging receipt of security reports within a defined service level, typically 72 hours. Initial triage is performed by the project founder. As the Foundation grows, a designated security reviewer or security committee assumes that role.

## Support and Backport Policy

Each major version on either version train carries a defined support window. The initial commitment is 24 months from the major version's release date, subject to refinement after the Foundation gains operational experience. The end-of-life date for each release line is published in advance, allowing operators to plan upgrades.

Within the support window, security fixes always backport to the release branch. Critical bug fixes (data loss, crashes, compliance breaks) backport per maintainer judgment within the window. Functional bug fixes and new features generally do not backport; users seeking those changes upgrade to a current release. After end of life, no further backports are made.

The operational cost of maintaining backports (cherry-pick conflict resolution, continuous integration runs on each release branch, coordinated multi-artifact releases, and security advisory authoring) is reduced but not eliminated by AI assistance. The 24-month support window length is calibrated to that cost and to operator upgrade tolerance.

## User Testing and Beta Participation

The Foundation does not operate any HiveAR instance on behalf of users; consequently, traditional in-product user testing is not available as a feedback mechanism. The Foundation relies instead on coordinated beta participation by partner agencies, who run pre-release builds in their own environments and provide structured feedback. The selection of beta partners, the cadence of beta releases, and the structure of feedback channels are operational details deferred to the contribution policy specification.

## Implementation Phasing

**Wax v1 (MVP):** Repository structure, trunk-based branching, semantic versioning, fork-and-pull-request contribution flow with Developer Certificate of Origin sign-off, code review and continuous-integration-pass merge gate, GitHub Actions pipeline, naming linter per [Wax Design Decision 5](../wax/WAX-0005-naming-conventions.md), unit and integration test suites, docs-as-code, GitHub Issues with templates, SECURITY.md, and a Windows MSI installer. Wax v1 is the proving ground for the lifecycle itself.

**Wax v2 and HiveAR v2:** Documentation drift detection workflow, AI-generated training materials published to the GitHub Wiki, regression test policy enforcement, Linux package installers (deb and rpm), Docker image distribution, GitHub Security Advisories integration, monitored security email channel, and structured changelog discipline. The support and backport policy becomes operationally meaningful once v1 releases exist to backport to.

**Wax v3+ and HiveAR v3+:** Signed installer pipeline, supply chain attestation, PGP key publication for security disclosures, formalized beta participation program, and a dedicated security reviewer role.

**Breaking change risk: LOW. Lifecycle elements with hard architectural dependencies (repository structure, branching model, version train independence) are committed up front. Operational elements (specific continuous integration workflows, beta program structure, support window length) can evolve without breaking anything material.**
