---
id: WAX-0001
title: "Enriched Event Sourcing"
status: Accepted
version: 1.2
area: wax
date: 2026-10-09
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 1: Enriched Event Sourcing

## Decision

The Wax will use enriched event sourcing as its primary audit and persistence strategy. Every state change to a domain entity (accounts, contacts, payments, disputes, assignments, and all other core objects) will be recorded as a discrete, immutable event in a single append-only event store. Each event carries both the prior state and the new state of the changed fields, along with the actor, timestamp, reason code, and source of the change.

The event store is the permanent record of truth. Authoritative state tables are maintained transactionally alongside the event store to serve as the current-state representation for command processing and queries. Read models owned by individual modules serve all user-facing query workloads.

> **WHAT THIS MEANS IN PRACTICE**
>
> An event is a record of something that happened, not a diff or a mutation log. Events are immutable once written. Nothing in the system ever updates or deletes an event. There is one events table for the entire platform. All aggregate types write to core.event. Authoritative state tables (e.g., ar.account) are always current and always consistent with the event store, written in the same transaction. Read models are pre-built query tables owned by modules, updated asynchronously from the event stream. All user-facing queries hit read models, never the event store directly. The event store is the recovery mechanism. If an authoritative state table is ever in doubt, it can be rebuilt by replaying the full event history.

## Why Enriched Rather Than Pure

Pure event sourcing stores only what happened and requires replay to determine the prior state. While theoretically clean, this creates friction for the most common compliance use case: producing a readable audit trail. Regulators, courts, and internal compliance teams need to answer the question of what changed, from what value to what value, by whom, and why, without requiring an engineering exercise to reconstruct the answer.

Enriched event sourcing stores both prior and current values directly in the event payload. The common audit query is answered by a simple read against the event store. Prior state is also fully derivable through replay for any recovery or forensic use case.

## The Single Events Table

There is one events table in the entire platform: core.event. Every event from every aggregate type is written to this table. The aggregate_type and aggregate_pk_ref columns identify what the event belongs to. This design has several advantages: one place to subscribe to the event stream, one table to back up, one write target for all command handlers, and projections can listen to the full stream or filter to the aggregate types they care about.

There is no per-entity events table. A contact.phone_corrected event and a payment.posted event both live in core.event, distinguished by their aggregate_type value.

## Authoritative State Tables

Each aggregate-backed entity type has an authoritative state table in the core schema (e.g., ar.account, ar.payment, ar.entity). These tables always reflect the current state of their entities and are written in the same database transaction as the event that caused the state change. The atomicity of this write is a critical invariant: the event and the state update either both succeed or both fail. They are never written independently.

Authoritative state tables serve two purposes. First, they provide a fast, always-current starting point for command handlers that need to load an aggregate before processing a command. Second, they provide a transactionally consistent current-state reference that does not depend on the asynchronous propagation lag inherent in read models.

Authoritative state tables are not a replacement for the event store. They are a materialized view of it. If there is ever any reason to doubt the accuracy of an authoritative state table, whether from a bug, a failed migration, or any other cause, the table can be rebuilt by replaying the full event history from core.event. The event store is always the ground truth.

## Read Models

All user-facing query workloads are served by read models: pre-built tables optimized for specific query patterns. A read model is owned by the module that needs it and lives in that module's schema. Wax does not own read models.

Read models are updated asynchronously as events flow through the event stream. A collector queue view, an aging report, a supervisor dashboard, and a compliance summary are all read models, each maintained by the module responsible for that capability. Running any of these queries is a single fast read against a pre-aggregated table, not a calculation at request time.

Because read models are updated asynchronously, there is a brief window after a write where a read model may not yet reflect the latest event. For a collections workflow, this lag is typically imperceptible, and the authoritative state table is available for any operation that requires a guaranteed current state. The UI should be designed to handle the async nature of read model updates gracefully, for example, by showing a brief updating indicator after a write action.

