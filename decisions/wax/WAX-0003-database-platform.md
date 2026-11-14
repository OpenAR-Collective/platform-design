---
id: WAX-0003
title: "Database Platform"
status: Accepted
version: 2.0
area: wax
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 3: Database Platform

## Decision

The Wax will use PostgreSQL as its primary relational database. This decision applies to the Wax event store, all entity tables, and all module-owned schema extensions. Application code reaches PostgreSQL with plain SQL through Npgsql, the PostgreSQL driver for .NET, inside a repository and query-object layer, and uses no object-relational mapper. The schema changes only through hand-written SQL migrations, applied in order.

## Rationale

The accounts receivable domain has a well-understood data model, and in the jurisdictions where agencies collect, collection and consumer protection law shapes what data must be captured, maintained, and auditable. That clarity is an asset, not a constraint. A fixed, enforced schema at the database level is a compliance feature, not a limitation to design around.

## PostgreSQL is the correct tool for this workload for several reasons:

**Relational integrity**: A debt links to contacts, payments, disputes, communications, assignments, and creditors. These relationships carry legal meaning. PostgreSQL enforces referential integrity natively. Leaving that enforcement to the application layer, as document databases require, introduces risk that contributors can inadvertently create orphaned or inconsistent records.

**Event store fit**: The enriched event sourcing architecture ([Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)) is a natural fit for PostgreSQL. An append-only events table with strong consistency guarantees, transactional writes, and rich query support is exactly what PostgreSQL does exceptionally well.

**Reporting and compliance queries**: Aging reports, collector productivity metrics, dispute tracking, and regulatory response deadline queries are join-heavy and aggregate-heavy by nature. PostgreSQL handles these elegantly without workarounds.

**Contributor accessibility**: PostgreSQL is among the most widely understood relational databases in the developer community. Contributors to an open-source project should not need to learn a specialized query model to participate.

**jsonb**: event payloads, read model extensions, and user-defined table data all require storing structured but variable-shape data alongside strictly typed relational columns. PostgreSQL's jsonb column type stores this data in a binary-decomposed format that supports full GIN indexing, key-existence queries, containment queries, and field extraction operators. A GIN index on core.event's prior_value and new_value columns enables queries like "find all events that touched the social_security_number field" or "find all debt.placed events where the placed balance exceeded 10,000 USD" without a full table scan, regardless of how many billions of rows the table holds. jsonb gives Wax the structured storage of a document store and the relational integrity and query power of a relational database, in a single column type, without any architectural compromise.

**Row-level security and SECURITY DEFINER functions**: PostgreSQL's native row-level security (RLS) policies enforce data access boundaries at the database layer rather than relying solely on application code. Combined with SECURITY DEFINER view and function definitions, this allows Wax to present decrypted PII to authorized roles transparently, enforce multi-tenant data isolation, and expose a safe read surface to BI tools and direct SQL users, all without bespoke application middleware. [Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md) describes the read layer architecture built on these capabilities.

**An event store with no library between it and PostgreSQL**: Wax implements the event store abstraction interface of [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md) itself, on the core.event table, with plain SQL through Npgsql, the PostgreSQL driver for .NET. PostgreSQL supplies everything that implementation needs: row locks that serialize the writes to one aggregate, a sequence and an insert trigger that number and time each event, transaction identifiers from which a reader finds its high-water mark, and SKIP LOCKED for readers that share the work. Round 1 of the Foundation's engine bake-off measured this implementation against the same workloads run through the Marten event store library. Marten's append function took 3.2 to 4.8 times as long as a plain insert into the same table in every measured pair of runs, and the implementation without Marten used less database CPU per command than the Marten side in nine of ten comparisons, as the [round 1 report](https://github.com/OpenAR-Collective/spikes/blob/main/engine-bakeoff/REPORT-ROUND-1.md) describes. Wax owns the code and its correctness in exchange, and the abstraction interface still lets the implementation change without changing the code that calls it.

**Enterprise operational maturity**: PostgreSQL carries decades of production deployment history across industries with data integrity requirements at least as demanding as debt collection. Logical replication, streaming replication, point-in-time recovery, tablespace management, connection pooling via pgBouncer, and automatic failover via Patroni are all well-understood, well-documented capabilities with large operational communities. The high availability and disaster recovery architecture for Wax deployments is built directly on these capabilities and is described in [Wax Design Decision 24](WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md).

## Why Not Mongodb

A document database such as MongoDB is often chosen for schema flexibility. That argument does not hold for HiveAR. The flexibility MongoDB offers is most valuable when the data model is unpredictable or rapidly changing. The debt collection domain is neither. The compliance obligations that define the data model have been stable for decades. Schema flexibility is not a feature HiveAR needs, and the tradeoffs it introduces (application-layer integrity enforcement, weaker transactional guarantees, more complex aggregate queries) are not tradeoffs HiveAR should accept.

## Application Data Access Pattern

Application code accesses PostgreSQL with plain SQL through Npgsql, organized using a repository and query-object discipline, on every path: commands, the event store, projections, and queries. Business logic, command handlers, projection workers, and query handlers receive typed objects from repositories and query objects rather than executing SQL themselves, and SQL is written only inside the data access layer.

This discipline serves two purposes. It keeps SQL, and the PostgreSQL-specific syntax and features it uses, confined to a single layer rather than scattered across the codebase. It allows database access to be mocked or stubbed cleanly for unit testing.

Wax uses no object-relational mapper. The command path locks the aggregate, checks its version, appends its events, and writes its state rows in one transaction and in as few round trips as possible, and an ORM's change tracking and generated statements add round trips and database work to that path. The Foundation tested this in October 2026 on the same C# command handlers, in the [EF Core mini-pass of the engine bake-off](https://github.com/OpenAR-Collective/spikes/blob/round-2/engine-bakeoff/README.md#the-ef-core-mini-pass). With EF Core, tuned with context pooling, compiled queries, a compiled model, and no change tracking where nothing was written, the handlers used 17 to 27 percent more database CPU and 97 to 128 percent more application CPU per command, and handled 17 to 23 percent fewer commands per second than with plain SQL, in each of the four configurations judged: the payment file, real time, and interest accrual at 8 workers, and the payment file with the engine paused. A single pair of runs on placing new debts, too few for a verdict, appeared to go the other way, because the engine under EF Core fell behind and left about a fifth of that run's work outside the measured window. For the event store interface established in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md), the data access layer is Wax's own implementation, written directly on PostgreSQL. An ORM may return for read-side queries only if a measured test shows that it earns its place. No read-side query has been measured, and the question is open in [OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md).

