---
id: HIVE-0002
title: "Entity Matching, Golden Record, and Locale-Aware Identity Resolution"
status: Accepted
version: 2.0
area: hivear
date: 2026-09-01
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 2: Entity Matching, Golden Record, and Locale-Aware Identity Resolution

## Decision

HiveAR will include an entity matching engine that identifies duplicate person and business entity records across the database, merges them into a single canonical record while preserving all source data, and maintains a programmatic golden record view that surfaces the best available value for each attribute based on source reliability and data recency, where a multi-field attribute such as a name or an address is selected as a whole unit, never assembled from components of different source records. Entity matching is locale-aware: the fields used for matching, the validation rules applied to those fields, and the scoring weights assigned to field matches are declared by Locale Modules rather than hardcoded in Wax. Merges are reversible with a full audit trail.

## The Problem Entity Matching Solves

Collection agencies routinely receive the same consumer from multiple creditor clients, across multiple debt types, and over multiple years. The same person may appear as John A. Smith on one account, J. Smith on another, and John Smith Jr. on a third. Without entity matching, these are treated as three separate people. The agency cannot see the full relationship between the consumer and the agency across all accounts. Compliance obligations that apply at the person level (such as cease and desist requests, bankruptcy notifications, and dispute records) may be applied to one account but not surfaced for the others.

Entity matching creates a single canonical person or business record to which all accounts are related, while preserving every source record intact. No source data is deleted or overwritten. The merge is a logical operation that links records together and designates one as the canonical survivor. Every attribute value from every source record remains in the database, associated with the canonical record through the merge history.

## Locale-Aware Matching

Because address fields, identity number fields, and name component fields live in Locale Module satellite tables rather than in the core schema, the entity matching engine cannot assume a fixed set of matching fields. An installation with only the US Locale Module has SSN, US address, and Western name components available for matching. An installation with both the US Locale Module and a Philippines Locale Module has two distinct address satellite schemas, two distinct identity satellite schemas, and potentially two distinct name component schemas. The matching engine must query whichever satellite tables are present for each record and apply the matching logic declared by the relevant Locale Module.

Each Locale Module declares its entity matching field registry as part of its module contract. The registry specifies which fields are available for matching, the matching algorithm appropriate for each field (exact match, fuzzy string match, normalized format match, or phonetic match), and the scoring weight assigned to a match on each field. The entity matching engine reads these declarations at runtime and applies them dynamically based on which Locale Modules are installed and which satellite tables a given record has data in.

When two records have data from the same Locale Module (both have US addresses, for example), the engine applies that Locale Module's matching weights. When two records have data from different Locale Modules, the engine applies a cross-locale matching strategy declared by the Locale Modules themselves if they choose to declare one, or falls back to matching only on core schema fields (display_name similarity) if no cross-locale strategy is declared.

## The Golden Record

After a merge, one record is designated the canonical survivor. All accounts that referenced the merged records are re-pointed to the canonical survivor. The canonical survivor is not a static choice made at merge time and forgotten. It is a dynamic view that re-evaluates the best available value for each field across all source records whenever the record is read.

The golden record view applies two scoring dimensions to determine the best value for each attribute. Source reliability is a configured weight assigned to each data source type: a value sourced from a credit bureau pull is weighted higher than a value self-reported by a consumer, which is weighted higher than a value inferred from a creditor file. Data recency weights more recent values higher than older ones within the same source reliability tier. A multi-field attribute such as a name or an address is scored and selected as a single unit; the view never assembles an attribute from components of different source records. The golden record view returns the highest-scoring non-null value for each attribute, with the source and timestamp of that value accessible for any attribute where the caller requests it.

The golden record is a read model, not a stored value. It is computed at query time from the merge history and the current values of all source satellite table records. This means the golden record automatically updates when a higher-reliability or more recent value arrives on any of the merged records, without any administrative action.

