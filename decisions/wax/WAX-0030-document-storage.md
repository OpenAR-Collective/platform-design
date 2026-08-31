---
id: WAX-0030
title: "Document Storage"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 30: Document Storage

## Decision

Wax will store documents by separating the document aggregate from the document bytes. The document aggregate, metadata, content hash, references, lifecycle events, retention class, and an optional encryption key reference, lives in the core database and is hash-chained like any other aggregate. The bytes live behind a pluggable storage provider that may be a filesystem or network path, a cloud object store, or an external document repository the agency already operates. A document is referenced by aggregates through a typed, labeled, many-to-many relationship. The document is immutable once stored; it is never edited, only superseded or destroyed.

## The Cut: Aggregate Apart From Bytes

The decision that organizes everything else is the separation of the small, structured aggregate from the large, opaque bytes. The aggregate is tiny and transactional and stays in the core database with the rest of the platform. The bytes, which are large and may be very large for media, live wherever the agency chooses through a storage provider interface. With that separation, the question of disk versus blob stops being an architectural question and becomes a provider configuration: the architecture above the provider, references, integrity, access control, and retention, is identical regardless of where the bytes sit. This is the same provider-seam posture taken with the event store, where the interface is the commitment and the backing implementation is swappable.

## Byte Storage Options

Two byte stores are co-equal in the v2 release, neither privileged over the other. A filesystem or network path suits an agency that prefers a one-time hardware purchase, an on-premises file server, or sunk infrastructure it already owns. A cloud object store suits an agency comfortable with recurring storage cost and drawn to archive tiers, which fit immutable documents well. The choice is the agency's, and it follows their capital-versus-operating-cost preference rather than a platform mandate. Database-blob storage is deferred to Wax v3 and later and is discouraged even then, because keeping large bytes in the primary database complicates the very thing agencies want, the ability to host documents on separate, cheaper, or larger storage without re-architecting the database.

## Custody: Managed or External

A document has one of two custody models, chosen by the agency for any document or document class. Under HiveAR-managed custody, the bytes sit in a provider HiveAR controls, and HiveAR provides full integrity, optional encryption, and retention and destruction guarantees. Under external-reference custody, the bytes remain in the agency's own document system or file server, and HiveAR holds only the metadata, the reference, and the content hash captured when it first saw the document. The honest tradeoff is surfaced rather than enforced: HiveAR cannot prove the integrity of bytes it does not hold, so tamper-evidence on externally held documents is only as strong as the hash captured at reference time. An agency that wants HiveAR to manage and prove its evidence configures managed custody for those documents; an agency that prefers to treat every document uniformly in its existing system is free to do so.

## Integrity Without Holding the Bytes

The document's content hash is recorded in the document-created and reference events. The hash chain established in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) then proves the bytes have not changed without containing them, a content hash sealed inside the event hash chain. A recorded call or a signed agreement under managed custody is tamper-evident by the same mechanism that protects every other domain fact. Under external custody the same hash is recorded, with the caveat above that HiveAR cannot police a store it does not control.

## Typed, Many-to-Many References

A document is linked to the aggregates that use it through a many-to-many bridge, polymorphic on the aggregate side the way core.event already references aggregates. One document may be referenced by many aggregates, and one aggregate may reference many documents. Each reference carries a type and label, so the same validation document shared by a set of accounts is labeled as the validation of debt by each account that points to it. Attaching and detaching a reference are document events, so the bridge table is a projection and the question of who attached a document, to what, and when remains auditable. An account-relevant attachment also surfaces as an account domain fact through the normal command handler, the same pattern tasking uses.

## Retention and Destruction Reclaim Space

Documents diverge from core.event on destruction. Crypto-shredding alone does not satisfy a document retention obligation, because the encrypted bytes still occupy disk. Document destruction therefore deletes the bytes to reclaim the space and records a destruction event, leaving a tamper-evident tombstone: the document existed, here was its content hash, here is what it was attached to, and here is when and under what policy it was destroyed. Where optional encryption is in use, key destruction remains as defense in depth and as the instant-unreadable step when a consumer is erased, but byte deletion is what reclaims the disk. Retention classes and legal holds govern eligibility, and a hold overrides a class. The scheduled destruction sweep is a recurring Job Scheduler job that finds eligible documents and destroys them.

## Shared Documents and Most-Restrictive Retention

Because a document may be referenced by many aggregates, its destruction eligibility is computed across the whole reference set rather than from a single timer. A validation document shared by a set of accounts cannot be destroyed when one account's retention lapses if the others still require it, and a legal hold on any one referencing aggregate freezes the document for all of them. A shared document is destroyable only when no remaining reference requires it and no hold touches it anywhere, the document analog of most-restrictive-wins. The Job Scheduler sweep evaluates that condition before deleting any bytes.

