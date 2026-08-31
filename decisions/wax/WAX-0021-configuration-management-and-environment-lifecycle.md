---
id: WAX-0021
title: "Configuration Management and Environment Lifecycle"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 21: Configuration Management and Environment Lifecycle

## Decision

All user-configurable items are treated as versioned configuration with full change history. Configuration state can be exported and imported between environments. Wax ships with supported tooling for a development, test, staging, and production lifecycle including a PII redaction utility. User-defined windows (UDWs) are a supported platform capability for agency-defined views. A system-to-system promotion interface is a named future goal designed toward from the start.

## Versioned Configuration

Every user-configurable item is versioned. The scope of versioned configuration includes workflow definitions, UDT definitions, reference values and their translations, reason codes, RBAC role definitions, service account configurations, module activation settings, and any other items that govern platform behavior rather than operational data. Every change preserves the prior version, recording who made the change, when, and the full content before and after.

## Export and Import

Configuration state can be exported from an environment as a structured package and imported into another. The import process validates the package against the target environment's schema version and module configuration before applying any changes. Conflicts are surfaced for review before the import proceeds. The export/import mechanism is the foundation of the environment promotion workflow.

## Environment Lifecycle Tooling

HiveAR ships with supported patterns and tooling for a development, test, staging, and production lifecycle. Tooling includes environment configuration templates, a database seeding framework, and a PII redaction utility that produces a de-identified copy of a production database suitable for development and QA use.

## User-Defined Windows

User-defined windows (UDWs) are agency-designed GUI views that surface UDT fields, core or module-delivered fields, and calculated values in any combination. UDW definitions are versioned configuration items that participate in the full export and import model. The full UDW architecture, including the view designer specification, is covered in [Wax Design Decision 22](WAX-0022-user-defined-tables-and-user-defined-windows.md).

## Future Goal: System-to-System Promotion Interface

A future goal is a purpose-built system-to-system promotion interface where an administrator browses configuration items from a source instance, reviews a diff window, enters a mandatory comment, and applies the promotion with full audit history stored in both instances. This capability is documented as a named future goal so the export/import format is designed with it in mind from the start.

## Implementation Phasing

**Wax v1 (MVP):** System configuration stored in database tables (not config files). No versioned configuration snapshots. No export or import. No environment promotion tooling.

**Wax v2:** Configuration export and import (JSON format). Versioned configuration snapshots.

**Wax v3+:** Environment lifecycle tooling (dev to staging to production promotion). System-to-system promotion interface.

**Breaking change risk: NONE.** Lifecycle tooling is additive.

## Implications For Contributors

All user-configurable items contributed by modules must implement the configuration versioning interface so they participate correctly in the export/import and promotion model.

UDW definitions and all other organization-scoped configuration items must carry an organization_fk and support the export/import serialization format.
