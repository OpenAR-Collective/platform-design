---
id: WAX-0009
title: "Module Contract Standard"
status: Accepted
version: 1.1
area: wax
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 9: Module Contract Standard

## Decision

The Wax module contract standard will use a hybrid model: a manifest file for discovery, metadata, and dependency declarations, combined with a C# interface for runtime behavioral contracts. Each component serves a different purpose and the two are complementary. Together they define a complete, enforceable, and well-documented standard that any module author can implement.

## The Manifest File

Every module will ship with a manifest file in a defined JSON format. The manifest is a human-readable, machine-parseable declaration of everything about the module that Wax and tooling need to know before the module is loaded. It is the module's identity document.

The manifest is the right place for information that must be readable outside the application runtime: by administrators evaluating a module before installation, by certification reviewers assessing a module against the Collective's standards, by tooling that validates compatibility before deployment, and by the module registry at installation time.

> **MANIFEST FILE COVERS**
>
> **Module identity**: name (as a reference to i18n translations), version, author, Collective certification status.
>
> **Module type**: the tier in the module taxonomy (language_pack, region_pack, business_class, debt_type, treatment, vendor_integration, seed_package).
>
> **Schema namespace**: the PostgreSQL schema the module owns.
>
> **Dependency declarations**: other modules this module requires, with minimum version constraints.
>
> **Compatibility constraints**: module tiers or specific modules this module is incompatible with.
>
> **i18n compliance**: the locales for which translations are provided.
>
> **Supported regions**: the Region Packs the module is built for. A module that names a currency in code declares the Region Pack that supplies it, as defined in [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md). A module with no regional dependence declares no supported regions.
>
> **Capability flags**: a structured declaration of the commands, events, and query endpoints this module contributes, at a summary level suitable for tooling and certification review.
>
> **Legal info:** License and attribution information.

## The C# Interface

In addition to the manifest, every module must implement a defined C# interface. This is the runtime contract. Where the manifest declares what a module is and what it contains, the C# interface is what Wax calls at runtime to register the module's behavior, load its command handlers, subscribe its projections to the event stream, and wire its API endpoints into the routing layer.

The C# interface enforces the contract at compile time. A module that declares a command handler in its manifest but does not implement the corresponding interface method will not compile. This means the manifest and the interface stay in sync by construction rather than by convention.

> **C# INTERFACE COVERS**
>
> **Module registration**: the entry point Core calls to load the module into the composition system.
>
> **Command handler registration**: the set of command handlers the module contributes, keyed by command type.
>
> **Event subscription registration**: the projections and read model processors that subscribe to the event stream.
>
> **API endpoint registration**: the REST endpoints the module exposes, wired into the application's routing layer.
>
> **Migration execution**: the method Core calls to run the module's schema migrations during installation.
>
> **Uninstall execution**: the method Core calls to reverse the module's contributions during uninstall, in dependency order.

## Why Hybrid Rather Than Either Alone

A manifest alone would be sufficient for discovery and tooling but would leave behavioral registration entirely to convention. Modules could declare capabilities they do not implement, and Wax would have no compile-time guarantee that a declared command handler actually exists. Discoverability would be good but enforcement would be weak.

A C# interface alone would provide strong compile-time enforcement but would give tooling, certification reviewers, and administrators no human-readable window into a module's capabilities without running the code. The certification program in particular requires the ability to review a module's declared scope against a readable artifact, and the module directory requires structured metadata that can be queried without executing application code.

The hybrid model gives each component the job it is suited for. The manifest handles declaration, discovery, and review. The interface handles enforcement and runtime wiring. A module that conforms to both is correct by construction and reviewable by anyone.

## Relationship to Vendor Certification

The module contract standard is the technical foundation for the Platform Integration certification track. A certified module is one that has been reviewed against the published module contract specification, verified to implement the C# interface correctly, confirmed to follow naming conventions and schema ownership rules, and assessed for quality and security standards beyond bare technical compliance.

The contract standard is not the certification program. Any module that conforms to the technical standard is installable by any agency. Certification governs the Collective's own directory listing and endorsement. This distinction is deliberate and fundamental to the open-source model.

## What This Decision Does Not Specify

The detailed specification of the manifest schema, method signatures, validation tooling, linting rules, and module author documentation are covered in the Module Contract specification document.

## Implementation Phasing

**Wax v1 (MVP):** Internal convention only. No formal manifest file or C# interface validation at runtime. The v1 codebase follows module contract patterns informally: separate namespaces, no cross-boundary direct table access, extension points defined but not enforced.

**Wax v2:** Full implementation. Manifest file schema published. C# interface defined and enforced. Module validation tooling.

**Breaking change risk: LOW.** The contract is an interface definition. v1 code that respects the intended boundaries will conform when the interface is formalized.

## Implications For Contributors

No module will be accepted into the Collective's repository until the full module contract specification has been published and the module demonstrably conforms to it.

The manifest and the C# interface are both required. A module that implements one without the other does not meet the contract standard.

The manifest must be kept current with the implementation. A manifest that declares capabilities the module does not implement, or omits capabilities it does implement, is a contract violation.

A module declares the Region Packs it supports in its manifest, as it declares the locales it provides translations for. A module that names a currency in code and does not declare the Region Pack that supplies it is a contract violation.

A module that declares no supported regions is treated as region-neutral. The certification review checks such a module for violations of the currency, language, and other region and language pack requirements, and a module found to depend on any of them must declare the regions it supports or remove the dependence.

Module authors building against the platform before the full specification is published should follow the architectural principles in this document and expect that some implementation details will be clarified during Year 1.
