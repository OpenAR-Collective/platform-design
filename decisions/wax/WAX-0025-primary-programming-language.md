---
id: WAX-0025
title: "Primary Programming Language"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
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

## Architectural Fit: Marten on PostgreSQL

The most significant technical factor is the Marten library, an open-source .NET library that implements event sourcing and document storage natively on PostgreSQL. Marten's design maps almost exactly onto the architectural decisions already locked in for Wax:

Append-only event streams per aggregate, corresponding directly to [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md).

Built-in optimistic concurrency enforcement via expected version, implementing the invariant described in the event store abstraction layer.

An asynchronous projection daemon that maintains read models from the event stream, corresponding to the read model ownership pattern in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md).

PostgreSQL as the sole database, consistent with [Wax Design Decision 3](WAX-0003-database-platform.md).

Using Marten means the Collective is implementing the architecture it already designed rather than assembling equivalent capabilities from lower-level libraries. The event store abstraction interface defined in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md) wraps Marten, preserving the ability to replace the underlying implementation if the community later determines a different event store is warranted.

## Contributor Community

Research into actual developer skills in the accounts receivable and adjacent regulated industry software space confirms that the relevant contributor community skews toward C# and .NET rather than Java or Kotlin. The incumbent AR software platforms are built on proprietary legacy tooling, not mainstream JVM languages. The broader enterprise financial services, healthcare billing, insurance, and regulated industry software markets, which represent the most natural source of Wax contributors, show consistent C# and .NET representation in job postings and developer profiles.

Kotlin's developer community is primarily Android-focused. Java's enterprise base is large but skews toward large banking and payments infrastructure rather than the mid-market agency software space Wax is targeting. C# represents the most direct overlap with the skills of developers who work in and around the industry Wax serves.

## Founder Familiarity

The founding development team's primary expertise is in C#. During Year 1, when the platform's foundational architecture is being established, founder fluency in the primary language is a meaningful operational advantage. Architectural judgment is sharpest in familiar territory, and the quality of early decisions has outsized influence on the platform's long-term trajectory.

## Open Source Library Availability

The complete C# stack required for Wax is available under permissive open-source licenses with no cost for HiveAR's use case. The core libraries are ASP.NET Core under MIT, Marten under MIT, Npgsql (the PostgreSQL driver) under MIT, MediatR for CQRS under Apache 2.0, FluentValidation under Apache 2.0, and xUnit for testing under Apache 2.0. No paid library components are required.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. C# on .NET LTS. Marten for event store. This is decided and does not phase.

**Breaking change risk: NONE.**

## Implications For Contributors

All Wax and module server-side code will be written in C# targeting the current .NET LTS release.

Contribution guidelines will specify the minimum supported .NET version and will be updated as new LTS releases are adopted.

The Marten library is the implementation of the event store abstraction interface. Contributors working on event handling and projection code will need familiarity with Marten's API. Documentation and contributor guides will include Marten-specific onboarding material.

Frontend technology is adopted in Shared Design Decision 4: Blazor WebAssembly. The C# backend choice and the Blazor frontend choice are complementary, enabling a single language across the full stack.