## The Event Store Abstraction Layer

The rest of the application never communicates directly with PostgreSQL for event store operations. All event store interactions pass through a defined C# interface. PostgreSQL is one implementation of that interface. This abstraction means the underlying event store technology can be changed in the future without modifying any application code outside the implementation layer.

## The interface defines a focused set of operations:

append(streamId, expectedVersion, events): writes one or more events to a stream. The expectedVersion parameter enforces optimistic concurrency: if another process has already written to this stream since the caller last read it, the append is rejected and the command is retried. This prevents conflicting concurrent writes.

loadStream(streamId, fromVersion): returns events for a given aggregate from a specified version onward. Command handlers use this after loading the authoritative state table to pick up any events written since the state was last persisted.

subscribe(streamId, fromVersion, handler): registers a projection or read model to receive events as they are written. This is the mechanism that keeps read models current without polling.

## JSON Payload Model

Every event payload in core.event uses a uniform JSON model. The prior_value and new_value columns are always a jsonb keyed object: each key is a field name and each value is the field's value at the time of the event. There are no scalar payloads, no bare strings, and no arrays at the top level. Every event, from a single-field correction to a fifty-field account placement, uses the same structure.

A single-field phone correction writes { "primary_phone": "8175550001" } as prior_value and { "primary_phone": "8175550002" } as new_value. A multi-field account placement carries all changed fields as keys in the same object. There is no field_name column and no distinction between single-field and compound events. The event type name communicates what happened. The payload keys communicate which fields were affected.

Monetary values in a payload are typed quantities, an amount and a currency code together, as defined in [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md).

This uniform structure has several consequences that apply throughout the platform: queries into the payload use PostgreSQL's jsonb operators consistently, PII encryption envelopes are applied at the field key level rather than wrapping the entire payload, and contributors writing new event types make no decisions about which shape to use.

**PostgreSQL jsonb queries. **PostgreSQL provides full index support for jsonb columns. A GIN index on prior_value and new_value enables key-existence queries and containment queries without full table scans. Key-existence queries use the ? operator: WHERE new_value ? 'social_security_number'. Containment queries use the @> operator: WHERE new_value @> '{"status": "active"}'. Field value extraction uses the ->> operator: SELECT new_value ->> 'primary_phone' FROM core.event WHERE event_type = 'contact.phone_corrected'. These are first-class PostgreSQL capabilities, not workarounds.

**PII encryption envelope. **When a field is PII-classified, its value in prior_value or new_value is not stored as plaintext. The Wax Security Module (WSM, defined in [Wax Design Decision 15](WAX-0015-security-module.md)) serialization layer replaces the plaintext value with a structured encryption envelope at the field key level: { "social_security_number": { "_enc": true, "alg": "AES-256-GCM", "kid": "a3f8c2d1-...", "ct": "base64ciphertext==" } }. Non-PII fields in the same payload object remain as bare values. A reader encountering a field value checks for the _enc key. If present, the reader calls the WSM with the kid to request decryption. If the subject's key has been destroyed, the WSM returns a typed inaccessible indicator rather than plaintext.

> **ENCRYPTION ENVELOPE FIELDS**
>
> **_enc**: boolean, always true. Signals that this field value is an encryption envelope rather than a plaintext value.
>
> **alg**: the encryption algorithm used (e.g., AES-256-GCM). Stored with the ciphertext so the decryption path is self-describing and algorithm selection can evolve without rewriting historical records.
>
> **kid**: the key identifier. A UUID referencing the subject's encryption key in the WSM key store. This is the link between the encrypted payload and the key management lifecycle.
>
> **ct**: the base64-encoded ciphertext, including the authentication tag for authenticated encryption modes.

## Sequence Numbers

Two distinct sequence numbers are stored in every core.event row. They serve different purposes and must not be conflated.

