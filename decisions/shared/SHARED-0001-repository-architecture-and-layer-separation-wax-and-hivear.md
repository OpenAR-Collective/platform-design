---
id: SHARED-0001
title: "Repository Architecture and Layer Separation (Wax and HiveAR)"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 1: Repository Architecture and Layer Separation (Wax and HiveAR)

## Decision

The platform is developed as two distinct codebases housed in separate repositories, each with independent version cadences. Wax is a domain-agnostic application framework. HiveAR is an accounts receivable platform built on top of Wax. Modules extend HiveAR with locale, business class, debt type, treatment, and integration capabilities. The OpenAR Collective Foundation owns and publishes both repositories. The platform product names Wax and HiveAR are distinct from the Foundation's organizational identity.

> **THE THREE-LAYER MODEL**
>
> **Wax** is the framework. It provides the event store, CQRS command/query pipeline, module system, workflow engine, internationalization infrastructure, security module, identity and access control, organizational model, configuration management, user-defined extensibility, and all other domain-agnostic infrastructure. Wax owns the core database schema and the i18n schema. A developer building a non-AR application on Wax would use these schemas and never touch HiveAR.
>
> **HiveAR** is the AR domain layer. It provides the entity data model (person, business, relationships), account lifecycle, account sets, demographic history, contact intelligence, entity matching, and the golden record. HiveAR owns the ar database schema. HiveAR is a privileged first-party consumer of Wax: it installs first, other AR modules declare dependencies on it, and it is treated as near-framework by the runtime even though it is not bundled with Wax.
>
> **Modules** extend HiveAR with interchangeable capabilities: Locale Modules provide region-specific schema and compliance structures, Business Class Modules provide industry-specific workflows, Treatment Modules add operational capabilities like legal collections. Modules own mod_* schemas.

## Schema Ownership

| **Schema** | **Owner** | **Contents** |
| --- | --- | --- |
| core | Wax | event, reference_type, reference_value, module_registry, workflow_definition, configuration, user, role, permission, organization |
| i18n | Wax | reference_value_translation, module_translation, resource_bundle |
| ar | HiveAR | account, entity, person, business, entity_relationship, entity_account_role, account_set, payment, payment_arrangement, dispute, communication, demographic history tables, entity_merge |
| mod_[name] | Modules | Module-specific tables: satellite extensions, read models, module-owned entities |

The core schema name was chosen because it reads naturally and communicates that these are the foundational infrastructure tables. A developer querying core.event immediately understands they are looking at the platform's central event store. HiveAR's ar schema follows the same principle: ar.account, ar.entity, ar.payment read cleanly as domain objects. The abbreviated domain prefix is a recommended pattern for Wax implementations. A hypothetical healthcare platform built on Wax might create an hc schema.

## The Stability Gradient

Wax is designed to stabilize early and change rarely. HiveAR evolves as the AR domain model matures. Modules change most frequently as the community contributes new capabilities. This gradient is a deliberate architectural property, not an observation.

The practical consequence is that the cost of a change increases as it moves down the stack. A module change affects one module. A HiveAR change may affect modules that depend on it. A Wax change potentially affects everything. Pull requests to the Wax repository should be rare after initial stabilization and should require strong justification. The community will enforce this norm socially through code review culture; the Foundation will formalize it through contribution governance as the project matures.

## Versioning

Wax and HiveAR maintain independent version numbers. Wax v1.0 and HiveAR v0.7 can coexist. HiveAR declares a minimum compatible Wax version in its dependency metadata. The version cadences are expected to diverge: Wax will reach stability earlier, and its version numbers will increment slowly. HiveAR will continue evolving through v1, v2, and v3 releases as the AR domain model expands. HiveAR releases may introduce new features (entity matching engines, scoring algorithms, new domain tables) without requiring any Wax version change.

## Naming And Brand Separation

The platform product names (Wax, HiveAR) are deliberately distinct from the Foundation's organizational identity (OpenAR Collective). This separation serves two purposes. First, it avoids conflating the community organization with its software products. The Foundation may produce other initiatives (educational resources, compliance guides, community programs) that are not software. Second, it allows Wax to stand as a genuinely domain-agnostic framework that developers outside the AR industry might adopt, without the accounts receivable signal embedded in the Foundation's name.

The naming draws from the bee and hive brand language: Wax is the building material of the comb, the structural foundation everything else is built from. HiveAR is the hive where the AR work happens. Modules are cells in the comb, each serving a specific function within the larger structure.

## Implications For Contributors

- Every design decision in this document is tagged with a Repository indicator: Wax, HiveAR, or Both. Contributors should direct pull requests to the correct repository.

Code that modifies Wax framework behavior (event store, module registry, workflow engine internals, security module, i18n infrastructure) goes to the Wax repository. Code that modifies AR domain behavior (entity model, account lifecycle, contact intelligence, matching algorithms) goes to the HiveAR repository.

Module authors work exclusively in the HiveAR ecosystem. Modules depend on HiveAR, which depends on Wax. A module author should never need to modify Wax to accomplish their goals. If a module author finds themselves blocked by a Wax limitation, that is a signal that Wax's extension surface needs improvement, not that the module should work around it.

The Wax repository will include its own documentation, contribution guidelines, and test suite independent of HiveAR. A developer evaluating Wax for a non-AR project should be able to understand and use it without any exposure to HiveAR concepts.
