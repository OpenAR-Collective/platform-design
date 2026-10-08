---
id: WAX-0013
title: "Event Chain Integrity and Tamper-Evidence"
status: Accepted
version: 1.1
area: wax
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 13: Event Chain Integrity and Tamper-Evidence

## Decision

Wax will implement cryptographically verifiable, tamper-evident audit history through three complementary mechanisms: per-aggregate hash chaining within core.event, delta-based periodic checkpoint anchoring to an external RFC 3161 trusted timestamp authority, and a formal break-glass process for authorized chain modifications. PII fields in event payloads will be protected through serialization-layer cryptographic erasure, with the encryption key as the retention mechanism rather than record deletion. A pluggable anchor interface allows alternative anchoring mechanisms to be added in future. The Foundation will not operate a timestamp authority, a blockchain, or any other anchoring service; anchoring relies on independent third parties, and the Foundation's role is limited to shipping a recommended default and, on request, suggesting alternatives.

## Why This Matters

Incumbent collections platforms were largely built when an audit trail meant a log table that a system administrator could edit. Regulatory requirements and litigation exposure have grown enormously since then, but the underlying infrastructure has not kept pace. Wax will be the first platform in the AR industry to build cryptographically sealed, independently verifiable audit history into its core architecture from inception. Agencies running Wax will be able to demonstrate to regulators, creditors, and consumers that their operational records are trustworthy and provably unaltered, in a way no proprietary closed-source platform can credibly claim.

## Per-Aggregate Hash Chaining

core.event is a single shared table. Every event from every aggregate across the entire system is written into it: a payment posted on account A and an address changed on account B are both rows in the same table. The table carries a global sequence number, a monotonically increasing integer assigned by PostgreSQL's sequence generator, which establishes a total ordering of all events written to the store.

Two columns in core.event support per-aggregate hash chaining: event_hash and prior_event_hash. Both are formally declared in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). The event_hash column stores a SHA-256 cryptographic hash computed over the event's immutable content: aggregate type, aggregate primary key, event type, schema version, payload, occurred_at timestamp, actor reference, and reason code. The prior_event_hash column stores the event_hash of the immediately preceding event for the same aggregate, linking every event cryptographically to its predecessor within that aggregate's own history.

Hash chaining is per-aggregate rather than global. A global chain would require every new event to know the hash of the single globally preceding event, serializing all writes system-wide and making concurrent writes to different aggregates impossible. Per-aggregate chains are independent sequences that live within the shared core.event table. Account A's chain and Account B's chain do not reference each other. Account A's prior_event_hash at sequence 1000 points to Account A's previous event at sequence 947, regardless of what was written at sequences 948 through 999 for other aggregates. Multiple aggregates can write concurrently without conflict because their chains never intersect.

Same-aggregate write serialization is enforced by a SELECT FOR UPDATE row lock on the aggregate's authoritative state row, acquired before any hash computation or event write begins. If two command handlers attempt to write to the same aggregate simultaneously, the second blocks on the lock until the first transaction commits. This guarantees that each event for a given aggregate sees the correct prior event hash and that no two events claim the same predecessor. The lock is held only for the duration of the write transaction and released immediately on commit.

The hash is computed over the encrypted ciphertext of PII fields, not the plaintext. This means the hash remains stable after key destruction: the ciphertext does not change when the key is destroyed, so the chain continues to verify correctly even for records whose PII content is no longer decryptable. Verification of a record with a destroyed key confirms the record was not modified, even though its PII content is inaccessible.

Each value enters the hash in the form in which it is stored in the payload. A monetary amount is hashed as the canonical string defined in [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md), exactly as the framework's money type wrote it, and it is never derived again from a number at verification time. A later change to a currency's standard number of digits therefore cannot change the hash of an event already stored.

## Three Complementary Integrity Tiers

Wax's tamper-evidence architecture operates across three independent and complementary tiers. Each tier catches different classes of tampering. No single tier is sufficient on its own, and each tier provides guarantees that the others cannot.

