---
id: WAX-0033
title: "Module Composition Model"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 33: Module Composition Model

## Decision

Wax modules will compose from a shared pool of primitive definitions rather than redefining the primitives they have in common. The machinery for this already exists across earlier decisions: the schema extension pattern from [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md), the bucket registry from [HiveAR Design Decision 5](../hivear/HIVE-0005-account-structure-and-balance-composition.md), the manifest-and-interface module contract from [Wax Design Decision 9](WAX-0009-module-contract-standard.md), and the module registry with its reference-value ownership and its seed package type from [Wax Design Decision 10](WAX-0010-module-registry.md). This decision states the composition model those pieces add up to. Common debt-domain primitives, buckets, role types, declared properties, and waterfall templates, ship once in a foundational seed package and are referenced by a module's manifest by key, never cloned into the module. A module also declares what it is compatible with, so an eligibility check can confirm a combination of module, contract type, locale, and packs before it deploys. This decision also adds contract_type to the module type classifier from [Wax Design Decision 10](WAX-0010-module-registry.md).

## Composition Over Redefinition

A module is, in the main, a declarative selection. [Wax Design Decision 9](WAX-0009-module-contract-standard.md) already makes a module a manifest paired with a behavioral interface, and [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md) already forbids a module from copying or altering the core schema, extending only through its own satellite tables. The composition model carries that discipline down to the primitives a module uses: it does not redefine the principal bucket or the debtor role that a dozen other modules also use, it references the single shared definition. Most of a module is therefore a manifest that points at shared definitions and configures them, which is why a module reads much like a configuration or a reference pack rather than a body of code. The small portion that is behavior is implemented once as a shared component and invoked through the module's interface, and module-specific code is reserved for behavior that is truly its own.

## The Shared Primitive Seed Package

The common primitives live in a foundational seed package, the seed_package module type established in [Wax Design Decision 10](WAX-0010-module-registry.md). The seed package contributes the shared bucket definitions, role types, declared properties, and waterfall templates that debt-domain modules draw on, each as a single keyed definition. A module's manifest references these by key and declares a dependency on the seed package, so the definition exists in one place and its ownership stays traceable through the installed-by-module reference from [Wax Design Decision 10](WAX-0010-module-registry.md). A module that needs a primitive no seed package provides contributes its own in its own namespace, exactly as it contributes subject-matter structure. Nothing is cloned, because nothing is copied: a shared primitive is defined once and referred to from everywhere it is used.

## Compatibility and Eligibility

Primitives and modules carry compatibility metadata, building on the dependency declarations the manifest already supports under [Wax Design Decision 9](WAX-0009-module-contract-standard.md). A primitive may declare the contexts it suits, and a module declares the contract types, locales, and packs it is built for. Before a configuration deploys, an eligibility check confirms it is coherent, that the module, its contract type, the installed locale, and the installed packs fit together, and it refuses or warns on a combination that does not. An incoherent deployment becomes a caught error rather than a runtime surprise, and a module's intended envelope is documented for the administrator assembling a configuration.

## The contract_type Module Type

[Wax Design Decision 10](WAX-0010-module-registry.md) fixes the module type classifier and includes no value for the contract relationship, yet contract type, servicing, third-party contingency, and purchase, is a first-class module concern: the debt-purchase module already exists, and the contingency module follows. This decision adds contract_type to the classifier. It is distinct from debt_type, which classifies what the debt is, and from treatment, which is a way of working an account; contract_type is the ownership-and-relationship model under which a debt is held and billed. The classifier remains platform-fixed and not extensible by module authors, so this is a platform amendment rather than a module extension.

## Implementation Phasing

**Wax v1 (MVP):** The composition model as the governing discipline: shared primitives defined once and referenced by key, modules as manifests that select and configure them, and the contract_type classifier value recognized. The seed package and its primitives ship in code in v1, consistent with Wax Design Decisions 4 and 10, since dynamic module installation is itself a v2 capability.

**Wax v2:** Compatibility metadata and the eligibility check enforced through the formalized manifest and the module installation pipeline.

**Wax v3+:** Richer compatibility expression and assembly tooling as the module ecosystem grows.

**Breaking change risk: LOW. The model names a discipline the existing schema, registry, and contract decisions already support, and adding contract_type to the classifier is additive. Nothing already built changes shape.**

**Confidence: HIGH. The model is a synthesis of decisions already made and reflects the way shared definitions and module manifests were always meant to combine.**

## Implications For Contributors

Reference shared primitives, do not redefine them. A primitive a seed package already provides, a common bucket, role, or property, is referenced by key from the manifest, never copied into the module.

A module is mostly a manifest. Most of a module is declarative selection and configuration of shared primitives; the behavioral portion is a shared component invoked through the interface, and bespoke code is the exception.

Declare compatibility. A module declares the contract types, locales, and packs it is built for, so the eligibility check can keep incoherent configurations from deploying.

contract_type is a recognized module type. Contract-type modules such as contingency, debt purchase, and servicing register under it, not under debt_type or treatment.
