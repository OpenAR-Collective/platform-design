---
id: HIVE-0002
title: "Entity Matching, Golden Record, and Locale-Aware Identity Resolution"
status: Accepted
version: 1.0
area: hivear
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 2: Entity Matching, Golden Record, and Locale-Aware Identity Resolution

## Decision

HiveAR will include an entity matching engine that identifies duplicate person and business entity records across the database, merges them into a single canonical record while preserving all source data, and maintains a programmatic golden record view that surfaces the best available value for each field based on source reliability and data recency. Entity matching is locale-aware: the fields used for matching, the validation rules applied to those fields, and the scoring weights assigned to field matches are declared by Locale Modules rather than hardcoded in Wax. Merges are reversible with a full audit trail.

## The Problem Entity Matching Solves

Collection agencies routinely receive the same consumer from multiple creditor clients, across multiple debt types, and over multiple years. The same person may appear as John A. Smith on one account, J. Smith on another, and John Smith Jr. on a third. Without entity matching, these are treated as three separate people. The agency cannot see the full relationship between the consumer and the agency across all accounts. Compliance obligations that apply at the person level (such as cease and desist requests, bankruptcy notifications, and dispute records) may be applied to one account but not surfaced for the others.

Entity matching creates a single canonical person or business record to which all accounts are related, while preserving every source record intact. No source data is deleted or overwritten. The merge is a logical operation that links records together and designates one as the canonical survivor. Every attribute value from every source record remains in the database, associated with the canonical record through the merge history.

## Locale-Aware Matching

Because address fields, identity number fields, and name component fields live in Locale Module satellite tables rather than in the core schema, the entity matching engine cannot assume a fixed set of matching fields. An installation with only the US Locale Module has SSN, US address, and Western name components available for matching. An installation with both the US Locale Module and a Philippines Locale Module has two distinct address satellite schemas, two distinct identity satellite schemas, and potentially two distinct name component schemas. The matching engine must query whichever satellite tables are present for each record and apply the matching logic declared by the relevant Locale Module.

Each Locale Module declares its entity matching field registry as part of its module contract. The registry specifies which fields are available for matching, the matching algorithm appropriate for each field (exact match, fuzzy string match, normalized format match, or phonetic match), and the scoring weight assigned to a match on each field. The entity matching engine reads these declarations at runtime and applies them dynamically based on which Locale Modules are installed and which satellite tables a given record has data in.

When two records have data from the same Locale Module (both have US addresses, for example), the engine applies that Locale Module's matching weights. When two records have data from different Locale Modules, the engine applies a cross-locale matching strategy declared by the Locale Modules themselves if they choose to declare one, or falls back to matching only on core schema fields (display_name similarity) if no cross-locale strategy is declared.

## The Golden Record

After a merge, one record is designated the canonical survivor. All accounts that referenced the merged records are re-pointed to the canonical survivor. The canonical survivor is not a static choice made at merge time and forgotten. It is a dynamic view that re-evaluates the best available value for each field across all source records whenever the record is read.

The golden record view applies two scoring dimensions to determine the best value for each field. Source reliability is a configured weight assigned to each data source type: a value sourced from a credit bureau pull is weighted higher than a value self-reported by a consumer, which is weighted higher than a value inferred from a creditor file. Data recency weights more recent values higher than older ones within the same source reliability tier. The golden record view returns the highest-scoring non-null value for each field, with the source and timestamp of that value accessible for any field where the caller requests it.

The golden record is a read model, not a stored value. It is computed at query time from the merge history and the current values of all source satellite table records. This means the golden record automatically updates when a higher-reliability or more recent value arrives on any of the merged records, without any administrative action.

## Merge Operations and Audit Trail

Merges may be initiated manually by an authorized administrator or programmatically by the entity matching engine based on a confidence threshold. All merges are recorded in the event store with full enriched payload: the records merged, the merge initiator (human or engine), the confidence score if programmatically triggered, and the designated canonical survivor. The merge event is part of the immutable audit trail and is subject to the same hash chain integrity protections as all other events.

Merges are reversible through an unmerge operation. An unmerge separates previously merged records, restores all account associations to their pre-merge state, and records the unmerge in the event store. The full merge and unmerge history is preserved and queryable. An auditor can reconstruct the complete identity resolution history for any person record.

## Automatic Account Closure for Unrecognized Jurisdictions

The entity matching engine intersects with the Compliance Pack auto-close mechanism described in [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). When a new account arrives with a debtor address satellite record whose jurisdiction is not covered by any installed Compliance Pack, and the agency has configured the auto-close policy, the account is automatically closed before any collector activity begins. The auto-close fires at account creation time, before entity matching runs. If the account is later re-opened after the appropriate Compliance Pack is installed, entity matching runs at that point and any existing canonical person record is identified or created.

## What This Decision Does Not Specify

The specific matching algorithm (edit distance thresholds, phonetic matching libraries, machine learning-based similarity scoring), the golden record scoring formula, the merge confidence threshold configuration, the merge workflow UI, and the unmerge authorization requirements are all deferred to future architecture work. This decision establishes the architectural principles: locale-aware field discovery, dynamic golden record computation, reversible merges with full audit trail, and the Module contract mechanism for locale-specific matching declarations.

## Implementation Phasing

**HiveAR v1 (MVP):** Not implemented; schema prepared. Entity primary keys must be UUIDs from day one. The entity-to-account relationship table must support the canonical survivor pattern. The merge history table schema (ar.entity_merge) exists but remains empty, with columns for survivor, absorbed, merge_type, confidence_score, merged_by, merged_at.

**HiveAR v2:** Basic entity matching: exact-match on SSN, name + DOB + address. Manual merge and unmerge with full audit trail. Golden record view (simple: most recent non-null value per field, no scoring).

**HiveAR v3+:** Fuzzy and phonetic matching with confidence scoring. Locale-aware matching field registries. Automated matching with configurable thresholds. Full four-dimension scoring engine.

**Breaking change risk: MEDIUM.** UUID primary keys and the merge history schema are the critical v1 investments.

## Implications For Contributors

Locale Module authors must declare their entity matching field registry in the module contract manifest. A Locale Module that contributes address or identity satellite tables without a matching field registry declaration cannot participate in entity matching and will be flagged as incomplete.

The entity matching engine is a Wax component. Module authors may not implement alternative entity matching logic. They may influence matching behavior only through the declared matching field registry.

The golden record view is generated by Wax based on the installed Locale Modules' satellite table schemas. Module authors may declare source reliability weights for data their Module contributes, which the golden record view incorporates.

Merge and unmerge operations produce core.event entries. All entity matching activity is part of the tamper-evident audit trail.