> **WHAT EACH TIER CATCHES**
>
> **Per-aggregate hash chain**: catches modifications and deletions within a specific account's history. This is the finest-grained mechanism. If any event for account A is deleted or its content changed, account A'x27;s chain breaks at that point. The break is detectable by recomputing hashes and finding a mismatch with the stored prior_event_hash values. Does not detect tampering with other accounts' events.
>
> **Global sequence numbers**: catch deletions anywhere in the event store, across all aggregates. The sequence is globally assigned and must be gapless. If any event is deleted, a gap appears in the sequence. A verifier scanning for gaps detects the deletion even if the per-aggregate chain for that aggregate has no other events that would reveal the break. Does not catch modifications to existing records, only deletions.
>
> **Delta checkpoint hash**: catches both deletions and modifications within a checkpoint window, across all aggregates. The checkpoint hash is computed over all events in a sequence number window in order. If any event in the window is deleted or its content changed, the recomputed hash will not match the RFC 3161 anchored value. Provides the broadest global coverage but at checkpoint granularity rather than per-event granularity.

Together, the three tiers provide defense in depth. The per-aggregate chain provides the strongest per-account guarantee. Global sequence gap detection provides a fast, cheap system-wide deletion check requiring no cryptographic tools. The delta checkpoint provides cryptographic proof of system-wide integrity at a point in time, externally anchored and independently verifiable by any third party.

## Delta-Based External Checkpoint Anchoring

The checkpoint module periodically computes a checkpoint hash covering only the events written since the previous checkpoint, a delta window rather than the full event history. The hash is submitted to an RFC 3161 trusted timestamp authority. The TSA signs the hash and returns a self-contained token recording the submitted hash, the signing time to millisecond precision, and the TSA's cryptographic signature. The token is returned to the agency and stored locally. The TSA retains no copy.

Delta-based checkpoints are essential for the break-glass mechanism to remain useful. A cumulative checkpoint, one that hashes the entire event history from the beginning, would be invalidated by any authorized break anywhere in history, rendering all subsequent checkpoints permanently suspect. A delta checkpoint covers only a defined window of sequence numbers. An authorized break within a window invalidates at most the checkpoint spanning that window. All prior checkpoints and all subsequent checkpoints covering events written after the break remain fully valid and independently verifiable.

> **CHECKPOINT RECORD SCHEMA**
>
> **start_sequence_number**: the first event sequence number covered by this checkpoint.
>
> **end_sequence_number**: the last event sequence number covered by this checkpoint.
>
> **checkpoint_hash**: SHA-256 hash computed over all events in the window in sequence number order.
>
> **tsa_endpoint**: the TSA endpoint used, for verification reference.
>
> **rfc3161_token**: the binary token returned by the TSA, stored in full.
>
> **created_at**: UTC timestamp when the checkpoint was computed and submitted.
>
> **tsa_stamped_at**: the timestamp embedded in the RFC 3161 token, extracted for query convenience.

Checkpoint records are stored in a dedicated append-only table. For installations where the threat model includes a privileged insider, tokens should additionally be replicated to write-once cloud storage such as AWS S3 Object Lock in compliance mode. Write-once storage prevents token deletion even by the account owner during the configured retention period, closing the scenario where an attacker with database access attempts to delete tokens alongside the records they are trying to conceal.

## Verification and Diagnostic Process

Verification walks the checkpoint sequence in order. For each checkpoint, the verifier recomputes the hash over the events in the declared sequence number window and compares it to the hash stored in the checkpoint record. The TSA token is independently verified using the TSA's public certificate, confirming the checkpoint existed at the recorded time. A checkpoint that passes both verifications is clean. A checkpoint that fails hash comparison triggers a break record lookup within that sequence window.

The verifier runs a separate sequence number gap scan across core.event independently of the checkpoint walk. Every sequence number from the minimum to the maximum present in the table must exist. A missing sequence number is a signal to run checkpoint verification for the window containing the gap. The checkpoint hash is the authoritative determination of what happened: if the checkpoint for that window validates correctly against its RFC 3161 token, the gap was a legitimate rollback artifact from a transaction that acquired the sequence number and then rolled back before committing. If the checkpoint fails to validate, a record was deleted. The gap scan is a fast, cheap first pass that identifies windows requiring cryptographic investigation. The checkpoint is the oracle that resolves whether a gap is benign or evidence of tampering.

