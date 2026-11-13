---
id: HIVE-0014
title: "Collections Module Types and the Seed Package"
status: Proposed
version: 0.1
area: hivear
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 14: Collections Module Types and the Seed Package

## Decision

HiveAR will define the module types that belong to collections and the content of the seed package that holds the shared collections primitives, which [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md) and [Wax Design Decision 33](../wax/WAX-0033-module-composition-model.md) defined until this decision moved them out of the framework. The collections module types are the business class module, the debt-type module, the contract-type module, and the treatment module. Each implements the full module contract of [Wax Design Decision 9](../wax/WAX-0009-module-contract-standard.md), registers under its own value in the module type classifier of [Wax Design Decision 10](../wax/WAX-0010-module-registry.md), and composes from shared primitives by key under the module composition model of Wax Design Decision 33. HiveAR's seed package contributes the shared bucket definitions, role types, declared properties, and waterfall templates that collections modules reference by key, each defined once. Wax keeps the generic mechanics: the Module, Pack, and Bundle constructs; the Locale Module and the Vendor Integration Module; the Pack types, including the seed package that a domain layer fills; and the rule that a domain layer built on Wax defines the module types of its own domain.

## Why These Belong to HiveAR

Wax is the domain-agnostic framework, and HiveAR is the collections domain built on it, as [Shared Design Decision 1](../shared/SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md) provides. A business class, a debt type, a contract type, a treatment, a balance bucket, a debt role, and a waterfall are collections concepts, so a Wax decision that defines them puts collections vocabulary in the framework, and another domain built on Wax would inherit types it has no use for. This decision moves the definitions to HiveAR and does not change what they mean. A Wax decision may still use a collections example where an example helps, because an example defines nothing.

## The Module Types

Each collections module type implements the full module contract. The type determines what kind of capability a module contributes and which contract declarations apply.

> **COLLECTIONS MODULE TYPES**
>
> **Business class module**: contributes the schema, workflow patterns, and operational configuration for a business vertical such as healthcare, auto lending, student loans, or utilities, and defines the debt types and required fields relevant to that vertical. It is operational and carries no compliance content, which belongs to the Compliance Packs of Wax Design Decision 8.
>
> **Debt-type module**: contributes a specific debt classification within a business class, with its buckets, role types, declared properties, and subject-matter structure, as [HiveAR Design Decision 9](HIVE-0009-debt-type-structure-extension.md) describes, together with its field requirements, validation rules, and default workflow patterns. It affects what a debt carries, not how a statute is interpreted.
>
> **Contract-type module**: contributes the ownership and relationship model under which a debt is held and billed, such as servicing, third-party contingency, or purchase, the contract types of [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md). It affects how debts are managed, not how a statute is interpreted.
>
> **Treatment module**: contributes a treatment strategy type, meaning a defined approach to working a debt such as payment arrangements, settlement workflows, or legal referral, and extends the core workflow for that path.

A working HiveAR configuration needs at least one business class module, at least one debt-type module, and at least one contract-type module, while a treatment module is optional, as the module taxonomy of [Wax Design Decision 7](../wax/WAX-0007-modular-composition-architecture.md) required before this decision. Contract type is distinct from debt type, which classifies what a debt is, and from treatment, which is a way of working a debt.

## Registering the Types

The module type classifier of Wax Design Decision 10 carries a value for each collections module type: business_class, debt_type, contract_type, and treatment. HiveAR fixes these values as the domain layer, and module authors may not extend them, as Wax Design Decision 10 provides for the classifier as a whole. contract_type entered the classifier through Wax Design Decision 33 for the contract-type modules, such as contingency, debt purchase, and servicing, and this decision is now where it is defined. A contract-type module registers under contract_type, never under debt_type or treatment.

## The Seed Package

The seed package is the Pack type of Wax Design Decision 8 through which a domain layer ships the primitives that its modules share. HiveAR's seed package holds the collections primitives: the shared bucket definitions of HiveAR Design Decision 5, the debt role types of [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md) and HiveAR Design Decision 9, the standardized properties of HiveAR Design Decision 9, and the waterfall templates of [HiveAR Design Decision 7](HIVE-0007-payment-application-and-waterfall.md). Each is defined once under a key. A module's manifest references a primitive by key and declares a dependency on the seed package, so the definition exists in one place and its ownership stays traceable through the installed-by-module reference of Wax Design Decision 10. A module that needs a primitive the seed package does not provide contributes its own in its own namespace, exactly as it contributes subject-matter structure. The unsecured consumer debt module of [Unsecured Consumer Debt Module Design Decision 1](../modules/unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md) is the reference example, because almost all of it is a selection from the seed package.

## Compatibility

Under Wax Design Decision 33 a module declares what it is built for, and an eligibility check confirms a configuration before it deploys. A collections module also declares the contract types it supports, so the check can refuse a debt-type module on a contract type it was not built for. A business class module may declare that it requires specific events from a debt-type module, or that it cannot run beside a particular treatment module, and the Wax runtime validates those declarations at deployment as Wax Design Decision 7 provides for every module.

## Scope and Boundaries

This decision defines the collections module types and the content of HiveAR's seed package. The module contract, the registry and its classifier, the composition model, and the eligibility check stay in Wax Design Decisions 9, 10, and 33. Compliance rules stay in the Compliance Packs, and starting content that is not compliance stays in the Boilerplate Packs, under Wax Design Decision 8. What a debt-type module attaches to a debt is decided in HiveAR Design Decision 9, and the bucket registry is decided in HiveAR Design Decision 5.

## Implementation Phasing

**HiveAR v1 (MVP):** The four collections module types recognized and the code organized along their boundaries, with a basic third-party collections business class and a generic debt-type configuration built into the v1 codebase, as Wax Design Decision 7 provides for v1. The seed package and its primitives ship in code, because dynamic module installation is a v2 capability, as Wax Design Decision 33 provides.

**HiveAR v2:** The seed package installed through the Pack installation pipeline of Wax Design Decision 8, and the contract types that a module declares checked by the eligibility check of Wax Design Decision 33.

**HiveAR v3+:** Richer compatibility declarations as the module ecosystem grows.

**Breaking change risk: LOW.** The move changes where the definitions are recorded and not what they mean, and the classifier values stay the same.

## Implications For Contributors

A collections module registers under business_class, debt_type, contract_type, or treatment, and a contract-type module never registers under debt_type or treatment.

Reference shared collections primitives from the seed package by key. Never copy one into a module.

A new collections module type is added in this decision, never in a Wax decision. Wax provides only the mechanism that registers it.
