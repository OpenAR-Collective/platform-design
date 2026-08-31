# Wax and HiveAR: Architecture Design Decisions

This repository is the authoritative record of architectural decisions for **Wax** and **HiveAR**, free and open-source software published by The Open Accounts Receivable Collective Foundation (The OpenAR Collective). Every decision, its reasoning, and its implications for contributors are public here, one file per decision.

**Wax** is a free, open-source event sourcing application framework. It provides the event store, CQRS command and query pipeline, module system, workflow automation engine, internationalization infrastructure, and the Wax Security Module integration boundary. Wax is domain-agnostic: it contains no accounts receivable logic and is designed to serve as the structural foundation for multiple domain applications over time.

**HiveAR** is a free, open-source accounts receivable and collections platform built on Wax. It is designed for deployment by collection agencies of any size and serves as neutral, community-governed infrastructure for an industry that has historically lacked it. HiveAR is designed to run under the agency's control: installed on the agency's own infrastructure, or hosted by a vendor of the agency's choosing. The Collective does not operate HiveAR on behalf of agencies, does not hold agency data, and does not have access to agency operational systems.

The naming draws from the bee and hive brand language: Wax is the building material of the comb, the structural foundation everything else is built from. HiveAR is the hive where the AR work happens. Modules are cells in the comb.

## Status

The platform is in design. This repository records what has been decided (52 decisions so far), what remains open ([OPEN-QUESTIONS.md](OPEN-QUESTIONS.md)), and the principles that govern both ([PRINCIPLES.md](PRINCIPLES.md)). Decisions carry `status: Accepted`, meaning they are the Foundation's current commitment; while Wax and HiveAR are pre-1.0, decisions remain open to revision through the process in [GOVERNANCE.md](GOVERNANCE.md), and community review is the point of publishing them. Wax is designed to stabilize early and change rarely; HiveAR is the active frontier where input matters most right now.

Decision history is the Git history; releases are tagged and summarized in [CHANGELOG.md](CHANGELOG.md).

## Explore

- **[INDEX.md](INDEX.md)**: every decision on one line. Start here, or point your AI assistant here.
- **Reading order for newcomers:** [SHARED-0001](decisions/shared/SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md), then Wax Design Decisions 1 through 9, which cover the repository architecture, the event sourcing model, the CQRS pattern, the database platform, and the naming conventions everything else references.
- **[PRINCIPLES.md](PRINCIPLES.md)**: the six principles every decision answers to.

## Contribute

You do not need to write code, and you do not need to understand event sourcing. The most valuable contributions are answers to questions about how collections actually work, from the people who do it.

1. Go to **[START-HERE.md](START-HERE.md)**, or point your AI assistant at it and say "walk me through this."
2. Ask how the platform handles something you deal with every day.
3. If the answer is wrong, incomplete, or missing, tell us: in a [GitHub issue](https://github.com/OpenAR-Collective/platform-design/issues/new/choose), or in the [#platform-design channel](https://discord.com/channels/1497335210658762964/1543762760993603675) if you are on the Collective's Discord. [Membership](https://join.openarcollective.org) is free and includes Discord access.

[CONTRIBUTING.md](CONTRIBUTING.md) covers the file format and the pull request path. [GOVERNANCE.md](GOVERNANCE.md) covers who decides and how.

## Licensing

Prose in this repository is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0): share it, adapt it, and build on it, with attribution to The Open Accounts Receivable Collective Foundation. Code samples embedded in the prose are additionally available under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), matching the license the Wax and HiveAR codebases will carry. See [LICENSE](LICENSE) for the CC BY 4.0 text and [LICENSE-CODE](LICENSE-CODE) for the Apache 2.0 text.

Neither license grants rights to the Foundation's trademarks. Wax™, HiveAR™, The OpenAR Collective™, and the Foundation's logos are trademarks of The Open Accounts Receivable Collective Foundation, and their use is governed by the Foundation's Trademark Policy.

## About the Foundation

The Open Accounts Receivable Collective Foundation is a Delaware nonprofit whose mission is to provide the accounts receivable and debt collection industry with free, open-source software, open compliance and educational resources, and a vendor-neutral peer community, governed to prevent industry capture. Learn more at [openarcollective.org](https://openarcollective.org).