When a break is detected, the checkpoint history provides a precise time window for the event. The most recent checkpoint before the break that verifies cleanly establishes the last known-clean state. The failed checkpoint establishes the window during which the modification occurred. More frequent checkpointing narrows this window. Hourly checkpoints localize any tampering to within one hour. The agency configures the checkpoint interval based on risk tolerance.

## TSA Selection and Cost

Several RFC 3161 TSAs operate as free public services including those operated by DigiCert, Sectigo, and GlobalSign. Government-operated TSAs exist in several countries. For an installation generating hourly checkpoints, the annual request volume is approximately 8,760 timestamps. Even commercial TSAs that charge per token do so at fractions of a cent. The checkpoint module ships with a default free public TSA endpoint. Agencies may configure an alternative TSA. The pluggable anchor interface means the TSA can be changed without any module code changes.

## PII Field Enforcement and Cryptographic Erasure

Because the event store is permanent and the hash chain makes modification detectable, any PII that enters the event store unencrypted is there forever with no remediation path. This is not a hypothetical risk. It is a structural property of the architecture that must be addressed structurally, not procedurally.

Every field in every event payload schema must carry an explicit PII classification before it can be used. The classifications are: not PII, PII (encrypted at rest using the subject's encryption key), and sensitive but not PII (encrypted for other reasons such as financial data). There is no unclassified option. A payload schema field with no classification does not compile. The module contract validator rejects any payload schema containing an unannotated field.

Encryption happens at the serialization layer, not in application code. When an event is about to be written to core.event, the serialization layer inspects the payload schema annotations, identifies all PII and sensitive fields, encrypts those values using the subject's encryption key, and writes the encrypted payload. Application code never decides whether to encrypt a field. The infrastructure enforces it based on the declared schema. There is no API path for writing unencrypted PII to the event store.

> **DEFENSE IN DEPTH FOR PII PROTECTION**
>
> **Compile-time enforcement**: payload schemas with unannotated fields do not build. Module authors cannot ship a module with unclassified fields.
>
> **Serialization-layer automatic encryption**: annotated PII fields are encrypted without command handler involvement. The only way to store a PII field value is through the annotated schema path.
>
> **Runtime write validation**: before commit, the write path verifies that all PII-annotated fields in the payload are present as ciphertext, not plaintext. A payload containing recognizable plaintext in a PII-annotated field is rejected.
>
> **Periodic audit scanning**: a scheduled tool scans event payloads for values matching known PII patterns (SSN format, date of birth, credit card numbers). Any match in a non-encrypted field triggers an alert.
>
> **UDT field default-to-encrypt**: UDT fields cannot be validated at compile time because their schema is defined at runtime. All UDT fields default to encrypted unless the agency explicitly marks them as non-PII during field definition. The schema builder UI requires a PII classification for every field and surfaces a prominent warning when the agency selects non-PII for a free-text field.
>
> **Staged import scanning**: bulk data imports into UDTs pass through a staging area where a mandatory PII pattern scan runs before the data is committed. An import is blocked if potential PII is detected in fields marked as non-PII, and the agency is shown the findings before being asked to reclassify or abort.

Cryptographic erasure is the retention mechanism for PII fields. When a subject's retention period expires, the encryption key for that subject is destroyed. The encrypted ciphertext remains in the event table permanently. The hash chain is unbroken. The payload is present, but the PII content is irrecoverably inaccessible without the key. In most jurisdictions, key destruction is legally equivalent to data deletion for retention compliance purposes. The key management architecture, including per-subject key storage, retention-triggered key destruction workflows, and audit logging of key lifecycle events, is a dependency on the security specification from [Wax Design Decision 14](WAX-0014-encryption-and-data-protection.md).

## Break-Glass: Authorized Chain Modification

Some agencies will need to perform deliberate chain modifications that cryptographic erasure does not address: removal of PII that was accidentally loaded into a non-encrypted field, true record deletion per agency policy, or compliance with a regulatory directive requiring record removal. A system that provides no sanctioned path for these operations will see agencies perform unsanctioned modifications with no documentation, no audit trail, and no explanation for regulators. The break-glass mechanism provides a formal, controlled, auditable path for authorized chain modifications.

The break-glass process is deliberately cumbersome. Friction is a feature. The process requires a request from an authorized administrator specifying the affected sequence numbers, a reason category from a defined list (PII remediation, legal hold release, retention compliance, regulatory directive, or other with mandatory explanation), and a free-text explanation of meaningful minimum length. The request enters a review queue. A second authorized administrator with a separate credential must approve before execution proceeds. Two-person authorization prevents a single rogue administrator from quietly modifying the chain.

Upon approval and execution, a break record is created in a dedicated break registry table. The break record is signed with an RFC 3161 timestamp, providing an external anchor proving the break was documented at a specific time. The break record cannot be modified after creation. Supplemental records may be added but the original is permanent.

> **BREAK RECORD CONTENTS**
>
> **Affected sequence numbers**: the complete list of event sequence numbers modified or deleted.
>
> **Reason category**: from the defined classification list.
>
> **Explanation**: full free-text description of why the modification was necessary.
>
> **Requesting administrator**: identity, credential type, and timestamp of request.
>
> **Approving administrator**: identity, credential type, and timestamp of approval.
>
> **Execution timestamp**: when the modification was carried out.
>
> **Pre-modification hashes**: the event_hash values of all affected records before modification, so an auditor can confirm what was there.
>
> **Modification description**: what was done (deleted, field replaced, key destroyed).
>
> **Legal or regulatory basis**: citation if applicable.
>
> **RFC 3161 token**: timestamp token proving this break record existed at a specific time.

After execution, the chain is resealed from the break point forward. The event record immediately following the break has its prior_event_hash updated to reference the break record rather than the deleted or modified record. From that point forward the chain is intact and valid. The break record serves as the bridge between the pre-break and post-break chain segments.

## Verification with Explained and Unexplained Breaks

The verification tool distinguishes between two categories of broken chain. An unexplained break is a sequence number where the hash chain does not validate and no break record exists in the registry. This is evidence of tampering or system failure and is reported as a critical integrity finding. An explained break is a sequence number where the hash chain does not validate but a valid, signed break record exists documenting the authorized modification. This is reported as an explained modification and is not treated as a integrity violation.

Delta checkpoint validation follows the same logic. A checkpoint that fails hash comparison triggers a break record lookup within that sequence window. If a valid break record is found, the checkpoint failure is explained and verification continues. The RFC 3161 tokens from before and after the break remain independently valid. The break record bridges the two periods. An auditor can trace the complete timeline: chain was intact through this checkpoint, break was authorized and documented at this time with this explanation, chain is intact from this checkpoint forward.

## Event Store Scale and Performance

A billion-row event table with proper indexing is not a transactional performance problem. Queries that matter for daily operations filter by aggregate_pk and order by sequence_number, hitting a btree index on those two columns. That query scans a few hundred rows regardless of whether the table has a million rows or ten billion. Index-based queries are insensitive to table size.

Full-table analytics queries do not belong in the raw event store. They belong in read models and reporting infrastructure as established in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). The event store is the source of truth; purpose-built read models are the query surface. Backup duration does grow with table size, which is an operational and infrastructure planning concern rather than an architectural defect. Incremental backup strategies, tablespaces on separate storage tiers, and point-in-time recovery are all well-supported by the PostgreSQL ecosystem. The storage cost of a complete, auditable, reproducible event history is the price of the compliance infrastructure the industry has always needed.

