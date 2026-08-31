---
id: WAX-0016
title: "Data Access Architecture, Read Layer, and Direct Query Interface"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 16: Data Access Architecture, Read Layer, and Direct Query Interface

## Decision

No INSERT, UPDATE, or DELETE operations are permitted on the platform's database tables by any user, tool, or connection other than the application's own service credentials operating through the command handler path. The database is a read surface for everyone except the application itself. All read access is provided through a view layer that transparently decrypts PII fields and resolves i18n labels using SECURITY DEFINER functions, presenting a clean SQL interface to authorized callers without exposing key material or requiring awareness of the underlying encryption and translation architecture.

## The Write Surface: Application Only

All writes enter the system through command handlers as established in [Wax Design Decision 2](WAX-0002-cqrs-model.md). A command handler receives a command, validates it against current state, calls the WSM for any required encryption operations, produces an event, and writes the event and updated authoritative state table atomically through the application's dedicated service credentials. Those credentials are never distributed outside the application process.

No user account, no module, no BI tool, no administrative utility, and no direct database connection holds INSERT, UPDATE, or DELETE privileges on any HiveAR application table. This is enforced at the PostgreSQL role level, not by convention. A direct database connection made with any credential other than the application service account is physically incapable of writing to Wax tables. This design property means the entire discussion of transparent decryption, i18n resolution, and view architecture is exclusively a read concern. There is no write surface to protect at the database query level because no write surface exists there.

## The Read Layer: Views and SECURITY DEFINER Functions

Read access is provided through a view layer built on top of the authoritative state tables and read model tables. Every entity exposed for querying has a corresponding view. The view is the public SQL interface. The underlying table is an implementation detail that is not directly accessible to any read user or tool.

PII fields in the underlying tables are stored as ciphertext using pgcrypto column-level encryption as established in [Wax Design Decision 14](WAX-0014-encryption-and-data-protection.md). The corresponding view column calls a SECURITY DEFINER function to decrypt the value before returning it. SECURITY DEFINER is a PostgreSQL mechanism that executes the function with the privileges of the function's owner rather than the calling user. The function owner has SELECT permission on the key table. The calling user does not. The key material is therefore only accessible through the function's controlled code path, enforced by PostgreSQL's own permission system rather than by application convention.

The result is that a developer, a reporting user, or a BI tool can write SELECT ssn FROM person_view and receive the plaintext social security number for any row their role permits them to see, without any knowledge of encryption, without any session variable setup, and without any application code involvement. The decryption is invisible.

> **SECURITY DEFINER FUNCTION PROPERTIES**
>
> The function is owned by a dedicated database role that holds SELECT on the key table. No other role has direct key table access. The function accepts the ciphertext column value and the subject primary key as parameters. It retrieves the subject's encryption key from the key table, decrypts the ciphertext, and returns the plaintext. If the subject's key has been destroyed (retention-triggered erasure per [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md)), the function returns a typed null with a metadata indicator distinguishing a destroyed-key null from a legitimately null field. Application code and BI tools can detect and handle this condition explicitly. The function is called within the view definition. The view consumer never calls the function directly. The decryption is an implementation detail of the view. SECURITY DEFINER functions execute with elevated privileges only for the specific operations they perform. They do not grant the calling user any other elevated access.

## i18n Label Resolution in Views

Reference value fields in the underlying tables store UUID surrogate keys as established in [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md). The corresponding view column calls a locale-resolution SECURITY DEFINER function that joins through the i18n translation tables and returns the translated label for the calling user's configured locale. The user's locale is derived from their user profile row in core.user, which the function reads using the session's authenticated user identifier. No session variable setup is required.

The locale resolution follows the three-level fallback chain established in Wax Design Decision 11: the user's configured locale first, the installation's system default second, and the installation's base locale third. A developer writing SELECT status_label FROM account_view receives the correctly translated status label for their locale without any awareness of the i18n architecture. The translation is invisible.

The view for a given entity composes multiple SECURITY DEFINER function calls: one per PII field for decryption, one per reference value field for i18n label resolution. The view definition is generated automatically based on the entity's registered field schema. Module authors and UDT definitions supply the field metadata. The view generator produces the corresponding view definition. Developers never write view definitions that call decryption or translation functions manually.

## Row-Level Security as the Authorization Boundary

SECURITY DEFINER functions handle the column-level concern: decrypting a field value for an authorized caller. Row-level security handles the row-level concern: determining which records a given principal is permitted to see at all. The two mechanisms are complementary and independent.

RLS policies on the underlying tables and views enforce that a principal only sees rows within their authorized scope: their organization, their assigned accounts, their permitted business classes. The WSM's SECURITY DEFINER functions fire only for rows that RLS has already permitted. A principal cannot retrieve the decrypted SSN for a record they are not authorized to see, because RLS prevents the record from appearing in their result set before the decryption function is ever called.

