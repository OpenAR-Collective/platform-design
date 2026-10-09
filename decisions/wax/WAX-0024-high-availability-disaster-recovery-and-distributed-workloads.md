---
id: WAX-0024
title: "High Availability, Disaster Recovery, and Distributed Workloads"
status: Accepted
version: 2.0
area: wax
date: 2026-10-09
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 24: High Availability, Disaster Recovery, and Distributed Workloads

## Decision

Wax's application tier is stateless, enabling horizontal scaling and instance-level failover without coordination. The WSM is stateless per operation and scales horizontally alongside the application tier, with same-aggregate write serialization enforced by PostgreSQL row locks rather than inter-process coordination. Distributed workloads including API request handling, workflow evaluation, scheduled event firing, batch job execution, and job scheduling are coordinated through PostgreSQL's SELECT FOR UPDATE SKIP LOCKED mechanism, eliminating the need for an external message queue in Year 1. Batch jobs are parallelized using a chunk-based work claiming model that distributes processing across multiple instances and threads. A batch job type designated as a bulk operation writes each chunk in a single transaction with set-based statements, and every event it writes is hashed, chained, and shaped exactly as the single-command path would write it. PostgreSQL HA/DR is provided through streaming replication and Patroni-managed automatic failover, documented by reference to the projects' own guides rather than reimplemented. The Collective defines the architectural requirements and supported patterns. Infrastructure provisioning, backup schedules, and RTO/RPO targets are agency responsibilities.

## Stateless Application Tier

The HiveAR application process carries no local state. Every request is self-contained: the information needed to handle it arrives with the request or is retrieved from the database. No session data, no in-memory aggregate state, and no local file system dependencies are maintained between requests. This is a structural consequence of the API-first architecture from Decision 4 and the event sourcing read model pattern from Decision 1.

Statelessness means any number of HiveAR application instances can run simultaneously behind a load balancer. Any instance can serve any request. If an instance fails, in-flight requests are lost and the client retries against a surviving instance. No session migration or state handoff is required. Adding instances increases capacity linearly. Removing instances requires no coordination.

## WSM Horizontal Scaling

The WSM is stateless per operation. It holds no in-memory state between calls. Key material is stored in PostgreSQL's WSM-exclusive key store table and is retrieved on demand. Multiple WSM instances can run simultaneously, handling concurrent cryptographic operations against different aggregates with no inter-instance coordination. A load balancer routes WSM calls from application instances to available WSM instances in the same way it routes HTTP requests to application instances.

Key retrieval strategy is fresh-from-store per operation for correctness, with an optional short-lived per-request cache acceptable for performance tuning. The key store is the authoritative source. A key destruction event writes to the key store table, which all WSM instances see on their next retrieval. No cache invalidation broadcast is needed because the TTL of any in-request cache is shorter than any plausible key destruction race.

Write serialization for the hash chain is not the WSM's concern. The command handler acquires a SELECT FOR UPDATE lock on the aggregate's authoritative state row before invoking the WSM for hash computation. The database enforces that only one command handler writes to a given aggregate at a time. Multiple WSM instances computing hashes for different aggregates simultaneously is safe because their chains are independent. The WSM does not need to know whether another instance is also computing a hash; the database serializes the writes.

## Distributed Workload Coordination via SKIP LOCKED

The majority of Wax's distributed workload coordination is handled by PostgreSQL's SELECT FOR UPDATE SKIP LOCKED. This mechanism allows multiple workers to claim units of work from a shared queue table without collision: a worker claims rows by locking them, other workers querying the same table skip already-locked rows and claim different ones. No external message queue, no distributed mutex, and no inter-process communication is required.

> **WORKLOAD TYPES AND THEIR COORDINATION MECHANISM**
>
> API request handling: fully stateless. Any instance handles any request. Load balancer distributes requests. No coordination required. Command handler execution: acquires SELECT FOR UPDATE on the aggregate's authoritative state row before writing. Serializes same-aggregate concurrent writes. Different aggregates write concurrently with no conflict. Event projection workers: read from core.event and write to read model tables. Different projections run on different instances concurrently. Projections are idempotent: a duplicate run produces the same result, so occasional double-processing on failover is safe. Workflow engine evaluation: when an event fires, it is written to core.event and simultaneously written to a pending_workflow_evaluation outbox table. Worker instances claim rows from the outbox using SKIP LOCKED. Each event is processed by exactly one worker. A worker that fails mid-evaluation releases its lock after a configurable timeout, allowing another worker to reclaim and retry. Scheduled event firing: due entries are claimed from the Pending Event Register ([Wax Design Decision 27](WAX-0027-pending-event-register.md)) using SKIP LOCKED. Only one worker fires each scheduled event. A rolled-back or failed claim releases automatically. Job scheduler: the job scheduler table is polled using SKIP LOCKED. One instance claims each scheduled job. The claiming instance becomes the coordinator for that job run. WSM operations: stateless per operation. Multiple instances handle concurrent requests with no coordination beyond the per-aggregate write lock described above.