## Merge Operations and Audit Trail

Merges may be initiated manually by an authorized administrator or programmatically by the entity matching engine based on a confidence threshold. All merges are recorded in the event store with full enriched payload: the records merged, the merge initiator (human or engine), the confidence score if programmatically triggered, and the designated canonical survivor. The merge event is part of the immutable audit trail and is subject to the same hash chain integrity protections as all other events.

Merges are reversible through an unmerge operation. An unmerge separates previously merged records, restores all account associations to their pre-merge state, and records the unmerge in the event store. The full merge and unmerge history is preserved and queryable. An auditor can reconstruct the complete identity resolution history for any person record.

## Worked Example

The mechanics above read most concretely as one consumer's records moving through the system. The scoring weights and thresholds in this example are illustrative only; the actual formula, thresholds, and configuration are deferred, as stated in What This Decision Does Not Specify.

An agency running the US Locale Module holds a 2023 credit card placement for John A. Smith of 414 Birch Street, Dayton, Ohio, with a full SSN and a date of birth from the creditor file. A 2025 medical placement arrives for J. Smith at 78 Corridor Road, Beavercreek, Ohio, carrying the same SSN and no date of birth. Suppose the US Locale Module's matching field registry declares an exact SSN match at weight 60, a phonetic name match at weight 15, an exact date of birth match at weight 15, and a normalized address match at weight 10, with programmatic merges configured to fire at a confidence of 65. The new record scores 60 on the SSN and a partial name score on J. Smith against John A. Smith, clearing the threshold: the engine merges the two records programmatically, designates the 2023 record the canonical survivor, and writes the merge event with its confidence score to the event store.

A third placement then arrives for John Smith Jr. at the same Birch Street address, with no SSN supplied by the creditor. Name and address alone score 25, far below the programmatic threshold, so no automatic merge occurs. An administrator reviewing the accounts later merges the records manually, and the merge event records the human initiator. Months afterward a dispute reveals that John Smith Jr. is the original debtor's adult son with his own obligation. The administrator unmerges the record: the son's record and his account associations are restored exactly as they stood before the merge, and both the merge and the unmerge remain permanently in the audit trail. The mistake is recoverable precisely because the merge was a logical link rather than a destructive rewrite.

The golden record view composes the canonical record attribute by attribute, not record by record, and it selects each attribute as a whole unit. A multi-field attribute travels together: the view picks the best complete address from among the addresses on file, never the street from one address with the apartment number from another, and it evaluates names the same way, as complete units rather than component fields. Completeness is part of what the deferred scoring formula must weigh: a full name outranks a partial one, and a partial one outranks a bare initial, so the 2025 record's J. Smith does not displace John A. Smith merely by being newer, and the fuller name is retained. The addresses cut the other way. Both arrived in creditor files, the same source reliability tier, so recency decides, and the recency of a client-supplied value is judged by the client's own aging dates, the date of service or the charge-off date, rather than the date the file happened to be placed. The medical account's 2025 date of service makes Corridor Road the fresher address by two years, and the contact outcome history of [HiveAR Design Decision 3](HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md) corroborates the switch: repeated mailings to Birch Street with no successful contact demote it under the full scoring engine of the v3+ phasing. The resulting golden record is a composite no single source ever supplied: John A. Smith, the complete name from the 2023 record, at 78 Corridor Road, the whole address from the 2025 record. When a 2026 credit bureau pull lands on any of the merged records with a new address, the view shifts again without administrative action, because it is computed at read time across all source records.

Nothing in this sequence overwrites anything. The Dayton address, the bare-initial name, and every other source value remain in the database, associated with the canonical record through the merge history, each with its source and timestamp accessible for any attribute where the caller requests it. When a regulator asks what address the agency had on file when a 2023 notice went out, the answer is retrievable, and an auditor can replay the full identity resolution history for the consumer, merges, unmerge, and golden record inputs included.

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