This provides defense in depth. A bug in the application layer that incorrectly grants a user access to a record they should not see would still need to pass through RLS before that record appears in any query result. RLS is enforced by the database, not by the application, and cannot be bypassed by any query the principal submits directly to the database.

## WSM Table Isolation

The WSM's key store, the key audit log, and the checkpoint token table are owned exclusively by the WSM's dedicated database credential. No other role, including the application service account, holds any privilege on these tables. The application service account interacts with these tables only through the WSM's published interface, which calls into the WSM process rather than executing SQL directly.

This means a direct database connection made with any credential, including the application service account, cannot read, write, or modify WSM internal tables. The isolation is absolute and enforced entirely at the PostgreSQL privilege level.

## Read Model Tables and Projection Workers

Read model tables are populated by projection workers that subscribe to the event stream. A projection worker receives an event, extracts the relevant field values, and writes a denormalized read model row optimized for a specific query pattern. PII fields written to read model tables are encrypted by the projection worker through the WSM interface before the row is committed. The read model table therefore also stores ciphertext for PII fields. The corresponding read model view applies the same SECURITY DEFINER decryption pattern as the authoritative entity views. From the query consumer's perspective, querying a read model view and querying an entity view are identical experiences.

## UDT-Generated Views

When an agency creates a user-defined table, the view generator produces a corresponding UDT view. For UDT fields marked as PII at definition time, the generated view includes the appropriate SECURITY DEFINER decryption call. For UDT fields backed by reference values, the generated view includes the appropriate i18n label resolution call. The UDT view presents the same transparent query interface as all other entity views. If the PII classification of a UDT field is changed after data has been written, the view must be regenerated and existing ciphertext must be migrated. This is a break-glass-level operation requiring administrative authorization.

## BI Tools, Reporting Tools, and Direct SQL Access

A BI tool, a reporting tool, or any direct SQL client connecting to the platform's database with valid read credentials can query the view layer and receive decrypted, translated data using standard SQL. No special client configuration is required beyond a valid database connection. The tool does not need to know about encryption, i18n, or the WSM. It connects, authenticates, queries views, and receives clean data.

The authenticated database credential determines which views the tool can access and which rows within those views RLS permits. A reporting user with a collector role sees only the accounts within their assigned scope, with all PII decrypted and all labels translated. A supervisor role sees a broader scope. An administrative reporting role may see the full organization scope. The authorization model is the same for direct SQL clients as for the API: roles, organization scope, and RLS, all enforced by the database.

Direct SQL clients cannot write to any table. They cannot access WSM internal tables. They cannot bypass RLS. They cannot call decryption functions directly except through the view definitions that expose them. Their access is read-only, scoped by their role, and transparent with respect to the underlying encryption and i18n architecture.

## What This Means for the Audit Trail

The core.event table and the key audit log are not exposed through the standard view layer for general querying. Direct access to the event store is restricted to the compliance audit query interface described in [Wax Design Decision 2](WAX-0002-cqrs-model.md), which is exposed through a specific API endpoint available only to roles granted audit access. This preserves the integrity of the audit trail: a reporting user cannot inadvertently modify their perception of the event history by querying it through a BI tool, because the event tables are not in their accessible schema.

A designated compliance auditor role may be granted read access to the event store view, which presents the event payload with PII fields decrypted through the same SECURITY DEFINER mechanism. The event hash and prior_event_hash fields are always returned in their raw form, allowing an auditor to independently verify the hash chain without relying on the application's verification tooling.

## Implementation Phasing

**Wax v1 (MVP):** Application-only write surface (all writes through command handlers). Basic database views for common read patterns. No SECURITY DEFINER functions (no PII encryption to decrypt). No RLS enforcement. BI tool access guidance deferred.

**Wax v2:** SECURITY DEFINER functions for PII decryption and i18n label resolution. RLS policies. BI tool connection guidance.

**Wax v3+:** UDT-generated views. Full read layer with all security boundaries enforced at the database level.

**Breaking change risk: LOW.** Views and functions are additive. The write-surface discipline (all writes through commands) must be in place from v1.

## Implications For Contributors

Module authors must not grant INSERT, UPDATE, or DELETE privileges on module-owned tables to any role other than the application service account. All writes to module tables go through the command handler path.

Every entity or read model that module authors expose for querying must have a corresponding view. Direct table access for read users is not permitted. The view is the public SQL contract.

Module authors must register PII fields in the field registry so the view generator can produce the correct SECURITY DEFINER decryption calls. A PII field exposed through a view without decryption is a data exposure defect.

Module authors must register reference value fields in the field registry so the view generator can produce the correct i18n label resolution calls. A reference value UUID exposed directly in a view without resolution is a usability defect.

SECURITY DEFINER functions are owned and maintained by Wax. Module authors do not write SECURITY DEFINER functions. They declare their field types through the module contract and the view generator handles the rest.

The view generator is a Wax component. Module authors trigger view regeneration through the module installation and update lifecycle, not by writing SQL directly.
