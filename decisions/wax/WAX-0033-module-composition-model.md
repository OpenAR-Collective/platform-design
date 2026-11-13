---
id: WAX-0033
title: "Module Composition Model"
status: Accepted
version: 3.0
area: wax
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 33: Module Composition Model

## Decision

Wax modules will compose from a shared pool of primitive definitions rather than redefining the primitives they have in common. The machinery for this already exists across earlier decisions: the schema extension pattern from [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md), the manifest-and-interface module contract from [Wax Design Decision 9](WAX-0009-module-contract-standard.md), and the module registry with its reference-value ownership and its seed package type from [Wax Design Decision 10](WAX-0010-module-registry.md). This decision states the composition model those pieces add up to. The primitives that a domain layer's modules have in common ship once in a seed package and are referenced by a module's manifest by key, never cloned into the module, and the domain layer decides what they are: for HiveAR, the bucket definitions, role types, declared properties, and waterfall templates of [HiveAR Design Decision 14](../hivear/HIVE-0014-collections-module-types-and-the-seed-package.md). A module also declares what it is compatible with, so an eligibility check can confirm a combination of module, locale, packs, and the compatibility facts that its domain layer defines before it deploys.

## Composition Over Redefinition

A module is, in the main, a declarative selection. [Wax Design Decision 9](WAX-0009-module-contract-standard.md) already makes a module a manifest paired with a behavioral interface, and [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md) already forbids a module from copying or altering the core schema, extending only through its own satellite tables. The composition model carries that discipline down to the primitives a module uses: it does not redefine the principal bucket or the debtor role that a dozen other modules also use, it references the single shared definition. Most of a module is therefore a manifest that points at shared definitions and configures them, which is why a module reads much like a configuration or a Pack rather than a body of code. The small portion that is behavior is implemented once as a shared component and invoked through the module's interface, and module-specific code is reserved for behavior that is truly its own.

## The Seed Package

The common primitives live in a seed package, the seed_package Pack type that [Wax Design Decision 8](WAX-0008-extensibility-construct-nomenclature.md) and [Wax Design Decision 10](WAX-0010-module-registry.md) establish. A domain layer fills it with the primitives that its modules draw on, each as a single keyed definition, and HiveAR's are listed in HiveAR Design Decision 14. A module's manifest references these by key and declares a dependency on the seed package, so the definition exists in one place and its ownership stays traceable through the installed-by-module reference from [Wax Design Decision 10](WAX-0010-module-registry.md). A module that needs a primitive no seed package provides contributes its own in its own namespace, exactly as it contributes subject-matter structure. Nothing is cloned, because nothing is copied: a shared primitive is defined once and referred to from everywhere it is used.

## Compatibility and Eligibility

Primitives and modules carry compatibility metadata, building on the dependency declarations the manifest already supports under [Wax Design Decision 9](WAX-0009-module-contract-standard.md). A primitive may declare the contexts it suits, and a module declares the locales and packs it is built for, together with any compatibility facts that its domain layer defines, such as the contract types of HiveAR Design Decision 14. Before a configuration deploys, an eligibility check confirms it is coherent, that the module, the installed locale, the installed packs, and those facts fit together, and it refuses or warns on a combination that does not. An incoherent deployment becomes a caught error rather than a runtime surprise, and a module's intended envelope is documented for the administrator assembling a configuration.

## Domain Module Types

[Wax Design Decision 10](WAX-0010-module-registry.md) fixes the module type classifier, and a domain layer built on Wax adds a value for each module type that it defines. This decision added contract_type to the classifier in its first version, for HiveAR's contract-type modules. That value and HiveAR's other module types are now defined in HiveAR Design Decision 14, because they are collections concepts, and the classifier stays closed to module authors.

## Implementation Phasing

**Wax v1 (MVP):** The composition model as the governing discipline: shared primitives defined once and referenced by key, modules as manifests that select and configure them, and the classifier values of the domain layer recognized. The seed package and its primitives ship in code in v1, consistent with Wax Design Decisions 4 and 10, since dynamic module installation is itself a v2 capability.

**Wax v2:** Compatibility metadata and the eligibility check enforced through the formalized manifest and the module installation pipeline.

**Wax v3+:** Richer compatibility expression and assembly tooling as the module ecosystem grows.

**Breaking change risk: LOW. The model names a discipline the existing schema, registry, and contract decisions already support, and moving the domain's module types and seed package content to the domain's own decision changes no classifier value. Nothing already built changes shape.**

**Confidence: HIGH. The model is a synthesis of decisions already made and reflects the way shared definitions and module manifests were always meant to combine.**

## Implications For Contributors

Reference shared primitives, do not redefine them. A primitive a seed package already provides, a common bucket, role, or property, is referenced by key from the manifest, never copied into the module.

A module is mostly a manifest. Most of a module is declarative selection and configuration of shared primitives; the behavioral portion is a shared component invoked through the interface, and bespoke code is the exception.

Declare compatibility. A module declares the locales and packs it is built for, and the compatibility facts that its domain layer defines, so the eligibility check can keep incoherent configurations from deploying.

A domain layer defines its own module types. HiveAR's, contract_type among them, are in HiveAR Design Decision 14, and no Wax decision defines a domain module type.
