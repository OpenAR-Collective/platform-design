---
id: HIVE-0009
title: "Debt-Type Account Structure Extension"
status: Accepted
version: 1.0
area: hivear
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 9: Debt-Type Account Structure Extension

## Decision

HiveAR will let a debt-type module attach the subject-matter structure of its debt to the core account, while the core account itself ships no subject-matter structure of its own. The core account is the stable hub that carries who is involved, how much is owed, and how accounts are grouped, established in HiveAR Design Decisions 1, 5, and 4. What a debt is about, its service lines, its collateral, its itemized fees, varies completely by type and lives entirely in the debt-type module, attached through the same table, view, and registry machinery the platform already uses. A debt-type module also declares a small set of standardized properties about its debt, drawn from a Foundation-governed vocabulary, which other modules, the locale region packs in particular, read to apply rules without knowing the module by name. Account role types are an extensible registry, so a module contributes the roles its debt needs alongside its structure.

## The Core Account Is the Hub; Subject Matter Hangs Off It

Three of the account's four facets are already in the core and do not vary enough by business type to push outward. Who is involved is the entity model with its person and business subtypes and its account role types from [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md). How much is owed is the buckets and the three amount categories from [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md). How accounts are grouped is the set model from [HiveAR Design Decision 4](HIVE-0004-account-sets.md). The party side is polymorphic and the money side is bucket-driven, which already absorbs most of the variance that would otherwise surface here. The remaining facet, what the debt is about, is the one that varies by type, and it is the subject of this decision. Applying the stability gradient inside the account, the core hub ossifies while a module's subject-matter structure hangs off it and changes at module cadence. A debt-type module is therefore one package of buckets from [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md), role types from [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), subject-matter structure from this decision, and the declared properties below.

## The Core Ships No Subject-Matter Structure

Just as the core ships no balance bucket, it ships no subject-matter structure, because there is no universal shape to ship. Interest is meaningless on healthcare debt, collateral does not exist on a signature loan or a credit card, and utility and phone debt is dominated by fees that a mortgage deficiency does not have. Any field or sub-entity the core tried to provide would be wrong for some debt type, so the core provides none and hosts whatever a module brings. This is the founding inert-without-modules tenet applied to account structure: a configuration with no debt-type module and no agency-defined structure is not a working configuration.

## The Extension Mechanism

A debt-type module attaches subject-matter structure to the account in two forms: additional fields on the account, and whole sub-entities such as a set of service lines or a collateral record keyed to the account. Both are realized through the mechanisms the platform already has, the user-defined table machinery and the bucket registry pattern, rather than a new one invented here. Because they ride those mechanisms, module structure inherits row-level security, encryption of personal fields, internationalized labels, and the reporting view layer automatically, exactly as core data and agency-defined data do. A module's sub-entities are first-class queryable structures with generated views, so a healthcare module's service lines are reportable the moment the module is loaded, with no separate wiring. The account remains the hub the structure keys to, and nothing about a module's structure reaches into or alters the core account's own shape.

## Standardized Debt-Type Properties

Beyond structure, a debt-type module declares a small set of standardized properties describing the nature of its debt, drawn from a vocabulary the Foundation governs. The vocabulary covers properties such as regulatory nature, consumer versus commercial, secured versus unsecured, and interest-bearing or not. These properties are the cross-module read seam. Another module reads a debt's declared properties rather than testing for a specific module's identity, so a region pack decides whether consumer protections apply by reading the declared regulatory nature, never by hard-coding which debt-type module is the commercial one. Because the Foundation authors both the debt-type modules and the region packs, the property vocabulary stays coherent across them, and cross-module references resolve cleanly against a shared, governed set of terms rather than against guesses about another module's internals.

## Compliance Lives in the Locale Layer