**aggregate_sequence_number **is a per-aggregate ordinal that starts at 1 for the first event written for a given aggregate_pk_ref and increments by one for each subsequent event on that aggregate. It is the stored representation of the expectedVersion parameter in the event store abstraction interface's append call. When a command handler loads an aggregate and prepares to write an event, it passes the last known aggregate_sequence_number as expectedVersion. If another process wrote to that aggregate concurrently, the sequence will not match and the append is rejected, enforcing optimistic concurrency without a full table lock. The aggregate_sequence_number also defines the ordering within a per-aggregate hash chain: prior_event_hash at sequence N references the event_hash of the event at sequence N-1 for the same aggregate. No gaps are expected within a healthy chain; a gap is evidence of data loss or tampering.

**global_sequence_number **is assigned by a single PostgreSQL SEQUENCE object (core.event_global_sequence_seq) and is monotonically increasing across the entire table, regardless of aggregate. It establishes a total ordering of all writes to the event store: projections and other readers follow the stream by it, and it serves as the window anchor for delta checkpoint hashing in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). It is an ordering and has no integrity role. It is not part of an event's hashed content, and it is gap-tolerant by design: a transaction that acquires a sequence value and then rolls back leaves a gap, and nothing in the platform assumes a contiguous range. The UUID event_pk remains the surrogate primary key and deduplication mechanism. The two sequence numbers provide the per-aggregate and global orderings that a UUID cannot.

A sequence value is drawn when a row is inserted, not when its transaction commits, so an event with a lower global_sequence_number can become visible after an event with a higher one. A reader that follows the whole stream therefore reads only up to the high-water mark: the highest number at or below which every transaction that drew a value has either committed or rolled back. A reader that moved past an event still in flight would never see it. The same mark ends each checkpoint window in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). A long-running write transaction holds the mark back for every reader until it finishes, which is one reason write transactions are kept short.

## Hash Fields

Two hash columns are declared in core.event. Their purpose and chain mechanics are defined fully in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). They are declared here because they are core schema columns that must be present from the first row written.

**prior_event_hash **stores the event_hash of the immediately preceding event for the same aggregate, in aggregate_sequence_number order. It is null for aggregate_sequence_number = 1. Its presence binds each event to its predecessor, forming the per-aggregate hash chain.

**event_hash **stores the SHA-256 hash of this event's full payload, including prior_event_hash and excluding global_sequence_number, computed by the WSM before the row is committed. It is stored as a hex string: human-readable in diagnostic queries, portable into verification reports, and compatible with standard tooling. The WSM owns this computation. Application code cannot write an event that bypasses it. The hash is computed over the encrypted ciphertext of PII fields, not the plaintext, ensuring the chain remains verifiable after key destruction.

## Standard Event Payload Schema

Every event written to core.event will conform to the following schema. Module-specific events may extend this schema with additional fields but may not omit required fields.

