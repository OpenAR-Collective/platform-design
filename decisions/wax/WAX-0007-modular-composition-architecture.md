---
id: WAX-0007
title: "Modular Composition Architecture"
status: Accepted
version: 1.1
area: wax
date: 2026-10-05
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 7: Modular Composition Architecture

## Decision

The Wax will be built as a modular composition system. Wax is the base runtime and provides no standalone functionality. A deployed instance is assembled by selecting and combining modules from defined categories. Modules within each category are interchangeable and follow a published contract standard.

Modules govern structural and operational behavior: how the system is organized, how it handles data, and how workflows are executed. Compliance configuration, meaning the specific workflow rules, status codes, reason codes, and reference values that reflect an agency's interpretation of applicable law, is not delivered through Modules. It is delivered through Packs as described in [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md). This distinction is foundational and is addressed in detail below.

## Module Taxonomy

A complete deployable instance requires at least one selection from each required tier, plus any desired optional Modules.

| **Tier** | **Required** | **Examples** | **Notes** |
| --- | --- | --- | --- |
| Language Pack | Yes (1+) | English (US), English (UK), Spanish (US) | UI strings, date and number formats, locale defaults. No compliance content. |
| Region Pack | Yes (1+) | United States | Address structure, currency reference data (the list of currencies, minor-unit scales, and rounding conventions), phone number format, timezone handling. When the installed Region Packs name exactly one currency, that currency is the installation's default, as defined in Wax Design Decision 34. Structural and technical only. No compliance content. |
| Business Class Module | Yes (1+) | Healthcare, Auto, Bank Card, Student Loan | Workflow structure and data model differences by debt class. Operational, not prescriptive on compliance interpretation. |
| Debt Type Module | Yes (1+) | First Party, Third Party, Debt Purchase, Servicing | Operational model and ownership structure. Affects how accounts are managed, not how statutes are interpreted. |
| Treatment Module | No | Legal Collections, Outsourcing | Extends core workflow for specialized treatment paths. |
| Vendor Integration Module | No | Credit Bureau, Payment Processor, Skip Tracing | Third-party system connectors. |

## The Compliance Configuration Boundary

An earlier version of this taxonomy included State Modules as a required tier, with the intent of encoding state-specific compliance rules as installed system behavior. That approach has been deliberately rejected.

Compliance business logic is not architecture. Different agencies interpret the same statutes differently, and reasonably so. Legal obligations evolve as courts issue new interpretations and legislatures amend statutes. No module can guarantee that its encoded compliance logic reflects the current state of the law in any jurisdiction, or that it matches the specific legal advice an agency has received from its own counsel.

More fundamentally, encoding compliance rules as installed system behavior creates a liability the Collective should not accept. An agency that installs a module described as covering Texas debt collection law and then relies on it without independent legal review has been implicitly told the system has them covered. That claim cannot be made honestly.

The correct boundary is this: modules provide the structural capability for compliant workflows. Agencies configure those workflows in accordance with their own legal obligations, guided by their own counsel. The Collective supports this with thoughtfully designed Compliance Packs, clearly labeled as educational starting points, which agencies are free to adopt, adapt, or replace entirely.

> **WHAT MODULES DO VS. WHAT PACKS DO**
>
> Modules define how addresses are structured, how workflows are organized, how data flows between components, how third-party systems are integrated. Packs provide a starting point for compliance-oriented configuration, including suggested status codes, reason codes, and workflow reference values reflecting common industry practice. Modules are architectural decisions. Packs are educational reference configurations. Agencies own their compliance configuration. The Collective enables it. The Collective does not guarantee it.

## Design Rationale

The module taxonomy maps directly to the dimensions along which collection operations structurally vary. An agency doing third-party healthcare collections operates a materially different workflow than one doing first-party auto collections, and those structural differences are appropriate module concerns. A modular composition system handles this by assembling the right combination of structural behavior at deployment time, rather than through configuration flags and conditional logic that accumulates into unmaintainable complexity.

Removing compliance interpretation from the module taxonomy also creates a cleaner scope boundary for the Collective's vendor certification program. A certified vendor can be certified against specific module combinations with precisely defined scope, without any implication that certification confers compliance coverage.

## Module Contract Standard

All modules must conform to the published Wax Module Contract Standard. The standard defines how modules declare their dependencies, the commands they handle, the events they emit, the queries they expose, and the structural capabilities they provide. Modules that conform to the standard are interchangeable within their tier without modification to Wax or other modules.

The Module Contract Standard will be ratified by the technical steering committee before the first module is accepted into the repository.

## Cross-Module Compatibility

Modules within a tier may declare compatibility constraints. A Business Class module may declare that it requires specific events from a Debt Type module, or that it is incompatible with a specific Treatment Module. The Wax runtime will validate module compatibility at deployment time and surface conflicts before they reach production.

## Implementation Phasing

**Wax v1 (MVP):** Hardcoded composition. The platform ships as a single deployable application, not as Wax + pluggable modules. The US Locale Module, a basic third-party collections Business Class, and a generic debt-type configuration are baked into the v1 codebase. Code is organized along module boundaries internally (separate projects and namespaces for what will become modules), but there is no runtime module discovery, installation, or swapping. The critical discipline: v1 code must not cross module boundaries in ways the module contract would prohibit.

**Wax v2:** Module contract standard fully implemented. Module registry and installation pipeline. At least two to three alternative modules available.

**Wax v3+:** Community module marketplace. Module certification program. Module version compatibility matrix.

**Breaking change risk: MEDIUM.** Requires discipline in v1 to organize code along future module boundaries. If v1 code is a monolith with no internal structure, extracting modules in v2 becomes a rewrite.
