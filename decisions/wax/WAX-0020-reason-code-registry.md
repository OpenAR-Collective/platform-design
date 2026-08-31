---
id: WAX-0020
title: "Reason Code Registry"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 20: Reason Code Registry

## Decision

Reason codes are a defined subset of the reference value system established in [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md). They occupy a specific reference type in core.reference_type and are stored as UUID surrogate keys in core.reference_value with full i18n translation support. The registry is governed by a three-tier source model: canonical core codes maintained by the Collective, module-contributed codes shipped by module authors, and agency-defined codes created locally by individual deployments.

## What Reason Codes Are

A reason code is metadata attached to an event in core.event that answers the question of why a state change occurred. When a balance is adjusted, the reason code explains whether it was a payment, a creditor correction, a fee, or a dispute resolution. When a contact address is updated, the reason code identifies whether the change came from a debtor request, an NCOA match, a returned mail, or a skip trace result. Reason codes make the audit trail self-describing without requiring a reader to infer causation from surrounding context.

Reason codes are distinct from workflow events. A workflow event is a system signal that something happened, used to trigger automated processes. A reason code is a human-readable explanation of why it happened, stored as a field on the event record. The two concepts are related but serve different purposes. Workflow events are addressed in [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md).

## The Three-Tier Source Model

Every reason code row in core.reference_value carries an installed_by_module_fk and an is_system_defined flag. Together these identify the source tier of the code.

> **REASON CODE SOURCE TIERS**
>
> **Canonical core**: is_system_defined = true, installed_by_module_fk = null. Shipped by the Collective as part of the base platform. Covers universal state transitions meaningful in every deployment regardless of module combination: payment received, address corrected, name corrected, account assigned, account closed, dispute received, and similar. Added only through a reviewed pull request to the Collective repository. The bar for canonical status is whether the code represents a concept that is universal and unambiguous across all deployment configurations.
>
> **Module-contributed**: is_system_defined = true, installed_by_module_fk = [module reference]. Shipped by a module author as part of that module's seed data. Covers domain-specific events relevant to that module's scope. Follows the same reversibility rules as all module-contributed reference values: tagged to the module, removed with the module if uninstalled, checked for live references before deletion.
>
> **Agency-defined**: is_system_defined = false, installed_by_module_fk = null. Created by the agency through the administration interface. Covers operational needs specific to that deployment. Governed entirely by the agency. Not subject to Collective review. Not portable to other deployments.

## Canonical Code Governance

An agency or developer who believes a new reason code warrants canonical status submits a pull request to the Collective repository adding the reference value seed data and i18n translations for all supported locales. The technical steering committee reviews the proposal against the canonical bar: does this code represent a concept that is universal across all deployment configurations, or does it belong in a module namespace or an agency-specific definition?

The governance process is intentionally lightweight. The goal is not to make canonical additions difficult but to keep the canonical set meaningful. A large, undifferentiated canonical list degrades the utility of reason codes as an audit mechanism. Canonical codes should be the vocabulary that every Wax deployment shares, not a dumping ground for every possible event classification.

## Module Namespace Convention

Module-contributed reason codes are distinguishable from canonical codes by their installed_by_module_fk reference. The i18n translations for module-contributed codes must include a scope indicator in the label or description that identifies the contributing module, so that a compliance officer reviewing an audit trail can identify the source of an unfamiliar code without needing to query the module registry directly. This is a translation content convention, not a schema requirement.

## Agency-Defined Codes and Local Customization

An agency that wants reason codes specific to their operation creates them through the standard reference value administration UI. No pull request, no module, no special access is required. The creation workflow follows the process defined in Decision 8: the agency provides translations for all installed language packs before the code can be saved.

An agency that wants to contribute a locally created code to the canonical registry or to a module can do so by submitting a pull request. The code they created locally is effectively a proposal. If accepted, the Collective or the module author adds it to the appropriate Pack, and subsequent deployments will receive it automatically. The agency-defined version and the canonical version are different rows with different UUIDs; the agency would update their existing records to reference the canonical version if they choose to adopt it.

## Implementation Phasing

**Wax v1 (MVP):** Reason codes stored in the reference value system ([Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md)). Codes required on events, enforced by command handlers. A starter set ships with the Seed Pack. No namespace convention enforcement; all codes in a flat list.

**Wax v2:** Three-tier source model (canonical, module, agency). Namespace convention enforcement. Reason code governance tooling.

**Breaking change risk: LOW.** Reason codes are reference values. Adding governance metadata is additive.

## Implications For Contributors

Every event written to core.event that represents a state change with a meaningful cause must include a reason_code_fk. Events without a reason code where one is applicable are incomplete audit records.

Module authors must ship reason code seed data for every event type their module produces. Reason codes contributed by a module must include translations for all locales the module declares in its i18n compliance manifest.

Canonical reason code proposals submitted via pull request must include seed data and translations for all locales covered by Collective-maintained language packs at the time of submission.

Reason code labels in translations must be specific and unambiguous. A label like Updated is not acceptable. Address corrected per debtor request and Address updated via NCOA are both acceptable because they are self-describing in an audit context.