| **Field** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| event_pk | uuid | Yes | Surrogate primary key for this event row. Used for deduplication and as a foreign reference target. |
| global_sequence_number | bigint | Yes | Monotonically increasing integer assigned by a PostgreSQL sequence at insert time. Establishes total ordering across all aggregates. Readers follow the stream by it up to the high-water mark, and it is the window anchor for delta checkpoint hashing. Not part of the hashed content. Gap-tolerant: rolled-back transactions leave gaps, which is expected behavior. See [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). |
| aggregate_sequence_number | integer | Yes | Per-aggregate ordinal (1, 2, 3...) for a given aggregate_pk_ref. Resets independently per aggregate. Resolves the expectedVersion parameter in the event store abstraction interface, enforcing optimistic concurrency. Defines ordering within an aggregate's hash chain. No gaps are expected within a healthy chain. |
| event_type | text | Yes | Namespaced event type identifier (e.g., contact.phone_corrected, account.placed). The namespace identifies the owning module or Core. |
| schema_version | smallint | Yes | Revision of this event type's payload schema. Event-type-specific; starts at 1 and increments only on breaking changes. Included in the hash input. Semantics defined in [Wax Design Decision 26](WAX-0026-event-schema-versioning.md). |
| aggregate_pk_ref | uuid | Yes | Primary key of the aggregate root this event belongs to. Polymorphic: resolved via aggregate_type. Not a traditional foreign key. See the aggregate callout in this decision. |
| aggregate_type | text | Yes | Discriminator for aggregate_pk_ref. Identifies the aggregate root type (e.g., account, entity, payment, payment_arrangement). |
| occurred_at | timestamptz | Yes | The instant at which the fact happened, as asserted by the actor or the source, stored in UTC. It equals recorded_at unless the command asserts an earlier instant, as when a fact is entered late, for example a payment received by mail and keyed days afterward. |
| recorded_at | timestamptz | Yes | The instant the store wrote the row, stored in UTC. Assigned by the store and never supplied by a caller. |
| actor_pk_ref | uuid | Yes | Primary key of the user or system process that caused the event. Polymorphic: resolved via actor_type. Not a traditional foreign key. |
| actor_type | text | Yes | Discriminator for actor_pk_ref. Values: user, system, integration, batch. |
| prior_value | jsonb | Conditional | Keyed JSON object representing field values before this event. Each key is a field name; each value is the prior field value, or an encryption envelope if PII-classified. Null for creation events. Never a bare scalar. |
| new_value | jsonb | Conditional | Keyed JSON object representing field values after this event. Same structure as prior_value. PII-classified fields carry an encryption envelope. |
| reason_code_fk | uuid | Recommended | Foreign key to core.reference_value. Identifies why the change occurred. See [Wax Design Decision 20](WAX-0020-reason-code-registry.md). |
| source | text | Recommended | Origin of the change (e.g., debtor_request, ncoa, collector_ui, batch_import). |
| correlation_pk_ref | uuid | No | Links related events produced by a single logical operation to a shared source record. Polymorphic: resolved via correlation_type. Not a database-level foreign key. Known values: workflow_execution, batch_job_run, api_request, manual. |
| correlation_type | text | Conditional | Discriminator for correlation_pk_ref. Required when correlation_pk_ref is set. Known values: workflow_execution, batch_job_run, api_request, manual. Follows the same polymorphic pair pattern as aggregate_type and actor_type. |
| metadata | jsonb | No | Module-specific extension data not appropriate for the standard payload. |
| prior_event_hash | text | Conditional | The event_hash of the immediately preceding event for this aggregate, in aggregate_sequence_number order. Null for aggregate_sequence_number = 1. Forms the cryptographic link in the per-aggregate hash chain. See [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). |
| event_hash | text | Yes | SHA-256 hash of this event's full payload including prior_event_hash and excluding global_sequence_number, computed by the WSM before the row is committed. Stored as a hex string. Application code cannot write an event that bypasses this computation. See [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). |

> **POLYMORPHIC REFERENCE FIELDS**
>
> aggregate_pk_ref and actor_pk_ref do not follow the standard _fk naming convention because they are polymorphic: each can reference the primary key of multiple different tables depending on the value of its discriminator column (aggregate_type and actor_type respectively). This is a documented exception to the naming convention, not a violation. The _pk_ref suffix signals that the field holds a primary key value from another table but that the target table varies at runtime. Standard _fk fields in all other tables reference a single, fixed target table and follow the convention without exception. correlation_pk_ref joins aggregate_pk_ref and actor_pk_ref as a third documented polymorphic field, paired with its own discriminator correlation_type. The _pk_ref suffix applies for the same reason: the target table varies at runtime depending on the correlation_type value.

## Event Time and Business Dates

Two instants describe every event. occurred_at is the moment the fact happened, as asserted by whoever is recording it, and recorded_at is the moment the store wrote the row. They differ whenever a fact is entered late, and the gap between them is evidence in its own right: both are part of the hashed content, and recorded_at is assigned by the store and never supplied by a caller, so a backdated event shows both the time it asserts and the time it was actually recorded, and neither can be altered without breaking the chain.