## Batch Job Parallelism and Chunk-Based Claiming

Batch workflows iterate over potentially millions of rows and must be parallelizable across multiple instances and multiple threads within each instance. Running a batch job single-threaded on a single instance is not acceptable for large agencies. The chunk-based claiming model distributes batch work without requiring external coordination.

When a batch job is triggered, the first instance to claim it from the job scheduler table becomes the coordinator for that run. The coordinator divides the target row set into fixed-size chunks and writes each chunk as a row in a batch_job_chunk table, recording the chunk's primary key range or page bounds, its status (pending, claimed, complete, cancelled), and a claim expiry timestamp. The coordinator then immediately begins processing chunks itself like any other worker.

Worker instances, which may be multiple threads on multiple machines, claim chunks from batch_job_chunk using SELECT FOR UPDATE SKIP LOCKED. Each worker processes its claimed chunk independently, either through the normal command handler path one command at a time or, for a batch job type designated as a bulk operation, in one transaction as described under Bulk Chunk Writes. Processing a chunk produces events in core.event subject to the same per-aggregate row lock serialization as all other writes. Two workers processing different aggregates within the same chunk window write concurrently without conflict. Two workers attempting the same aggregate block on the row lock, with one waiting and the other completing first.

> **BATCH JOB CHUNK TABLE SCHEMA**
>
> **batch_job_run_fk**: the batch job run this chunk belongs to.
>
> **chunk_sequence_number**: ordering within the run, for progress display.
>
> **range_start and range_end**: the primary key bounds or page offset defining which rows this chunk covers.
>
> **status**: pending, claimed, in_progress, complete, failed, or cancelled.
>
> **claimed_by_instance**: the application instance identifier that claimed this chunk.
>
> **claimed_at**: UTC timestamp of the claim.
>
> **claim_expires_at**: UTC timestamp after which an incomplete claim is considered abandoned and may be reclaimed by another worker.
>
> **completed_at**: UTC timestamp of successful completion.
>
> **error_detail**: failure information if the chunk failed, for retry decision-making.

Chunk size is configurable per batch job definition. Smaller chunks reduce the blast radius of a worker failure (less work to redo) at the cost of more claiming overhead. Larger chunks reduce claiming overhead at the cost of longer recovery windows. Agencies configure chunk size based on the nature of the batch operation and their infrastructure characteristics.

Progress visibility is provided naturally by the batch_job_chunk table: completed chunks divided by total chunks gives a real-time completion percentage available to any admin dashboard query without additional infrastructure.

Cancellation marks all unclaimed chunks as cancelled. Workers holding claimed chunks complete or time out naturally. A cancelled job's already-completed chunks remain committed to the event store. Cancellation stops forward progress but does not roll back completed work. Compensating workflows may be triggered if rollback semantics are required for a specific batch operation type.

## Bulk Chunk Writes

Some batch operations apply one kind of change to a very large number of aggregates at once, such as a payment file from a client or a lockbox, a placement file of new accounts, or a mass update. Processed one command per transaction, an operation like this spends most of its time on the fixed cost of each transaction and each statement rather than on its business logic. A batch job type may therefore be designated a bulk operation. A worker processing a chunk of a bulk operation writes the whole chunk in one transaction, with set-based statements that insert all of the chunk's events and update all of its state rows together.

Aggregate-level hash chaining is what makes this possible. Each aggregate's chain depends only on that aggregate's own previous event, so the events of a thousand aggregates can be hashed independently and written together. A global chain would forbid it, because every event would wait on the one before it. A load of new aggregates, such as a placement file, is the simplest case, since a new aggregate has no previous event to read.