## Optional Encryption and the Intake Pipeline

Document encryption is optional, not mandatory, because many agencies prefer their documents remain readable on disk for direct browsing or for their own external tooling. When encryption is enabled, HiveAR holds the keys, and intake becomes an asynchronous step: a document arrives, is queued, is encrypted into the store, and has its metadata updated, so encrypting a large recording never blocks an upload. That intake queue is the first instance of a document processing pipeline running on the platform's standard SKIP LOCKED claim model; later processing steps such as optical character recognition, transcription, and virus scanning extend the same rail. The MVP has no pipeline because it performs no processing; it points at readable documents and does nothing to the bytes.

## Access Control Is the Application's, Disk Security Is the Agency's

The application enforces who may view or fetch a document through HiveAR role-based access control, resolved across every aggregate that references the document, and serves the bytes without exposing a durable public URL. Securing the byte store at the filesystem or object-store layer is the agency's responsibility and prerogative; an agency that wants its documents browsable on disk by its own IT staff is free to arrange that. HiveAR governs access through the application and does not govern the agency's filesystem.

## Duplicate Detection, Not Deduplication

The platform does not deduplicate document bytes in storage, because per-subject encryption means identical plaintext encrypts to different ciphertext, so storage-level deduplication would buy little and complicate erasure. Because the content hash of every document is already recorded, a duplicate-document audit report is provided in v2 that surfaces documents sharing a content hash. Agencies find and manage their own duplicates; the platform never silently collapses them.

## Interoperation With Document Management Systems

Rich document-management capability, optical character recognition, full-text and semantic search, electronic signature, form-fill, approval routing, markup, and redaction, and on the voice side transcription, personal and payment information redaction, and channel separation, is a software category in its own right, and the Foundation will not grow one inside HiveAR. Mature open-source document repositories exist for agencies that want that sophistication, and HiveAR interoperates with them rather than reimplementing or forking them. The external-reference custody model is the seam: HiveAR holds the metadata, the reference, and the hash, while the repository owns the bytes and the rich features, reached over the repository's published interface, the CMIS content-interoperability standard for the enterprise repositories and plain REST for lighter tools. Candidates worth evaluating at decision time, with license suitability assessed carefully, include Mayan EDMS under the permissive Apache 2.0 license, Paperless-ngx under GPL with strong optical character recognition, and the enterprise tier of Alfresco and similar platforms, with caution toward any once-open platform that has drifted behind a commercial vendor. Derived artifacts such as a transcript, a redacted copy, or a channel-split recording are themselves documents linked to the original, so the aggregate-and-reference model already carries them. Recordings are simply large immutable documents; their processing is integration, not a separate store.

## Implementation Phasing

**Wax v2 (core):** The document aggregate and lifecycle events, filesystem-or-path and cloud object byte stores, HiveAR-managed and external-reference custody, typed many-to-many references, content-hash integrity, retention classes and legal holds, destruction by byte deletion with a tombstone, the cross-reference most-restrictive destruction rule, application-layer access control, and the duplicate-document audit report.

**Wax v2 enhancement or v3:** Optional document encryption with HiveAR key custody and the asynchronous intake processing pipeline. The timing is low-stakes because the capability is additive.

**Wax v3+:** Database-blob storage as a discouraged option, and the rich document-management capabilities, delivered through interoperation with a mature open-source document repository rather than built in HiveAR. The selection of a repository to integrate with, and the depth of that integration, is the v3+ decision.

**Breaking change risk: LOW. The document aggregate is rebuildable from its events, the storage provider is a swappable interface, and references, encryption, processing steps, and integrations are all additive layers above a stable core.**

## Implications For Contributors

Documents are aggregates, and bytes are not. The aggregate, its references, and its hash live in the core database and flow through command handlers into core.event. The bytes live behind the storage provider interface, and no code path may assume a particular byte store.

References are typed and many-to-many. A document is attached to an aggregate through the reference bridge with a type and label, never by embedding the document in the aggregate. The same document may be referenced by many aggregates at once.

Destruction deletes bytes and keeps the tombstone. Reclaiming disk space is the point of document destruction, so destruction removes the bytes while preserving the document's event history and content hash. A shared document is destroyed only when no reference requires it and no hold applies.

Rich document features are integrations, not core. A contributor must not grow optical character recognition, search, signature, or similar capability inside the document store. These are reached by interoperating with an external repository through the external-reference seam.
