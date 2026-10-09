---
id: WAX-0002
title: "CQRS Model"
status: Accepted
version: 1.1
area: wax
date: 2026-10-09
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 2: CQRS Model

## Decision

The Wax will implement simple CQRS: a strict separation of the command path (writes) from the query path (reads) within the same application and the same PostgreSQL database. Commands change state and produce events. Queries read from purpose-built read models and never change state. The two paths use separate code, separate data shapes, and separate handlers. No physically separate infrastructure is required.

> **WHAT CQRS MEANS**
>
> *Command Query Responsibility Segregation* (CQRS) is a pattern that divides the operations an application performs into two distinct categories: commands and queries. A command changes state. A query reads state. The two are never mixed: a command returns no data, and a query changes nothing. In Wax, every write enters the system as a named command (e.g., PostPayment, OpenDispute, CorrectPhone) handled by a dedicated command handler. The handler validates the command, applies business rules, writes an event to core.event, and updates the authoritative state table, all in a single atomic transaction. It returns only success or failure. Every read is served by a purpose-built read model. Read models are pre-aggregated tables optimized for specific query patterns: the collector queue view, the aging report, the account history display. They are never queried through the command path. They are updated asynchronously as domain events flow through the event stream. The two paths use separate code, separate data shapes, and separate handlers. Neither side knows about the other's implementation details. This separation keeps the write side focused on correctness and the read side focused on performance, without the operational overhead of physically separate databases or distributed event synchronization.

## Rationale

CQRS exists on a spectrum from simple code separation to fully distributed read and write systems. The complex end of the spectrum, with physically separate databases and event-driven synchronization, adds operational overhead that is not justified at HiveAR's scale and would significantly increase the barrier to deployment and contributor participation.

Simple CQRS delivers the primary benefits without that overhead. The write side is focused on correctness: validate the command, apply business rules, write the event, update the authoritative state table. The read side is focused on performance: serve pre-built read models optimized for specific query patterns. Neither side needs to know about the other's implementation details.

## The Write Side: Commands

Every state change enters the system as a command. A command is a named instruction carrying all data required to process it. Command handlers are single-responsibility classes: one handler per command type. The handler loads current state from the authoritative state table, validates the command against that state, produces one or more events, and writes the event and the updated state in a single atomic transaction. Commands return only success or failure, never data.

A batch job type designated as a bulk operation in [Wax Design Decision 24](WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md) is the one case where several commands share a transaction. Its worker processes a chunk of commands in one transaction, with the same handler logic and the same resulting events as the single-command path. Each command's events and state changes still commit together, because the whole chunk commits or rolls back as one.

> **WRITE SIDE FLOW**
>
> Client submits command via REST API. API layer validates inputs and authenticates the request. Command handler loads current state from ar.account (or relevant authoritative table). Business rules are applied. If invalid, the command is rejected with an error. One or more events are produced and written to core.event. The authoritative state table is updated in the same transaction. Read model projections receive the event asynchronously and update.

## The Read Side: Queries

Every read request is served by a query handler backed by a read model. Read models are pre-built tables in module-owned schemas, updated asynchronously as events flow through the event stream. Query handlers are simple: load the read model rows matching the query parameters and return them. No business logic, no state changes, no event writes.

The compliance audit query is the one case where a query reads the event store directly rather than a read model. This is intentional and appropriate: the audit history is the event store's native output, and there is no meaningful pre-aggregation to do. Every other query goes through a read model.

> **READ SIDE FLOW**
>
> Client submits query via REST API. API layer validates inputs and authenticates the request. Query handler reads from the appropriate read model table. Response is returned immediately. No event writes, no state changes. For audit history specifically: query handler reads from core.event filtered by aggregate.

## Read Model Consistency

Read models are updated asynchronously after events are committed. There is a brief window after a write where a read model may not yet reflect the latest event. For collections workflows this lag is typically imperceptible. The authoritative state table is available for any operation requiring guaranteed current state. UI design should handle the async nature gracefully, for example by showing a brief updating indicator after a write action that affects a displayed read model.

## Why Not Full CQRS

Full CQRS with physically separate read and write databases introduces eventual consistency across infrastructure boundaries, separate operational concerns for two database systems, more complex deployment requirements, and a higher contributor learning curve. None of the use cases Wax serves justify this complexity at launch. If usage patterns eventually reveal specific read workloads that cannot be satisfied by PostgreSQL read models, the architecture can evolve toward a separate read store for those specific cases. That decision can be made with real data rather than in advance.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. Simple CQRS within a single PostgreSQL database ships complete. Command handlers (one per command type, single-responsibility), read models (at least one per major screen), commands return success/failure only, queries never write. Read model projection updates can be synchronous in v1: projections update in the same transaction or immediately after the event write, eliminating eventual-consistency complexity without changing the external API contract.

**Wax v2:** Async projection updates via event stream subscription. Projection rebuild tooling (drop and replay from event store).

**Wax v3+:** Optional separate read database for reporting-heavy deployments.

**Breaking change risk: NONE.** The CQRS contract is a code-organization pattern, not a schema dependency.

## Implications For Contributors

Command handlers may not return query results. A command succeeds or fails. If the caller needs updated data after a command, it issues a separate query.

Query handlers may not write to any table or produce any event. A query that changes state is a violation of the CQRS contract.

Every new module capability is classified as either a command or a query before implementation begins. This classification determines which path it follows and which patterns apply.

Read models are owned by the module that needs them. No module may query another module's read model directly. If two modules need similar data shapes, each maintains its own read model.

The authoritative state tables in the core schema are the source of truth for command validation. Read models are for queries only and are never used to validate commands.
