---
id: WAX-0026
title: "Event Schema Versioning"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 26: Event Schema Versioning

## Decision

Wax will evolve event payload schemas through read-time upcasting, never through in-place migration of stored events. A stored event is byte-immutable for its entire lifetime. Each event type carries an explicit schema_version on its core.event row, scoped to that event type, and that version is included in the [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) hash input. Only breaking changes increment the version; additive changes do not. Marten provides the upcasting implementation. The pair of event_type and schema_version fully determines how a stored payload is interpreted.

## Why This Matters

An event-sourced system lives or dies on how it handles schema change. The event store is the permanent record of truth, and the platform will run for decades against events written under schema definitions that have since evolved. The constraints in this platform are unusually strict: events are immutable, the per-aggregate hash chain is computed over the stored payload, and that hash specification can never change after deployment. A versioning approach that fits those constraints must be settled before hash computation activates, because the schema_version marker is part of the hashed content and the hash input cannot be altered once real hashes exist. This decision is therefore a v1 schema investment with a hard deadline, in the same category as the hash columns and the internationalization tables.

## The Weak-Schema Foundation

The uniform keyed JSON payload model defined in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md) is a weak schema by nature. The prior_value and new_value columns are keyed objects, so adding a field to an event type is adding a key, and older events simply lack that key. A reader tolerates the missing key without transformation. Additive evolution, which is the overwhelming majority of real schema change, therefore requires no version increment and no upcaster. This property narrows the entire versioning problem to the rare genuinely breaking change: renaming a field, changing a field's meaning or type, or splitting one event type into two.

## Upcasting on Read, Never Migration in Place

The hash chain forces a single safe model for breaking changes. Because the hash is computed over the stored payload and is immutable, a stored event can never be rewritten into a new shape; doing so would alter the bytes the hash covers and break the chain. Schema evolution is therefore strictly a read-time concern. The stored row remains exactly as written, its hash verifies against its original content, and any transformation to the current shape happens in memory after verification. An upcaster reads an event written under an older version and produces the current representation for the consumer that requested it. The stored event is history; the upcaster bridges it to the present.

## The Schema Version Marker

A schema_version column on core.event records which revision of an event type's payload schema a given row conforms to. The version is event-type-specific: it means revision N of this specific event type, and each event type maintains its own independent version sequence. A global or cross-type version number is explicitly rejected, because interpretation is always per event type and a shared counter would couple unrelated event types and convey nothing specific about any one of them. New event types begin at version 1, and most event types remain at version 1 permanently, since only breaking changes advance the number.

The schema_version is included in the [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) hash input, alongside event_type. The version determines how the payload is interpreted, so it is semantic content rather than storage metadata, and hashing it makes any alteration of the marker tamper-evident. This is the reason the decision must precede hash activation: once real hashes exist, the input specification is frozen. A purely informational minor version that incremented on additive changes was considered and rejected, because it would tax the common additive path for narrow benefit and place non-interpretation metadata into the integrity boundary; the additive history is captured instead in a schema changelog held as documentation.

## Encryption Envelope Handling

Upcasters are structural transformations only and never touch the contents of an encryption envelope. When an upcaster moves or renames a field whose value is a [Wax Design Decision 15](WAX-0015-security-module.md) encryption envelope, it carries the envelope across as an opaque value and never decrypts or re-encrypts it. This rule has two consequences. Upcasting requires no access to key material, and upcasting remains valid for records whose subject key has already been destroyed, since the envelope ciphertext is moved without being read. Schema evolution and cryptographic erasure are therefore fully independent.

## Projections, Replay, and the Upcaster Registry

The upcaster registry is the single place in the platform where historical schema knowledge lives. Projection code, read model builders, and command handlers are written against the current shape of each event type only. When the event store is replayed to rebuild an authoritative state table or a read model, every historical event passes through the registry and arrives at the consumer in its current shape. This keeps the rest of the codebase free of accumulated backward-compatibility branches: the knowledge of how a v1 payload differs from a v3 payload exists in exactly one upcaster chain and nowhere else.

## Schema Changelog

Each event type's schema history is recorded in a schema changelog held as project documentation: a dated list of revisions per event type, each with a description of what changed and whether it was additive or breaking. The changelog is the human-readable narrative of how the event vocabulary evolved, and it supports forensic correlation of any stored event against the schema generation in effect when it was written. The changelog is documentation rather than a per-row stamp, which keeps the additive path frictionless while still preserving the evolution record.

## Implementation Phasing

**Wax v1 (MVP):** The schema_version column is present on core.event and is included in the documented hash input specification, even though hash computation itself is deferred to v2. All events are written at version 1. The upcasting mechanism is not yet active because no event type has evolved. This tier exists to lock the schema_version marker into the hash input before the specification freezes.

**Wax v2:** Upcasting activates alongside hash computation. Marten upcaster registration is wired into the event store abstraction layer, the schema changelog discipline begins, and the first breaking change to any event type is handled by a registered upcaster and a version increment. A backfill is unnecessary, since stored v1 events are read through the upcaster rather than rewritten.

**Wax v3+:** Optional tooling: a schema-version audit report that surfaces the distribution of versions across the event store, and validation utilities that confirm every non-current version has a registered upcaster chain reaching the current shape.

**Breaking change risk: LOW. The schema_version column and its place in the hash input ship in v1, before the hash specification freezes. Everything thereafter is additive: upcasters are added as event types evolve, and no stored event is ever rewritten.**

## Implications For Contributors

Additive changes are the default and require no version increment. A contributor adding a new optional key to an event type does nothing to the version, because older events lacking the key are read without transformation.

A breaking change to an event type, meaning a rename, a type change, a change of meaning, or a split into multiple types, requires both an increment of that event type's schema_version and a registered upcaster that transforms the prior version to the new one. A breaking change without an upcaster will not be accepted.

Stored events are never rewritten. No migration, backfill, or maintenance process may alter the payload, event_type, or schema_version of an event already written to core.event. Evolution is always read-time upcasting.

Upcasters are structural only. An upcaster may not decrypt, re-encrypt, or otherwise inspect the contents of an encryption envelope; it moves envelopes as opaque values.

Every breaking change is recorded in the schema changelog for the affected event type. The changelog entry is part of the contribution, not an afterthought.