The bulk path is a way of running command handlers, not a way around them. The designation is part of the batch job type's definition. Every bulk chunk write holds to the following invariants.

> **BULK CHUNK INVARIANTS**
>
> **Same events**: each item produces exactly the events, in exactly the shape, that its command would produce through the single-command path, apart from the values the store assigns. Projections, workflows, the Pending Event Register, and the checkpoints cannot tell a bulk-written event from any other. PII fields are encrypted field by field at the serialization layer, as on every write.
>
> **Same rules**: each item is validated against its aggregate's current state by the same business logic as its command handler. An item the command handler would reject is rejected in bulk too, recorded against the chunk, and left out of the write, and the rest of the chunk proceeds.
>
> **Pre-event workflows**: the pre-event workflows of [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md) are evaluated for each item before the chunk is written, with the same outcomes as for a single command, including rejection and changes to provisional state.
>
> **Locks and versions**: the worker locks the state row of every aggregate in the chunk with SELECT FOR UPDATE, in primary key order, before reading any aggregate's previous event, and it checks each aggregate's version as the single-command path does. Locking in key order keeps bulk workers from deadlocking one another.
>
> **Hashing**: the WSM hashes every event individually and chains it to its own aggregate's previous event, within the chunk's transaction, as [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) requires of every write. A bulk insert that bypasses the per-event hash is a critical invariant violation.
>
> **Atomicity**: the chunk's events, its state changes, and its pending_workflow_evaluation rows commit together or not at all.
>
> **Fallback**: if the chunk's transaction fails, nothing from it is committed, and the worker reprocesses the chunk one command per transaction through the normal command handler path, which isolates the item that caused the failure.
>
> **Small chunks**: a bulk chunk is small enough that its transaction finishes in seconds. A long transaction holds its aggregates locked against live work, and it holds back the high-water mark that every reader of the event stream waits on, as described in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md).

## Sequence Numbers and the Write Path

The global sequence number in core.event is assigned by a PostgreSQL sequence generator. PostgreSQL sequences guarantee uniqueness and monotonic increase within a session but do not guarantee that a lower sequence number commits before a higher one. A transaction that acquires sequence 999 may commit a nanosecond after the transaction that acquired sequence 1000. Both records exist; the ordering reflects assignment time rather than commit time. This is normal and acceptable: the sequence provides a unique total order for all events, not a commit-order guarantee. Readers of the stream and the checkpoint module account for it by stopping at the high-water mark defined in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md).

Gaps in the sequence are expected. A transaction that acquires a sequence number and then rolls back consumes the number for good, and a crash between acquiring a number and committing does the same. No mechanism depends on the sequence being gapless and none looks for gaps. Deletion is detected by the per-aggregate hash chains and the delta checkpoints defined in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md).

Checkpoint frequency is therefore a genuine security configuration decision. Until a checkpoint covers an event, removing it leaves cryptographic evidence only if a later event on the same aggregate chains to it. Once a checkpoint token exists covering a sequence number, the presence or absence of that record is cryptographically anchored externally and verifiable forever. A shorter checkpoint interval means a smaller vulnerability window in both time and event count. Agencies with high sensitivity accounts or strong adversarial threat models should configure shorter checkpoint intervals. The TSA request cost is trivially small even at high frequency, as established in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md).

It is also worth noting that the realistic threat this architecture defends against is not a sophisticated attacker racing to delete a record in the seconds before a checkpoint fires. Records are not typically deleted the moment they are written. The far more common scenario is an agency facing litigation or a regulatory inquiry months or years later, discovering that a particular note, event, or payment record is inconvenient, and wanting it removed. By that point, many checkpoints have already anchored the record cryptographically, and in most cases later events on the same aggregate have chained to it. Deleting it breaks the per-aggregate hash chain and invalidates the checkpoint hash for the window that covered it, and those two failures are the proof that something was removed.

## PostgreSQL High Availability and Disaster Recovery

Wax's HA/DR at the database layer is provided by PostgreSQL's own streaming replication and the Patroni cluster management tool. The Collective documents these as the supported pattern and points to their respective project documentation rather than reimplementing their functionality.

The supported topology is a single primary PostgreSQL node accepting all writes, with one or more streaming replicas receiving a continuous replication stream. Replicas serve read-only queries including read model queries, BI tool connections, and reporting workloads, offloading the primary from read pressure. The primary handles all writes from the application service account and the WSM credential.

