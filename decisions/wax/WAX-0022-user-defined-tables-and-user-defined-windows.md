---
id: WAX-0022
title: "User-Defined Tables and User-Defined Windows"
status: Accepted
version: 1.1
area: wax
date: 2026-10-05
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 22: User-Defined Tables and User-Defined Windows

## Decision

Wax will support two distinct user-extensibility constructs. User-defined tables (UDTs) are agency-defined data storage structures that extend the platform data model without code changes or module development. User-defined windows (UDWs) are agency-designed GUI views that surface UDT fields, core or module-delivered fields, and calculated values in any combination. UDTs and UDWs are separate design artifacts: creating a UDT does not automatically create a UDW.

## User-Defined Tables

A UDT is defined through a schema builder UI. The agency names the table, selects its relationship type, selects its parent entity if applicable, and defines its fields. The platform generates the corresponding table in the organization's schema namespace, registers it in the UDT registry, and registers per-UDT event types in the workflow event registry.

> **UDT CORE SCHEMA**
>
> **udt_pk**: UUID, auto-generated surrogate primary key.
>
> **Short code and descriptive name**: follow the full i18n architecture. No English stored in the core UDT registry table. Translations are required for all installed language packs before a UDT definition can be saved.
>
> **parent_entity_type**: the registered entity type this UDT is attached to. Null for unattached UDTs.
>
> **parent_entity_fk**: the primary key of the specific parent record. Null for unattached UDTs.
>
> **relationship_type**: one_to_one or many_to_one.
>
> **created_at**: UTC timestamp, auto-set on insert, immutable.
>
> **updated_at**: UTC timestamp, auto-updated on every write.
>
> **created_by_user_fk and updated_by_user_fk**: actor references.

## Relationship Types

A one-to-one UDT has exactly one record per parent entity record, extending the parent with additional fields. A many-to-one UDT stores zero or more records per parent, modeling repeating structured data. An unattached UDT has no parent_entity_fk and is a system-wide table for agency-maintained reference data or operational tracking not affiliated with any specific entity.

## Field Types

Initial supported field types include text (short and long), integer, decimal, money, boolean, date, datetime, and reference value. A date field is a civil date with no zone, and a datetime field is an instant stored in UTC, as defined in [Wax Design Decision 12](WAX-0012-date-time-timezone-and-freeform-note-language.md). A money field carries its currency, as defined in [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md). It takes the installation's default currency when one exists, so the schema builder asks for a currency only in an installation with more than one. A decimal field is for quantities that are not money. File attachment is noted as a future addition pending the document storage architecture decision. Foreign key lookups to other entities are intentionally excluded: UDTs are satellite data structures, not structural extensions of the relational schema.

## i18n Compliance for UDT Names and Event Labels

UDT short codes and descriptive names follow the full i18n architecture: no English in the core table, translations required for all installed language packs. Each UDT generates two automatically registered event types: [udt_pk].record_created and [udt_pk].record_changed. The event type identifier used for routing is the UDT's UUID concatenated with the event category, never human-readable text. Display labels shown in the workflow designer are resolved through the i18n system. This separation of routing identifiers from display labels is a platform-wide rule applying to all constructs that serve both purposes.

## UDT Events and Workflow Integration

When a UDT record is created or changed, the corresponding event fires through the normal event pipeline and is written to core.event with a full enriched payload. The event's key ring carries the UDT record's own PK and, for attached UDTs, the parent entity's PK. Per-UDT event types mean workflow definitions subscribe to specific UDT events rather than a generic UDT-changed event, enabling field-level condition evaluation using pre_state and post_state key ring comparison.

## User-Defined Windows

A UDW is a designed view artifact separate from any UDT. The agency builds a UDW through a view designer composing any combination of UDT fields, core or module-delivered entity fields, and calculated values. UDW definitions are versioned configuration items subject to the export/import and promotion model. The full UDW view designer specification including supported layout types and calculation expression support is deferred to future architecture work.

## Implementation Phasing

**Wax v1 (MVP):** Not implemented. Reserve the udt_ table prefix in naming conventions. The event store schema must not assume a fixed set of aggregate types: aggregate_type is a string, not an enum, allowing UDT-originated events in v2 without schema changes.

**Wax v2:** Basic UDT: define custom tables with typed fields, link to accounts and entities. UDT events flow through the event store. Simple generated forms.

**Wax v3+:** Full UDT: calculation fields, complex relationships, schema builder UI. User-Defined Windows. UDT workflow integration.

**Breaking change risk: LOW if naming conventions and aggregate_type flexibility are preserved in v1.**

## Implications For Contributors

UDT event type identifiers use UUID-derived routing keys, never English or other human-readable strings. Display labels are resolved through i18n. This pattern must be followed consistently by all platform constructs that serve both routing and display purposes.

Module authors who introduce new entity types eligible as UDT parents must register those entity types in the platform entity registry as part of their module contract.

UDT tables are created in the organization's schema namespace. Module authors may not assume any specific UDT schema in their own code.