Compliance rules are not part of a debt-type module and are not part of this decision. They live in the locality modules and region packs, the locale layer that a working configuration already requires, which is what keeps the platform internationalization-friendly. A region pack's rules read the account's debt type and the standardized properties declared above to apply the correct regime, so a United States region pack applies its consumer rules to consumer debt and withholds them from commercial debt by reading the declared regulatory nature. This decision defines the properties that compliance rules read; it does not define the rules. The actual regime, validation, and communication constraints belong to the region pack and to a separate compliance treatment.

## Account Role Types Are an Extensible Registry

The account role types from [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), which connect entities to an account as a debtor, a guarantor, a cosigner, and so on, are an extensible registry, the same pattern as the bucket registry and the reason code registry. A debt-type module contributes the role types its debt requires as part of its package, so a healthcare module can introduce a patient and a responsible party while a commercial module introduces a business obligor and a personal guarantor, without the core enumerating every role any debt type might ever need. The party-side variance you would expect to find here is therefore handled by extending this registry rather than by module-specific structure.

## Worked Examples

The framework reads most concretely against several debt types. A healthcare module attaches service lines, each carrying a date of service, a facility and provider, and payer and claim detail, as a sub-entity set keyed to the account, and declares its debt consumer and non-interest-bearing. An auto deficiency module attaches a collateral record for the vehicle, the repossession and sale, and the deficiency computation, and declares its debt consumer and, where applicable, secured. A utility or phone module attaches a fee-heavy structure reflecting the service premises and the final bill, with little collateral or interest. A signature loan or credit card module attaches no subject-matter structure at all, since there is nothing to itemize beyond the buckets, which demonstrates that the framework imposes nothing and that a debt type with no subject matter is fully served by the core hub plus its buckets and roles.

## Scope and Boundaries

This decision defines the extension mechanism, the standardized property vocabulary, and the extensibility of the account role registry. It does not define any single module's structure in full; the worked examples illustrate the framework rather than specify those modules. Compliance rules live in the locale layer and only read this decision's properties. The chain of title, the original and prior creditors behind a purchased account, is account lineage's concern and not subject-matter structure. The itemized charge detail and service line structure remains its own item as the first concrete realization of this framework: this decision shows healthcare service lines as a worked example, and the full healthcare and itemized-charge module specification, the complete field set and the service-line semantics, is its own later work.

## Implementation Phasing

**HiveAR v1 (MVP):** The extension mechanism by which a debt-type module attaches subject-matter fields and sub-entities to the core account through the existing table, view, and registry machinery, inheriting row-level security, encryption, internationalized labels, and reporting views. The standardized debt-type property vocabulary and the cross-module read seam. The account role registry as extensible. At least one debt-type module is required for a working install, consistent with [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md).

**HiveAR v2:** Expansion of the standardized property vocabulary as additional debt types and region packs reveal new cross-module needs. Richer module-provided structure as the debt-type module set grows.

**HiveAR v3+:** Further extension points as new debt types require them, all additive, since the core hub does not change to accommodate a new debt type.

**Breaking change risk: LOW. The mechanism reuses the platform's existing table, view, and registry machinery, and module structure is additive and isolated to the module. The element to get right at the foundation is the standardized property vocabulary, since region packs and other modules depend on its stability; it follows the same governed-registry discipline as buckets, reason codes, and role types, and the core account hub does not change when a debt type is added.**

## Implications For Contributors

The core ships no subject-matter structure. No field or sub-entity describing what a debt is about belongs in the core account. Subject matter is contributed by a debt-type module or defined by the agency, never baked into core.

Module structure rides the existing mechanisms. Subject-matter fields and sub-entities use the user-defined table and registry machinery, so they inherit row-level security, encryption, labels, and reporting views rather than re-implementing them.

Read declared properties, not module identity. Cross-module logic, region packs especially, keys off a debt's standardized declared properties from the governed vocabulary, never off a test for a specific module.

Compliance rules stay in the locale layer. A contributor must not place regulatory rules in a debt-type module or in the core; they belong to the region packs, which read this decision's properties.

Role types are registry entries. New entity-to-account roles are added to the role registry, not hard-coded, the same discipline as buckets and reason codes.