## Key Deletion as Evidence Destruction

Cryptographic erasure creates a new risk: if notes are encrypted per subject, destroying the subject's encryption key makes all of that subject's encrypted content permanently inaccessible. An agency could destroy a key early, before the retention period expires, to conceal a specific incriminating note. This is evidence destruction dressed as data management, and the platform must make it detectable.

The defense is a combination of architectural constraints and tamper-evident logging that ensures early key destruction is always detectable, attributed, and externally anchored.

Key destruction is possible only through two authorized paths: the automated retention workflow triggered by a scheduled retention date, and the break-glass process with two-person authorization and mandatory documentation. There is no manual key deletion API and no administration UI that destroys a key on demand. Any attempt to destroy a key through any other path is rejected at the key management service boundary.

Every key lifecycle event is recorded in a dedicated key audit log: creation, scheduled retention date assignment, rotation, and actual destruction with the path used (retention workflow or break-glass). The key audit log is itself a hash-chained, checkpointed, tamper-evident structure using the same architecture as core.event. Destroying a key without a corresponding audit log entry breaks the key audit log chain, making the omission detectable. An audit log entry that shows a key was destroyed before its scheduled retention date is documented evidence of early destruction, timestamped and verifiable.

The delta checkpoint scope covers the key audit log alongside the event store. A checkpoint includes a hash of the current key audit log state. This means the state of the key registry at any point in time is externally anchored by the same RFC 3161 tokens that anchor the event chain. An attacker who destroys a key and attempts to alter the key audit log to conceal the early destruction would break the key audit log's hash chain, and that break would be captured in the checkpoint that follows.

