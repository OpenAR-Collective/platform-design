---
id: WAX-0008
title: "Extensibility Construct Nomenclature"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 8: Extensibility Construct Nomenclature

## Decision

Wax's extensibility system uses two top-level constructs distinguished by a single principle: Modules contain code; Packs contain data. A Module implements the module contract standard from [Wax Design Decision 9](WAX-0009-module-contract-standard.md). A Pack installs structured data through the seeding framework. A Bundle is a named, versioned grouping of one or more Modules and zero or more Packs that are designed to be installed together and collectively deliver a coherent capability. All extensibility constructs are either a Module, a Pack, or a Bundle.

## The Fundamental Distinction

A Module contributes code: command handlers, event subscriptions, API endpoints, UI components, schema namespaces, validation logic, and action types. It implements the full module contract: a manifest file and a C# interface. It has a build process, a versioned binary, and a schema namespace it owns. It is subject to the module registry, the installation and uninstall lifecycle, and Collective certification review.

A Pack contributes data: reference values, translations, workflow definitions, letter templates, reason code sets, compliance reference configurations, and other structured starting-point content. It has no compiled code. It installs through the seeding framework established in [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md). It is reversible through the same installed_by_module_fk mechanism used for all contributed reference values. Its contents are labeled as educational reference material and never as compliance guarantees.

This distinction is intentional and must not be blurred. A construct that adds a new database table is a Module, because schema is code. A construct that populates an existing table with seed data is a Pack. If a capability requires both, it is a Bundle containing a Module and a Pack.

## Module Subtypes

All Module subtypes implement the full module contract. The subtype classification determines what kind of capability the Module contributes and which required and optional contract declarations apply. The following subtypes are defined.

> **MODULE SUBTYPES**
>
> **Locale Module**: contributes locale-specific schema extensions, field format validation, and locale-specific service integrations. Locale Modules add satellite tables for address structures, national identity number formats, and name component conventions that cannot be universalized in Core. A Locale Module also contributes locale-specific validation logic and may register action types for locale-specific external services such as address standardization APIs. Locale Modules are the mechanism through which Wax gains meaningful international support. The US Locale Module, for example, contributes the US address satellite table, the SSN and EIN identity satellite table, US postal code format validation, and the USPS CASS address standardization action type.
>
> **Business Class Module**: contributes the schema, workflow patterns, and operational configuration for a specific business vertical such as healthcare, auto lending, student loans, or utilities. Defines the debt types, required fields, and compliance posture relevant to that vertical.
>
> **Debt Type Module**: contributes a specific debt classification within a business class, with its associated field requirements, validation rules, and default workflow patterns.
>
> **Treatment Module**: contributes a treatment strategy type, meaning a defined approach to account handling such as payment arrangements, settlement workflows, or legal referral processes.
>
> **Vendor Integration Module**: contributes integration with an external platform or service provider. Registers the integration's API endpoints, authentication configuration, action types for the workflow engine, and response schema declarations for condition evaluation. Platform Integration certification from the Collective governs directory listing for Vendor Integration Modules.

## Pack Subtypes

All Pack subtypes install through the seeding framework. They contribute no compiled code. The following subtypes are defined.

> **PACK SUBTYPES**
>
> **Language Pack**: contributes translations for the i18n schema. Covers UI chrome resource bundle files and translations for all reference value labels, reason code labels, and system-defined string resources. A Language Pack is identified by its IETF BCP 47 locale tag. Multiple Language Packs may be installed simultaneously to support multilingual deployments. A Language Pack that does not cover all required translation keys is flagged as i18n non-compliant in the module registry per [Wax Design Decision 10](WAX-0010-module-registry.md).
>
> **Region Pack**: contributes locale-specific reference data for a geographic region. Covers currency codes, date and number format preferences, locale configuration defaults, and translated versions of standard reference data labels for the region. A Region Pack contains no compliance content. It provides structural and formatting context, not regulatory guidance. It is identified by an ISO 3166-1 country code or ISO 3166-2 subdivision code.
>
> **Compliance Pack**: contributes compliance reference configurations for a specific jurisdiction and regulatory context. Covers reference workflow definitions, reason code sets, required disclosure templates, and other regulatory starting-point configurations reflecting the Collective's understanding of applicable law at the time of publication. Compliance Packs are labeled prominently as educational reference material and do not constitute legal advice. They are identified by a structured locale identifier using ISO 3166 codes: compliance.us.tx for Texas, compliance.us.ca for California, compliance.ca.on for Ontario. Jurisdiction-level granularity is the standard. A single national Compliance Pack that flattens state or provincial variation is not appropriate given the material differences in collection law across jurisdictions.
>
> **Reference Pack**: contributes general-purpose reference data not specific to a compliance context. Covers standard reason code sets, common status code configurations, industry-standard action and result codes, and other shared vocabulary that agencies typically want pre-populated rather than building from scratch.
>
> **Template Pack**: contributes starting-point user-configurable content. Covers workflow definitions, letter templates, report definitions, UDT definitions, and UDW layouts that agencies can adopt and customize. Template Pack contents are installed as agency-owned configuration items, meaning they appear identical to items the agency created themselves and are fully editable after installation.

## Bundles

A Bundle is a named, versioned grouping of one or more Modules and zero or more Packs that are designed to be installed together and collectively deliver a coherent end-to-end capability. Bundles exist for distribution convenience, not as a new technical construct: installing a Bundle installs each of its components through their respective installation paths.