Many facts in collections matter by the day, not by the moment, and the day that matters is often neither envelope instant: the day a death occurred, the day the collector received a notice, the day a fact takes effect, the day an effect ends. An event type whose consequences depend on calendar days carries those days as explicit civil-date fields in its own payload schema, and does not rely on occurred_at or recorded_at to stand in for them, as defined in [Wax Design Decision 12](WAX-0012-date-time-timezone-and-freeform-note-language.md). Where an event type records the day a notice or document was received, the day a fact took effect, or the day an effect ends, it names those fields received_date, effective_date, and end_date, so that rules, restrictions, and clocks defined in packs can refer to them uniformly. Which of these dates governs a given rule is rule content and belongs in packs.

## Illustrative Example: Full Write Cycle

The following example walks through a payment being posted, showing every layer of the architecture in sequence.

> **SCENARIO**: Collector posts a 500.00 USD payment on account-123
>
> 1. Collector submits Post Payment 500.00 USD command via the API.
> 2. Command handler loads ar.account where account_pk = account-123. Current balance: 1,500.00 USD. Account is active. Command is valid.
> 3. PaymentPosted event is written to core.event (see payload below).
> 4. ar.account.current_balance is updated to 1,000.00 USD in the same transaction. Steps 3 and 4 succeed or fail together. They are never split.
> 5. Event is published to subscribers asynchronously.
> 6. workflow module projection updates collector_queue_read_model: new balance, last payment date, next action recalculated.
> 7. reporting module projection updates aging_read_model: balance recalculated in the appropriate aging bucket.
>
> EVENT PAYLOAD written to core.event:
>
> ```
> event_pk: "9f3a1b2c-..."
> global_sequence_number: 1042871
> aggregate_sequence_number: 47
> event_type: "payment.posted"
> aggregate_pk_ref: "account-123"
> aggregate_type: "account"
> occurred_at: "2026-03-30T14:22:01.318402Z"
> actor_pk_ref: "user-0042"
> actor_type: "user"
> recorded_at: "2026-03-30T14:22:01.318402Z"
> prior_value: { "current_balance": { "amount": "1500.00", "currency": "USD" } }
> new_value: { "current_balance": { "amount": "1000.00", "currency": "USD" } }
> reason_code_fk: "uuid-of-payment-received-ref-value"
> source: "collector_ui"
> correlation_pk_ref: null  (no workflow triggered this command)
> correlation_type: null
> metadata: null
> prior_event_hash: "a3f9c2d1e5b7..."
> event_hash: "f1e2d3c4b5a6..."
> ```

## Illustrative Example: Audit Query

When a compliance officer opens the account history view, the API queries core.event where aggregate_pk_ref = account-123, ordered by aggregate_sequence_number. Every change ever made to the account is returned, in sequence, self-describing. No reconstruction is required. The prior and new values for every field change are directly readable in the event record.

This is the audit trail a regulator, plaintiff's attorney, or internal compliance team would see in a dispute. It is complete, immutable, and requires no engineering effort to produce.

## Schema Overview

The following illustrates how the layers of the architecture relate to each other across schemas:

| **Schema** | **Table / Object** | **Purpose** |
| --- | --- | --- |
| core | core.event | Single append-only event store for all aggregate types |
| core | ar.account | Authoritative current state for accounts |
| core | ar.entity | Authoritative current state for entities (persons and businesses) |
| core | ar.payment | Authoritative current state for payments |
| workflow | workflow.collector_queue_read_model | Read model for collector queue view, owned by workflow module |
| reporting | reporting.aging_read_model | Read model for aging reports, owned by reporting module |
| healthcare | healthcare.account_extension | Satellite table extending ar.account for healthcare module |