Patroni runs as a lightweight agent alongside each PostgreSQL instance. It monitors primary health via a configurable heartbeat interval, maintains distributed consensus through etcd (or Consul or ZooKeeper, at agency discretion), and promotes the most current replica to primary automatically when the primary fails to respond within the timeout threshold. Failover typically completes within 30 seconds. Patroni updates HAProxy or pgBouncer routing configuration automatically so application instances reconnect to the new primary without manual intervention.

pgBouncer provides connection pooling in front of PostgreSQL. Application instances connect to pgBouncer rather than directly to PostgreSQL. During a Patroni failover, pgBouncer is reconfigured to route to the new primary. Application instances experience a brief connection interruption, handled by the connection retry logic described below.

The Collective does not prescribe the etcd/Consul/ZooKeeper selection, the replica count, the synchronous versus asynchronous replication mode, or the specific Patroni tuning parameters. These are infrastructure decisions agencies make based on their durability requirements, RPO targets, and operational capabilities. The Collective provides a reference configuration demonstrating a working topology. Agencies adapt it to their environment.

## Application Tier Connection Resilience

Application instances must handle brief database disconnections gracefully. During a Patroni failover, the primary changes and existing connections to the old primary fail. The application connection pool must detect the failure, discard stale connections, and establish new connections to the new primary through pgBouncer within a configurable retry window.

In-flight command handler transactions that were not yet committed when the primary failed are lost. The client receives an error response and must retry. The command handler is idempotent by design: retrying a command that was partially processed but not committed produces the same result as the first attempt, because the event was never written and the authoritative state was never updated.

Pending workflow evaluations that were claimed from the outbox table but not yet completed are recovered automatically: the claim expiry timestamp ensures that an abandoned claim is reclaimed by another worker after the timeout. No manual intervention is required to recover in-flight workflow work after a failover.

## Scaling Inflection Point: When to Introduce a Message Broker

The SKIP LOCKED polling model is correct and sufficient for Year 1. At higher event volumes, polling a pending_workflow_evaluation table introduces latency: a worker that polls and finds no work must wait before polling again, and a burst of events may sit in the outbox for a polling interval before pickup. For most agency deployments this latency is acceptable.

When sustained event throughput reaches a level where polling latency becomes operationally significant, a lightweight message broker such as RabbitMQ or Valkey (the BSD-licensed open-source Redis fork) becomes the appropriate mechanism for waking workflow workers. In this model the broker carries a low-latency wake-up signal rather than the events themselves. The pending_workflow_evaluation outbox table remains the durable work queue and the source of truth: workers continue to claim work from it using SKIP LOCKED, and the broker replaces the polling interval with an immediate notification. A reduced-frequency SKIP LOCKED sweep is retained as a backstop, so a lost or undelivered notification never strands work.

The architecture is designed for this transition. The pending_workflow_evaluation outbox table defines the interface between event writing and workflow evaluation, and that interface does not change when the broker is introduced. The command handler write path, the per-aggregate locking and hash chain described in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md), and the SKIP LOCKED claiming all remain exactly as specified. The broker is layered on top purely as a notification mechanism: an operational upgrade, not an architectural redesign. The Collective will document the broker integration as an optional configuration available to high-volume deployments, and a deployment that never reaches the inflection point continues to run the polling model unchanged.

The application-side broker integration will use Wolverine, the .NET messaging library that shares authorship with Marten, the event store library adopted in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). Wolverine is selected over MassTransit primarily on licensing grounds. MassTransit moved to a commercial license with its version 9 release in early 2026, and its final open-source version loses support at the end of 2026; neither a per-application subscription cost nor a discretionary free-tier qualification is a sound foundation for a nonprofit-governed project intended to remain freely available. Wolverine's core, including its transports and its messaging layer, remains under the permissive MIT license, and its commercial offerings are confined to separate monitoring and advanced-feature add-ons that this integration does not require.

Wolverine will be adopted in a deliberately narrow slice: the broker transport, a best-effort publisher that emits a wake-up notification after a command transaction commits, and a consumer that triggers the existing SKIP LOCKED claim-and-process cycle on the pending_workflow_evaluation table. Wolverine's mediator, its transactional outbox, and its Marten aggregate handler workflow are intentionally not adopted. The wake-up notification is published outside the command transaction, so the messaging library never participates in the integrity-critical write described in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). This narrow footprint keeps Wolverine confined to the role of a transport and fully replaceable.

