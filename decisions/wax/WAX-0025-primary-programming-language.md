---
id: WAX-0025
title: "Primary Programming Language"
status: Accepted
version: 1.1
area: wax
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 25: Primary Programming Language

## Decision

The Wax will be built in C# on the .NET runtime. C# is the primary language for the Wax engine, all modules, all API layers, and all server-side application code. The .NET runtime provides cross-platform support for Windows Server, Linux, and cloud infrastructure deployments, consistent with the agency-controlled deployment model adopted in [Wax Design Decision 6](WAX-0006-deployment-model.md).

## Rationale

The language selection was evaluated against four criteria: platform-agnostic deployment, performance, ecosystem maturity, and the realistic contributor community for an open-source project in the accounts receivable industry.

## Platform Agnosticism and Performance

Since .NET Core and through the current .NET runtime, C# applications compile and run identically on Windows Server, Linux, and major cloud platforms. Deployment requires no JVM, no separate runtime installer beyond the .NET runtime itself, and produces self-contained deployable packages consistent with the goals of [Wax Design Decision 6](WAX-0006-deployment-model.md). Performance benchmarks for .NET have been competitive with or superior to JVM performance in most enterprise workload categories since .NET 7.

## The Event Store

When this decision was adopted, its most significant technical factor was the Marten library, an open-source .NET library that implements event sourcing on PostgreSQL and whose design mapped closely onto the architecture of [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). Wax does not use Marten. Round 1 of the Foundation's engine bake-off found that Marten's append added database cost and showed an event store written directly on PostgreSQL passing every correctness gate, so Wax implements the event store itself, as Wax Design Decision 1 and [Wax Design Decision 3](WAX-0003-database-platform.md) describe. The [round 1 report](https://github.com/OpenAR-Collective/spikes/blob/main/engine-bakeoff/REPORT-ROUND-1.md) gives the measurements.

The event store is therefore no longer a reason to prefer C#. An event store written directly on PostgreSQL needs only a database driver, and the bake-off's Python side, adapted from the prototype that Andy Troiano published, wrote its own in the same way. The choice of C# rests on the grounds this decision gives elsewhere: platform agnosticism and performance, the contributor community, founder familiarity, and the availability of the libraries it needs under permissive licenses.

## Contributor Community

Wax's most likely contributors are developers who already build business software where money, audit trails, and regulation matter: financial services, healthcare billing, insurance, and accounts receivable itself. C# on .NET is a mainstream language for that kind of software, so a C# codebase lets those developers contribute in a language they already use. A project that asked them to learn a new language first would lose many of them before their first contribution.

Kotlin's developer community is primarily Android-focused. Java's enterprise base is large but skews toward large banking and payments infrastructure rather than the mid-market agency software space Wax is targeting. C# represents the most direct overlap with the skills of developers who work in and around the industry Wax serves.

## Founder Familiarity

The founding development team's primary expertise is in C#. During Year 1, when the platform's foundational architecture is being established, founder fluency in the primary language is a meaningful operational advantage. Architectural judgment is sharpest in familiar territory, and the quality of early decisions has outsized influence on the platform's long-term trajectory.

## Open Source Library Availability

The complete C# stack required for Wax is available under permissive open-source licenses with no cost for HiveAR's use case. The core libraries are ASP.NET Core under MIT, Npgsql (the PostgreSQL driver, on which Wax writes its event store) under MIT, FluentValidation under Apache 2.0, and xUnit for testing under Apache 2.0. No paid library components are required.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. C# on .NET LTS, with the event store of [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md) written directly on PostgreSQL through Npgsql. This is decided and does not phase.

**Breaking change risk: NONE.**

## Implications For Contributors

All Wax and module server-side code will be written in C# targeting the current .NET LTS release.

Contribution guidelines will specify the minimum supported .NET version and will be updated as new LTS releases are adopted.

Wax implements the event store abstraction interface itself, directly on PostgreSQL through Npgsql, as Wax Design Decision 1 describes. Contributors working on event handling and projection code work with that implementation and with SQL, and the contributor guides will document both.

Frontend technology is adopted in Shared Design Decision 4: Blazor WebAssembly. The C# backend choice and the Blazor frontend choice are complementary, enabling a single language across the full stack.