> **AGGREGATES, AGGREGATE ROOTS, AND EVENT ATTRIBUTION**
>
> **What an aggregate is.** The term aggregate comes from Domain-Driven Design and means something specific that the word "table" does not capture. A table is a storage concept: a place where rows live. An aggregate is a behavioral concept: a named domain object with its own lifecycle, its own business rules, and a designated root entity through which all commands and state changes flow. The root entity's primary key is the identity of the entire aggregate. External references always point to the root, never to members.
>
> **What an aggregate root is.** The aggregate root is the single entry point for all commands directed at the aggregate. Nothing outside the aggregate reaches inside it to mutate a member directly. A command is issued to the root, the root enforces its business rules, and an event is written. This is what makes the event stream for a given aggregate a coherent and complete history: every change passed through the same gate.
>
> **The boundary test.** An object warrants its own aggregate root if it has business rules it enforces independently, and if it can change in ways that do not require another aggregate to be locked or loaded at the same time. Two aggregates may reference each other by primary key. Neither owns the other. The clearest signal that an object needs its own aggregate root is when its lifecycle inherently spans more than one other aggregate from start to finish: not just at initiation, but throughout.
>
> **Cross-aggregate events and fan-out.** Some domain operations inherently affect more than one aggregate. A split payment is received from an entity and applied across multiple accounts. A payment arrangement covers a payer-designated subset of the entity's accounts. A letter is sent to a person and covers some or all of their accounts. In these cases, the operation itself is its own aggregate with its own lifecycle. The cross-aggregate effect is handled by fan-out: one event on the originating aggregate, followed by a corresponding event on each affected aggregate, all linked by the originating aggregate's primary key. No single event claims more than one aggregate root.
>
> **Initiation versus lifecycle.** Not every operation that touches multiple accounts at once belongs to its own aggregate. A person may initiate a dispute against several accounts simultaneously. However, once initiated, each account's dispute follows a fully independent path: separate investigations, separate credit bureau responses, separate resolutions, potentially separate outcomes. The cross-account nature is a workflow concern at initiation, not a shared lifecycle concern. The command handler fires independent commands at each account aggregate. Each account's dispute.opened event may carry a reference to the initiating batch for traceability, but no dispute aggregate governs their shared lifecycle because no such shared lifecycle exists. When an operation's cross-aggregate span ends at initiation, it belongs to the member objects of each affected aggregate, not to a root of its own.
>
> **Known Wax aggregate roots.** The following aggregate types are established for Wax. The list will grow as modules are specified.
>
> **entity:** A person or business. Owns demographic history, address and phone history, contact outcome tracking, and the demographic scoring model. An entity can be updated independently of any account.
>
> **account:** A placed debt. Owns balance, status, dispute lifecycle, assignment history, and payment split application records. The account knows which entities are associated with it and in what capacity (primary debtor, co-signer, guarantor, and similar roles).
>
> **account_set:** A named grouping of accounts. Owns membership rules, lock state during legal proceedings, and aggregate lifecycle flags derived from member composition.
>
> **payment:** A payment received from an entity. Owns the full payment lifecycle: receipt, split calculation by the configured methodology, application of splits to target accounts, and reversal. A split payment is not owned by any single account. It is its own aggregate, and each target account receives a corresponding fan-out event recording the split applied to it.
>
> **payment_arrangement:** A payment arrangement made by an entity covering one or more payer-designated accounts. Owns the full arrangement lifecycle: proposal, acceptance, modification, fulfillment, and breach. The payer's designation of which accounts are covered is a core term of the arrangement, not a workflow detail, and the arrangement governs all covered accounts throughout its lifecycle. Each covered account and the arranging entity receive corresponding fan-out events.
>
> **communication:** An outbound communication: a letter, a notice, or a contact attempt. Owns the communication lifecycle: generation, queuing, delivery, and outcome. Both the addressed entity and any covered accounts receive corresponding fan-out events. The communication aggregate type is provisional; the communications module specification may define more granular types if letter and contact attempt lifecycles diverge sufficiently to warrant it.
>
> **client:** A creditor client. Owns placement history, billing terms, and client configuration.
>
> **legal_case:** A legal proceeding. Defined by the legal module. Owns case lifecycle, account and set associations, and filing and judgment history.
>
> **workflow_definition:** A configured workflow. A configuration aggregate with its own versioned lifecycle.
>
> **user:** A staff member or system actor. Owns credential and role assignment history.
>
> **Member objects are not aggregate roots.** Disputes, assignments, address history records, and phone history records are members of their parent aggregate. They do not have their own aggregate roots. Events that describe changes to these objects are attributed to the parent aggregate root, with the member object's identity carried in the event payload. A dispute.opened event has aggregate_type = 'account' and aggregate_pk_ref pointing to the account. The fact that a person may initiate disputes against multiple accounts simultaneously does not make dispute its own aggregate: each dispute follows a fully independent lifecycle from initiation onward and is governed entirely by its own account. The dispute is not a separate aggregate.