A Bundle manifest declares its component Modules and Packs with their required versions. The installer resolves component compatibility before installation begins and surfaces any conflicts. Updating a Bundle updates all components to their declared versions unless individual components are pinned by the agency.

The US Bundle is the natural starting configuration for a US-based agency: the US Locale Module, the appropriate Business Class Module for the agency's vertical, Compliance Packs for each state in which the agency is licensed to collect, the US Reference Pack, and optionally a starter Template Pack. Installing the US Bundle gives an agency a working configured Wax deployment with a single operation.

## Locale Modules and the Principle of Core Schema Neutrality

Wax owns no locale-specific schema. Address fields, national identity number fields, and structured name component fields are not defined in the core schema. This is a deliberate architectural principle: embedding US address conventions or any other locale's conventions in the core schema would make every non-US deployment carry meaningless schema columns and would make Wax a poorer fit for every locale except the one that was assumed.

Wax defines person and business entity records with genuinely universal attributes: a UUID primary key, creation and update timestamps, an organization FK, and a display_name field used for general display purposes. All other entity attributes are contributed by Locale Modules as satellite tables following the schema extension pattern from [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md).

The US Locale Module contributes the us_address satellite table on the person entity with addr1, addr2, city, state_code, postal_code, and county columns, the us_identity satellite table with ssn (PII-encrypted) and ein columns for businesses, USPS postal code format validation, state code validation, SSN format validation, and the USPS CASS address standardization action type for the workflow engine. A Philippines Locale Module would contribute an entirely different address satellite table structured around barangay, municipality_city, province, and region, and different identity fields reflecting Philippine ID systems. Neither Module knows about the other's schema.

Display_name in the core schema is intentionally freeform. Western first_name and last_name conventions are not universal: many cultures write family name first, some have patronymics that function differently from surnames, and some individuals have a single name. Structured name components are contributed by Locale Modules as satellite table fields appropriate to their cultural conventions. The display_name core field is derived from those structured components by the Locale Module's read model projection and is what read models and UI displays use for general-purpose person identification.

## Compliance Packs and the Auto-Close Mechanism

Compliance Packs serve a secondary function beyond providing reference configurations: they define the jurisdictions in which an agency has configured the platform to operate. When Wax receives an account with a debtor address in a jurisdiction for which no Compliance Pack is installed, it can be configured to automatically close that account rather than allow collection activity to proceed without appropriate compliance configuration.

This auto-close mechanism makes the installed Compliance Pack set an implicit operational boundary. An agency licensed to collect in twelve states installs twelve state-level Compliance Packs and configures the auto-close policy. Accounts from unlicensed or unconfigured states are automatically closed before any collector activity begins. The auto-close policy is configurable: agencies may choose to route such accounts to a review queue rather than close them immediately, for example to manually assign them to a specialist or to flag them for compliance review before any action is taken.

The auto-close mechanism is a Wax capability, not a Locale Module or Compliance Pack feature. The Compliance Pack's jurisdiction identifier is what the mechanism checks against. The policy behavior is configured by the agency through Wax's administration UI.

## Construct Identifier Conventions

All extensibility constructs use a structured identifier following a consistent convention. Module identifiers use reverse domain notation: oar.core.us_locale, oar.core.business_class.healthcare, vendor.lexisnexis.address_verification. Pack identifiers use a structured dot-notation path: language.es_mx, region.us, compliance.us.tx, compliance.us.ca, reference.us.fdcpa, template.us.standard_workflows. Bundle identifiers follow the same reverse domain convention as Modules: bundle.us.standard for the standard US starting Bundle.

Compliance Pack identifiers use ISO 3166-1 alpha-2 country codes and ISO 3166-2 subdivision codes to ensure unambiguous jurisdiction identification: compliance.us.tx, compliance.us.ca, compliance.ca.on, compliance.gb.eng. This structured identifier is machine-readable, sortable, and unambiguous regardless of the language of the installation.

## Implementation Phasing

**Wax v1 (MVP):** Terminology established in all documentation and code comments. One Seed Pack shipped: a US Generic Third-Party Collections configuration applied during initial setup, not through a Pack installation pipeline. No Bundle concept (requires a module marketplace). No Compliance Pack auto-close mechanism; accounts from unrecognized jurisdictions are handled manually.

**Wax v2:** Pack installation pipeline. Compliance Pack auto-close mechanism. Additional Seed Packs (healthcare, auto, first-party).

**Wax v3+:** Bundles. Community-contributed Packs.

**Breaking change risk: LOW.** Pack data uses the same reference value tables regardless of installation method.

## Implications For Contributors

A construct that adds a new database table or schema namespace is a Module. A construct that populates existing tables with data is a Pack. This distinction is not optional: the wrong classification will cause installation to use the wrong path and will fail validation.

Locale Modules must not assume that any other Locale Module is installed. Two Locale Modules may coexist on the same installation without knowing about each other. Schema extensions must not cross-reference another Locale Module's satellite tables.

Compliance Packs must carry the standard educational disclaimer in their manifest and in all installed content. No Compliance Pack may represent itself as legal advice or as a guarantee of compliance.

Compliance Pack identifiers must use ISO 3166 jurisdiction codes exactly. A Compliance Pack with an ambiguous or non-standard jurisdiction identifier will be rejected from the Collective repository.

Language Packs must cover all required translation keys defined in the Collective's core translation key registry. A Language Pack with missing keys will be flagged as i18n non-compliant and will not be listed in the Collective's directory.

Bundle manifests must declare exact version requirements for all components. A Bundle that declares imprecise version ranges is a compatibility risk and will not be accepted into the Collective repository without justification.