Destroying the key destroys the content but not the evidence that content existed. The event record remains in core.event permanently with its encrypted ciphertext intact and its position in the hash chain verified by all subsequent checkpoint tokens. The key audit log shows exactly when the key was destroyed and whether the destruction was scheduled or premature. An auditor can determine that a note event exists, that its content is inaccessible because the key was destroyed on a specific date, and whether that date was consistent with the retention policy or suspiciously early. Premature destruction through the break-glass process additionally produces a signed break record with the reason and two-person authorization. The absence of content is documented, datable, attributed, and externally anchored.

## Pluggable Anchor Interface and Future Options

The checkpoint module defines an anchor interface with two methods: submit_checkpoint, which accepts a hash and sequence window and returns an anchor receipt, and verify_checkpoint, which accepts a stored receipt and returns a pass or fail with details. The RFC 3161 TSA implementation is the default. Alternative implementations, including public blockchain anchoring, can be added without architectural changes. Multiple anchor implementations can be active simultaneously, providing redundant external verification. A Foundation-operated anchoring service was considered and rejected. Independent public services already provide the function at negligible cost, operating one would take on liability without adding assurance, and an anchor run by the platform's own steward makes a weaker independence claim than one run by an unrelated third party.

## Implementation Phasing

**Wax v1 (MVP):** Schema columns present (event_hash, prior_event_hash) but hash computation deferred. Columns populated with placeholder values or nulls. The checkpoint anchoring and TSA submission infrastructure is not built in v1.

**Wax v2:** Hash chain computation activated. Backfill utility for v1 data. Per-aggregate chain verification tooling. Delta checkpoint hashing with TSA submission.

**Wax v3+:** Break-glass workflow with two-person authorization.

**Breaking change risk: LOW.** Columns exist from day one. Computation is additive.

## Implications For Contributors

The hash computation specification, including which fields are included, their serialization order, and the written form of each kind of value, which for a monetary amount is the canonical string defined in [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md), must be formally specified and must never change after deployment. Any change breaks all existing chains.

The Wax Security Module (WSM) computes event_hash and prior_event_hash within the same atomic transaction as the event write. Command handlers do not compute hash values directly. Invoking the WSM hash computation is a required step in the command handler write path; a write that bypasses it is a critical invariant violation. Hash values may not be computed after the fact.

Every field in every event payload schema must carry an explicit PII classification. A payload schema with any unannotated field does not compile. This rule applies to Wax, to all module-contributed event types, and to all UDT-generated event types.

The break-glass process is a Wax capability and is not extensible by modules. Module authors may not implement alternative chain modification mechanisms.

The checkpoint module is optional. Agencies that do not enable it receive the hash chain tamper-evidence guarantee but not the external timestamp anchoring. The hash chain is always maintained regardless of whether the checkpoint module is active.
