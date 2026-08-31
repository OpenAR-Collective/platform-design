---
id: WAX-0004
title: "Schema Architecture and Module Extension Pattern"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 4: Schema Architecture and Module Extension Pattern

## Decision

Wax will own a dedicated database schema named core. All entity tables (account, contact, payment, event, and related objects) reside in this schema. Wax controls these tables exclusively: their structure, their migration cycle, and their fields. No module may alter, extend, or add columns to any Wax-owned table.

Modules that require additional data fields extend Wax-owned entities through module-owned satellite tables in their own dedicated schemas. A satellite table carries a foreign key reference to the Wax-owned entity it extends and owns all fields it introduces. One-to-one satellite tables are used when the extension always applies to that entity type. One-to-many child tables are used when the module produces multiple related records per Wax-owned entity.

## Schema Namespace Convention

## Each module tier owns a distinct PostgreSQL schema namespace:

| **Schema** | **Owner** | **Examples** |
| --- | --- | --- |
| core | Wax | event, reference_type, reference_value, module_registry, workflow_definition, user, role, permission, organization |
| ar | HiveAR | account, entity, payment, payment_arrangement, account_set, dispute, communication, demographic history tables, entity_merge |
| healthcare | Healthcare Business Class module | account_extension, claim_detail |
| auto | Auto Business Class module | account_extension, vehicle |
| legal_collections | Legal Collections Treatment Module | account_extension, matter |
| us_region | United States Region Pack | state_configuration, address_validation |
| [module_name] | Any future module | Module-specific tables, owned entirely by that module |

## Why This Pattern

Independent release cycles are the primary benefit. Wax can publish a schema migration without coordinating with every module maintainer. A healthcare module update carries no risk of affecting the auto loan module. Each module owns its migration scripts and its schema namespace independently.

The core schema remains clean and auditable. A regulator, auditor, or new contributor can understand the core schema data model without encountering fields added by modules outside their scope of interest.

Contributor ownership is unambiguous. A developer building a new module has a clear contract: read from core schema tables as needed, consume and emit events per the module contract standard, and own everything within your schema namespace. Nothing outside that namespace is yours to modify.

## Implementation Phasing

**Wax v1 (MVP):** Ship the core schema (Wax-owned tables) and the ar schema (HiveAR-owned tables). Ship one hardcoded Locale Module's schema (US English) directly in core migrations rather than through the module installation pipeline. No dynamic module schema creation in v1; the US Locale Module's tables live in a mod_locale_us schema created by the core migration scripts. The schema naming convention is established even though dynamic provisioning is deferred.

**Wax v2:** Module installation pipeline creates schemas dynamically. Module-owned read model schemas.

**Wax v3+:** Module schema migration tooling, version management.

**Breaking change risk: LOW.** The naming convention is established in v1. Dynamic provisioning is additive.

## Implications For Contributors

Module satellite tables must declare a foreign key to the core schema table they extend. Orphaned extension records are a schema violation.

No module migration script may reference or alter any table in the core schema.

Module schemas are named after the module, in verbose snake_case, consistent with the platform naming conventions ([Wax Design Decision 5](WAX-0005-naming-conventions.md)).

Read models and projections (per [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md)) owned by a module reside in that module's schema.
