---
id: WAX-0003
title: "Database Platform"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 3: Database Platform

## Decision

The Wax will use PostgreSQL as its primary relational database. This decision applies to the Wax event store, all entity tables, and all module-owned schema extensions.

## Rationale

The accounts receivable domain has a well-understood, legally defined data model. The FDCPA, FCRA, Regulation F, and state consumer protection statutes prescribe what data must be captured, maintained, and auditable. That clarity is an asset, not a constraint. A fixed, enforced schema at the database level is a compliance feature, not a limitation to design around.

## PostgreSQL is the correct tool for this workload for several reasons:

**Relational integrity**: An account links to contacts, payments, disputes, communications, assignments, and creditors. These relationships carry legal meaning. PostgreSQL enforces referential integrity natively. Leaving that enforcement to the application layer, as document databases require, introduces risk that contributors can inadvertently create orphaned or inconsistent records.

**Event store fit**: The enriched event sourcing architecture ([Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)) is a natural fit for PostgreSQL. An append-only events table with strong consistency guarantees, transactional writes, and rich query support is exactly what PostgreSQL does exceptionally well.

**Reporting and compliance queries**: Aging reports, collector productivity metrics, dispute tracking, and regulatory response deadline queries are join-heavy and aggregate-heavy by nature. PostgreSQL handles these elegantly without workarounds.

**Contributor accessibility**: PostgreSQL is among the most widely understood relational databases in the developer community. Contributors to an open-source project should not need to learn a specialized query model to participate.

**jsonb**: event payloads, read model extensions, and user-defined table data all require storing structured but variable-shape data alongside strictly typed relational columns. PostgreSQL's jsonb column type stores this data in a binary-decomposed format that supports full GIN indexing, key-existence queries, containment queries, and field extraction operators. A GIN index on core.event's prior_value and new_value columns enables queries like "find all events that touched the social_security_number field" or "find all account.placed events where the placed balance exceeded 10,000 USD" without a full table scan, regardless of how many billions of rows the table holds. jsonb gives Wax the structured storage of a document store and the relational integrity and query power of a relational database, in a single column type, without any architectural compromise.

**Row-level security and SECURITY DEFINER functions**: PostgreSQL's native row-level security (RLS) policies enforce data access boundaries at the database layer rather than relying solely on application code. Combined with SECURITY DEFINER view and function definitions, this allows Wax to present decrypted PII to authorized roles transparently, enforce multi-tenant data isolation, and expose a safe read surface to BI tools and direct SQL users, all without bespoke application middleware. [Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md) describes the read layer architecture built on these capabilities.

**Marten as the event store abstraction implementation**: Marten is a .NET library that implements a document store and event store directly on PostgreSQL. HiveAR's event store abstraction interface ([Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)) uses Marten as its backing implementation. Marten handles stream management, optimistic concurrency via expectedVersion, and projection registration against the PostgreSQL event table. Using Marten means Wax inherits a well-maintained, production-proven event sourcing implementation rather than building one from scratch, while the abstraction layer ensures the platform is not permanently coupled to any single library.

**Enterprise operational maturity**: PostgreSQL carries decades of production deployment history across industries with data integrity requirements at least as demanding as debt collection. Logical replication, streaming replication, point-in-time recovery, tablespace management, connection pooling via pgBouncer, and automatic failover via Patroni are all well-understood, well-documented capabilities with large operational communities. The high availability and disaster recovery architecture for Wax deployments is built directly on these capabilities and is described in [Wax Design Decision 24](WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md).

## Why Not Mongodb

Several newer entrants to the AR software market have selected MongoDB, typically citing schema flexibility as the primary advantage. That argument does not hold for HiveAR. The flexibility MongoDB offers is most valuable when the data model is unpredictable or rapidly changing. The debt collection domain is neither. The compliance obligations that define the data model have been stable for decades. Schema flexibility is not a feature HiveAR needs, and the tradeoffs it introduces (application-layer integrity enforcement, weaker transactional guarantees, more complex aggregate queries) are not tradeoffs HiveAR should accept.

## Application Data Access Pattern

Application code accesses PostgreSQL through Entity Framework Core (EF Core), organized using a repository and query-object discipline. Business logic, command handlers, projection workers, and query handlers receive typed objects from repositories and query objects rather than executing SQL themselves. Raw SQL is permitted only inside the data access layer and only where a justified PostgreSQL-specific feature is in use.

This discipline serves three independent purposes. It keeps PostgreSQL-specific syntax and feature use confined to a single layer rather than scattered across the codebase. It allows database access to be mocked or stubbed cleanly for unit testing. It establishes a clean seam at which a third party could substitute a different EF Core provider if they were willing to undertake that work, without requiring the Foundation to design around portability as a goal.

EF Core supplies the change tracking, migration generation, query translation, and connection management that this layer would otherwise need to build. The Foundation does not maintain a custom data access framework above EF Core. Marten supplies the equivalent layer for the event store interface as established in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). Repository and query-object code outside the event store path uses EF Core directly.

## PostgreSQL-Specific Features Are Embraced

PostgreSQL is the supported database, and its differentiated capabilities are treated as features to use, not features to avoid. This stance is articulated explicitly because the alternative position, designing the data layer to remain portable across multiple relational database engines, carries a permanent and recurring cost paid in every release rather than a one-time cost paid at a hypothetical migration moment. The cost of vendor portability is the loss of every PostgreSQL feature that other engines do not support or implement differently.

The Foundation's design embraces, among others, jsonb columns with GIN indexing for variable-shape payloads ([Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)), partial indexes for selective filters such as active-account predicates, advisory locks for batch coordination, LISTEN and NOTIFY for real-time event distribution where applicable, row-level security policies and SECURITY DEFINER functions for the read layer ([Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md)), full-text search for note and communication content, range types where temporal or numeric range semantics apply, exclusion constraints, generated columns, and logical replication for reporting and analytics separation. Several of these capabilities map directly to AR domain problems and have no clean equivalent in lowest-common-denominator SQL.

A design that preserved portability would require the Foundation to forgo these capabilities, build application-layer substitutes for several of them, and continuously test against multiple database engines in CI. The maintenance burden is substantial and recurring. The migration scenario it preserves against, swapping PostgreSQL for a different engine in production, is one many architectures preserve against and few exercise: the literature is full of organizations that built portability layers and never used them. The Foundation declines this trade.

## Third-Party Database Provider Forks

Because EF Core supports multiple providers natively, the data access seam in the Foundation's codebase does not prevent a third party from forking the platform and implementing a SQL Server, MySQL, Oracle, or other provider. Such a fork would need to replace or substitute every PostgreSQL-specific feature use in the codebase, write a parallel set of migrations, supply equivalents for the read layer features that depend on PostgreSQL semantics, and maintain its fork against ongoing upstream changes. The Foundation neither commits to facilitating this work nor designs around it.

The articulation matters for a specific question that mid-market AR agencies running SQL Server-only infrastructure are likely to ask: can HiveAR run on SQL Server? The accurate answer is that the architecture does not forbid it, that EF Core's provider model makes it technically feasible, and that the Foundation does not support, document, or design for that path. An organization with the engineering capacity and motivation to maintain such a fork could do so. The Foundation's mainline distribution targets PostgreSQL exclusively.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. PostgreSQL is the database. No simplification needed.

Breaking change risk: NONE.