Correctness does not depend on the notification being delivered. The broker may provide at-least-once delivery, a notification may be lost, and the same notification may reach more than one worker; in every case the SKIP LOCKED claim on the durable outbox table deduplicates and serializes the actual work, and the retained backstop sweep recovers anything a lost notification missed. Wolverine supports both candidate brokers, RabbitMQ through its native transport and Valkey through its Redis transport, so the operator's broker selection remains open. The integration is an optional, operator-enabled configuration targeted at Wax v3 and later; a deployment below the inflection point installs neither the broker nor Wolverine.

## The Collective's Responsibility Boundary

> **WHAT THE COLLECTIVE PROVIDES**
>
> Stateless application tier architecture enabling horizontal scaling. WSM horizontal scaling with shared key store and no inter-instance coordination requirement. Per-aggregate row lock serialization guaranteeing hash chain integrity across concurrent writers. SKIP LOCKED work claiming for all distributed workload types. Chunk-based batch job parallelism with coordinator election and worker claiming. Bulk chunk writes for batch job types designated as bulk operations. Connection retry logic and pool recovery behavior in the application tier. Reference Docker/Compose topology demonstrating the component architecture. Reference Patroni configuration and pointers to Patroni, pgBouncer, and PostgreSQL streaming replication documentation. Documented scaling inflection point and optional message broker integration path. The reference Docker Compose topology and Patroni configuration listed here are delivered as the reference deployment architecture specified in [Shared Design Decision 8](../shared/SHARED-0008-reference-deployment-architecture.md).
>
> **WHAT IS THE AGENCY'S RESPONSIBILITY** Infrastructure provisioning: servers, VMs, cloud instances, network topology, and firewall configuration. PostgreSQL cluster deployment: installing and configuring PostgreSQL, Patroni, etcd/Consul/ZooKeeper, pgBouncer, and HAProxy per the reference patterns. Backup schedules and retention: configuring PostgreSQL base backups, WAL archiving, and backup storage. RTO and RPO targets: the Collective does not prescribe acceptable downtime or data loss thresholds. Agencies configure replication mode (synchronous vs asynchronous) and failover timing based on their own requirements. Failover testing: periodic failover drills to validate that the HA configuration actually works as expected. Monitoring and alerting: Patroni, pgBouncer, and application tier health monitoring. Capacity planning: determining the number of application instances, WSM instances, and PostgreSQL replicas required for the agency's workload.

## Implementation Phasing

**Wax v1 (MVP):** Single-node deployment. Single PostgreSQL instance, single application instance. No SKIP LOCKED coordination. Standard PostgreSQL backup guidance (pg_dump, WAL archiving).

**Wax v2:** Docker Compose HA reference (PostgreSQL primary + streaming replica). Stateless application tier with multiple instances behind a load balancer. SKIP LOCKED for distributed batch job coordination. Bulk chunk writes for batch job types designated as bulk operations. pgBouncer connection pooling.

**Wax v3+:** Patroni-based automatic failover. Message broker integration via Wolverine (RabbitMQ or Valkey) for high-volume event fan-out. Chunk-based batch parallelism.

**Breaking change risk: NONE.** HA is infrastructure, not schema.

## Implications For Contributors

No component may store state in the local file system of an application instance. State lives in PostgreSQL or in the WSM key store. A component that writes to local disk is incompatible with horizontal scaling.

Command handlers must acquire SELECT FOR UPDATE on the aggregate's authoritative state row before any event write. This is not optional. A command handler that writes events without the row lock may corrupt the per-aggregate hash chain under concurrent load.

All work queue consumers must use SELECT FOR UPDATE SKIP LOCKED. A consumer that uses a plain SELECT without locking will race with other consumers and produce double-processing.

The pending_workflow_evaluation outbox table write must be atomic with the core.event write. Both succeed or both fail. An event written to core.event without a corresponding outbox row will never trigger workflow evaluation.

Batch job chunk size is a configuration parameter on the batch job definition. Contributors who introduce new batch job types must declare a default chunk size appropriate to the expected row size and processing cost of that job type.

A contributor who designates a batch job type as a bulk operation must provide a test showing that the bulk path and the single-command path produce the same events and the same state for the same input, apart from the values the store assigns, and that test must keep passing for as long as the designation stands.