## Schema Migrations

The schema changes only through hand-written SQL migrations: ordered SQL files, each applied once and in order by a small runner that records which files have run. Every object the schema needs is written as SQL that a reviewer reads in the pull request, including the event store's triggers and sequence, the grants of the runtime role, and the names that [Wax Design Decision 5](WAX-0005-naming-conventions.md) requires. An ORM's generated migrations cannot express the triggers, functions, grants, roles, and views among those objects, so a schema they owned would still need raw SQL for everything that enforces the event store's invariants. Each component owns its own migration files, as [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md) provides for modules.

## PostgreSQL-Specific Features Are Embraced

PostgreSQL is the supported database, and its differentiated capabilities are treated as features to use, not features to avoid. This stance is articulated explicitly because the alternative position, designing the data layer to remain portable across multiple relational database engines, carries a permanent and recurring cost paid in every release rather than a one-time cost paid at a hypothetical migration moment. The cost of vendor portability is the loss of every PostgreSQL feature that other engines do not support or implement differently.

The Foundation's design embraces, among others, jsonb columns with GIN indexing for variable-shape payloads ([Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)), partial indexes for selective filters such as active-debt predicates, advisory locks for batch coordination, LISTEN and NOTIFY for real-time event distribution where applicable, row-level security policies and SECURITY DEFINER functions for the read layer ([Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md)), full-text search for note and communication content, range types where temporal or numeric range semantics apply, exclusion constraints, generated columns, and logical replication for reporting and analytics separation. Several of these capabilities map directly to AR domain problems and have no clean equivalent in lowest-common-denominator SQL.

A design that preserved portability would require the Foundation to forgo these capabilities, build application-layer substitutes for several of them, and continuously test against multiple database engines in CI. The maintenance burden is substantial and recurring. The migration scenario it preserves against, swapping PostgreSQL for a different engine in production, is one many architectures preserve against and few exercise: the literature is full of organizations that built portability layers and never used them. The Foundation declines this trade.

## Third-Party Database Provider Forks

A third party could fork the platform to run on SQL Server, MySQL, Oracle, or another engine. Such a fork would rewrite the data access layer, because its SQL is written for PostgreSQL. It would also need to replace or substitute every PostgreSQL-specific feature the platform uses, write a parallel set of migrations, supply equivalents for the read layer features that depend on PostgreSQL semantics, and maintain the fork against ongoing upstream changes. The Foundation neither commits to facilitating this work nor designs around it.

The articulation matters for a specific question that mid-market AR agencies running SQL Server-only infrastructure are likely to ask: can HiveAR run on SQL Server? The accurate answer is that the architecture does not forbid it but makes it a substantial project, because the event store, the read layer, and the data access layer all depend on PostgreSQL, and that the Foundation does not support, document, or design for that path. An object-relational mapper's provider model would not have made it much easier, since the platform depends on PostgreSQL-specific features that no provider translates. An organization with the engineering capacity and motivation to maintain such a fork could do so. The Foundation's mainline distribution targets PostgreSQL exclusively.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. PostgreSQL is the database, reached with plain SQL through a repository and query-object layer and changed by hand-written SQL migrations. No simplification needed.

**Wax v2:** An object-relational mapper for read-side queries, if the open question on it decides for one after a measured test.

Breaking change risk: NONE.

## Implications For Contributors

No code uses an object-relational mapper. Data access is plain SQL through Npgsql, written only inside repositories and query objects, and business logic never executes SQL itself.

Every schema change is a hand-written SQL migration file, reviewed as SQL. No migration is generated from code.