## Compliance Rationale

The FDCPA, FCRA, Regulation F, and state consumer protection statutes impose specific record-keeping obligations on collection agencies. The enriched event sourcing model satisfies these obligations structurally rather than procedurally. Compliance is not dependent on staff following a documented procedure; it is a property of the system itself. Every change to every account is recorded automatically, immutably, and with full context.

A regulator or auditor who questions whether an account's current state is accurate can be shown the complete event history that produced it, event by event. The current state can be mathematically derived from that history on demand. There is no ambiguity and no trust-us involved. This architecture directly supports the Collective's compliance-first design principle. It is not an optional feature; it is the foundation the platform is built on.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. The event store is foundational and non-negotiable. Ship the complete enriched event sourcing architecture: single core.event table, full standard payload schema, prior and new values on all state-change events (keyed JSON objects), atomic event + authoritative state table writes, event store abstraction layer (Marten), aggregate_sequence_number for optimistic concurrency, global_sequence_number for stream ordering, correlation_pk_ref for linking related events. Hash chain columns (event_hash, prior_event_hash) are present in the schema but may be populated with placeholder values; chain computation activates in v2. PII encryption envelopes are deferred; PII is stored as plaintext JSON in v1. This is acceptable for early adopters on their own infrastructure but must be documented as a known limitation.

**Wax v2:** Hash chain computation activated with backfill utility for v1 data. PII encryption envelope and Wax Security Module (WSM) integration. Event store partitioning strategy (by time range) for large installations.

**Wax v3+:** Cross-installation event federation. Event archival and cold storage policies.

**Breaking change risk: LOW.** The full schema ships in v1. All enhancements are additive.

## Implications For Contributors

Every state change must be expressed as a command that produces one or more events. Direct mutation of authoritative state tables outside the event pipeline is not permitted.

Events must conform to the standard payload schema. Module-specific events may extend the schema but may not override required fields.

Prior and new values must be included in all events where state changed. Both prior_value and new_value must be keyed JSON objects. Omitting prior_value on a state-change event is a schema violation. Bare scalar values in either column are not permitted.

The event write and the authoritative state table update must always occur in the same database transaction. Writing one without the other is a critical invariant violation.

Reason codes must be drawn from the published Reason Code Registry. If a required code does not exist, a registry extension proposal should be submitted before the module is merged.

Read models are owned by the module that needs them. A module requiring a specific query shape defines and maintains its own projection in its own schema.

No module may query core.event directly for user-facing workloads. All user-facing queries must go through read models.

occurred_at is asserted by the actor or the source and may precede recorded_at. recorded_at is assigned by the store and is never supplied by a caller.

An event type whose consequences depend on calendar days carries those days as civil-date payload fields and does not use occurred_at or recorded_at as a substitute.

No monetary value appears in a payload as a bare number.
