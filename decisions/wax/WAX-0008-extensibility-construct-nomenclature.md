---
id: WAX-0008
title: "Extensibility Construct Nomenclature"
status: Accepted
version: 2.0
area: wax
date: 2026-11-12
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 8: Extensibility Construct Nomenclature

## Decision

Wax's extensibility system uses two top-level constructs distinguished by a single principle: Modules contain code; Packs contain data. A Module implements the module contract standard from [Wax Design Decision 9](WAX-0009-module-contract-standard.md). A Pack installs structured data through the seeding framework. A Bundle is a named, versioned grouping of one or more Modules and zero or more Packs that are designed to be installed together and collectively deliver a coherent capability. All extensibility constructs are either a Module, a Pack, or a Bundle. Compliance rules, which govern how an organization must treat the people and businesses it deals with, ship only in a Compliance Pack for the jurisdiction whose rules they are, and the Locale Module, Region Pack, and Language Pack that carry a country's structure, formats, and translations carry none. Starting content that is not compliance, including the procedure that a module follows in a given jurisdiction, ships in a Boilerplate Pack. A rule's mechanism is code in the core or in a Module, built once, and a Pack supplies only the values for its jurisdiction. Every rule or value that a Pack carries, and every rule that a Module provides, has a stable identifier and a rule record that labels it, describes it in plain language, and cites its source. A jurisdiction's pack lists the jurisdictions inside it and marks each one, so that a coverage check can tell whether the installed packs cover a jurisdiction, and an organization can override that answer for a jurisdiction or designate a pack of its own. Every Pack is delivered read-only and serves as a template that is never used directly: installing it creates an instance that the organization owns and is encouraged to customize, and later delivered versions reach the instance only through a merge, as [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) describes. The Collective certifies Modules as software and publishes Packs as educational reference material, so an organization adopts a Pack as a starting point and remains responsible for its own compliance.

## The Fundamental Distinction

A Module contributes code: command handlers, event subscriptions, API endpoints, UI components, schema namespaces, validation logic, and action types. It implements the full module contract: a manifest file and a C# interface. It has a build process, a versioned binary, and a schema namespace it owns. It is subject to the module registry, the installation and uninstall lifecycle, and Collective certification review.

A Pack contributes data: reference values, translations, workflow definitions, letter templates, reason code sets, compliance reference configurations, and other structured starting-point content. It has no compiled code. It installs through the seeding framework established in [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md), as an instance of the read-only version that its publisher delivered. It is reversible through the same installed_by_module_fk mechanism used for all contributed reference values. Its contents are labeled as educational reference material and never as compliance guarantees.

This distinction is intentional and must not be blurred. A construct that adds a new database table is a Module, because schema is code. A construct that populates an existing table with seed data is a Pack. If a capability requires both, it is a Bundle containing a Module and a Pack.

## Where Content Belongs

Four tests place any piece of content and its defaults, and together they keep compliance out of the structural constructs and code out of the Packs.

> **WHERE CONTENT BELONGS**
>
> **The compliance test**: a rule that governs how an organization must treat another party, such as what it must disclose, when and how often it may make contact, or what it must stop doing, belongs to the Compliance Pack of the jurisdiction whose rule it is. A procedural rule of a court or another public body, which governs how that body runs its own process, is not compliance. It belongs to a Boilerplate Pack for the module that follows the process. [HiveAR Design Decision 13](../hivear/HIVE-0013-compliance-coverage-for-collections.md) reads this test for collections.
>
> **The code test**: content that needs code, a new table, or validation logic belongs to a Module. Values, templates, lists, and translations belong to a Pack.
>
> **The mechanism test**: a rule's mechanism, such as a counter of contacts or a window of permitted hours evaluated in a party's local time, is built once in the core or in a Module. A Compliance Pack supplies the rule's values for its jurisdiction, and the pack for a state or province supplies its own values on the same mechanism. In the same way, a module that follows another body's process builds that process once, and a Boilerplate Pack for each jurisdiction configures the jurisdiction's version of it. A rule that seems to need code inside a Pack shows that a mechanism is missing.
>
> **The default test**: a mechanism that needs a value before any pack supplies one carries a cautious default in the core or the Module, the value least likely to break a rule that the installation has not configured. A Compliance Pack replaces the default with the value that a jurisdiction's law sets, and that value stays flagged until someone with compliance standing verifies it. A Boilerplate Pack can set a conservative starting value for any setting that a mechanism exposes, such as whether a balance accrues interest, when the value is a sound practice that an organization may change rather than a rule of law. A question of law is therefore framed as a mechanism with a cautious default, and the answer lives in a pack.

A country's structure, formats, and translations ship in its Locale Module, Region Pack, and Language Packs, which carry no compliance, and its law ships in its Compliance Pack. A subdivision such as a state or province gets a Compliance Pack of its own, and Boilerplate Packs for any procedure that a module follows there, but no Locale Module or Region Pack unless its structure or formats differ from its country's, because its differences are legal and procedural and not structural. [HiveAR Design Decision 13](../hivear/HIVE-0013-compliance-coverage-for-collections.md) shows these layers for collections in the United States.

## Module Subtypes

All Module subtypes implement the full module contract. The subtype classification determines what kind of capability the Module contributes and which required and optional contract declarations apply. The following subtypes are defined.

> **MODULE SUBTYPES**
>
> **Locale Module**: contributes locale-specific schema extensions, field format validation, and locale-specific service integrations. Locale Modules add satellite tables for address structures, national identity number formats, and name component conventions that cannot be universalized in Core. A Locale Module also contributes locale-specific validation logic and may register action types for locale-specific external services such as address standardization APIs. Locale Modules are the mechanism through which Wax gains meaningful international support. The US Locale Module, for example, contributes the US address satellite table, the SSN and EIN identity satellite table, US postal code format validation, and the USPS CASS address standardization action type. One Locale Module serves a whole country, and a subdivision whose difference is only a name, such as a parish where other states have a county, uses the country's structure. A Locale Module carries no compliance content: the format of an identity number and its validation are structure, while a rule about when the number may be shown or used belongs to a Compliance Pack.
>
> **Business Class Module**: contributes the schema, workflow patterns, and operational configuration for a specific business vertical such as healthcare, auto lending, student loans, or utilities. Defines the debt types, required fields, and compliance posture relevant to that vertical.
>
> **Debt Type Module**: contributes a specific debt classification within a business class, with its associated field requirements, validation rules, and default workflow patterns.
>
> **Contract Type Module**: contributes the ownership and relationship model under which a debt is held and billed, such as servicing, third-party contingency, or purchase, as [Wax Design Decision 33](WAX-0033-module-composition-model.md) describes.
>
> **Treatment Module**: contributes a treatment strategy type, meaning a defined approach to debt handling such as payment arrangements, settlement workflows, or legal referral processes.
>
> **Vendor Integration Module**: contributes integration with an external platform or service provider. Registers the integration's API endpoints, authentication configuration, action types for the workflow engine, and response schema declarations for condition evaluation. Platform Integration certification from the Collective governs directory listing for Vendor Integration Modules.

## Pack Subtypes

All Pack subtypes install through the seeding framework, and each is delivered read-only and installed as an instance, as the section on delivered packs below describes. They contribute no compiled code. The following subtypes are defined.

> **PACK SUBTYPES**
>
> **Language Pack**: contributes translations for the i18n schema. Covers UI chrome resource bundle files and translations for all reference value labels, reason code labels, and system-defined string resources. A Language Pack is identified by its IETF BCP 47 locale tag. Multiple Language Packs may be installed simultaneously to support multilingual deployments. A Language Pack that does not cover all required translation keys is flagged as i18n non-compliant in the module registry per [Wax Design Decision 10](WAX-0010-module-registry.md).
>
> **Region Pack**: contributes the reference data of a country. Covers currency codes with their minor-unit scales and rounding conventions, date and number format preferences, time zones, locale configuration defaults, and translated versions of standard reference data labels for the region. A Region Pack contains no compliance content. It provides structural and formatting context, not regulatory guidance. It is identified by an ISO 3166-1 country code, or by an ISO 3166-2 subdivision code only where a subdivision's formats differ from its country's, never because its law differs.
>
> **Compliance Pack**: contributes the compliance reference configuration for one jurisdiction: the values that its rules need, such as windows, counts, durations, and thresholds, together with required disclosure templates, reference workflow definitions, reason code sets, and other regulatory starting-point configurations reflecting the Collective's understanding of applicable law at the time of publication. A Compliance Pack configures mechanisms that the core and Modules provide and carries no mechanism of its own. Each value it contributes has a rule record, and on top of that record it states its legal force, its effective dates, and whether someone with compliance standing has verified it, its justification being its source. A Compliance Pack lists the jurisdictions inside its own and marks each one, as the section on the jurisdiction tree below describes. Compliance Packs are labeled prominently as educational reference material and do not constitute legal advice. They are identified by a structured locale identifier using ISO 3166 codes: compliance.us for United States federal law, compliance.us.tx for Texas, compliance.us.ca for California, compliance.ca.on for Ontario. Jurisdiction-level granularity is the standard. The pack for a state or province layers on the pack for its country, and a single national Compliance Pack that flattens state or provincial variation is not appropriate given the material differences in law across jurisdictions.
>
> **Boilerplate Pack**: contributes the starting content that is not compliance, so that an organization does not begin with an empty system and have to think of everything itself: statuses, default roles, departments, and rules, workflow definitions, letter templates, report definitions, UDT definitions and UDW layouts, standard reason code sets, action and result codes, and other content that a typical organization wants. A Boilerplate Pack can also set the starting value of a setting that a core or Module mechanism exposes, where a conservative practice that the organization may change is wanted, as the default test above describes. A Boilerplate Pack also carries the procedure that a module follows in one jurisdiction, from the format of a filing to the time that must pass before the next step. That procedure is the bureaucracy of a court or another body and not compliance, because it governs how that body runs its process and not how the organization must treat another party. A rule that does govern how the organization must treat another party belongs to the Compliance Pack of that jurisdiction instead. [HiveAR Design Decision 13](../hivear/HIVE-0013-compliance-coverage-for-collections.md) describes the collections content of the Boilerplate Pack. A Boilerplate Pack is identified like other Packs, with a jurisdiction segment where its content is specific to one: boilerplate.us.collections, boilerplate.us.tx.legal_case_flow.
>
> **Seed Package**: contributes the foundational shared primitives that debt-domain modules reference by key, such as bucket definitions, role types, declared properties, and waterfall templates, as [Wax Design Decision 33](WAX-0033-module-composition-model.md) describes.

## Bundles

A Bundle is a named, versioned grouping of one or more Modules and zero or more Packs that are designed to be installed together and collectively deliver a coherent end-to-end capability. Bundles exist for distribution convenience, not as a new technical construct: installing a Bundle installs each of its components through their respective installation paths.

A Bundle manifest declares its component Modules and Packs with their required versions. The installer resolves component compatibility before installation begins and surfaces any conflicts. Updating a Bundle updates all components to their declared versions unless individual components are pinned by the organization, and each Pack in it reaches the organization's instance through the merge of Wax Design Decision 11.

A country's starting Bundle gathers its Locale Module, its Region Pack, its Language Packs, and the Compliance and Boilerplate Packs that a typical organization there starts with, so that a single operation gives the organization a working configuration. [HiveAR Design Decision 13](../hivear/HIVE-0013-compliance-coverage-for-collections.md) describes the United States starting Bundle for collections.

## Locale Modules and the Principle of Core Schema Neutrality

Wax owns no locale-specific schema. Address fields, national identity number fields, and structured name component fields are not defined in the core schema. This is a deliberate architectural principle: embedding US address conventions or any other locale's conventions in the core schema would make every non-US deployment carry meaningless schema columns and would make Wax a poorer fit for every locale except the one that was assumed.

Wax defines person and business entity records with genuinely universal attributes: a UUID primary key, creation and update timestamps, an organization FK, and a display_name field used for general display purposes. All other entity attributes are contributed by Locale Modules as satellite tables following the schema extension pattern from [Wax Design Decision 4](WAX-0004-schema-architecture-and-module-extension-pattern.md).

The US Locale Module contributes the us_address satellite table on the person entity with addr1, addr2, city, state_code, postal_code, and county columns, the us_identity satellite table with ssn (PII-encrypted) and ein columns for businesses, USPS postal code format validation, state code validation, SSN format validation, and the USPS CASS address standardization action type for the workflow engine. A Philippines Locale Module would contribute an entirely different address satellite table structured around barangay, municipality_city, province, and region, and different identity fields reflecting Philippine ID systems. Neither Module knows about the other's schema.

Display_name in the core schema is intentionally freeform. Western first_name and last_name conventions are not universal: many cultures write family name first, some have patronymics that function differently from surnames, and some individuals have a single name. Structured name components are contributed by Locale Modules as satellite table fields appropriate to their cultural conventions. The display_name core field is derived from those structured components by the Locale Module's read model projection and is what read models and UI displays use for general-purpose person identification.

## The Jurisdiction Tree

A jurisdiction's pack lists the jurisdictions inside it, such as a country's pack listing its states and territories, or a state's pack listing the counties and cities within it that have rules of their own, and it marks each child in one of three ways.

> **CHILD JURISDICTION MARKS**
>
> **Has its own pack**: the child has rules of its own, published in a pack that the mark names together with its version.
>
> **Checked, nothing to add**: the child was researched and adds nothing to its parent, so its parent's pack covers it.
>
> **Not yet researched**: no one has yet established whether the child has rules of its own.

A mark is a pack value like any other, so it carries a rule record and changes in a delivered update when research changes it. A child that a pack leaves unmarked counts as not yet researched. The tree is generic: a Canadian pack lists its provinces and territories in the same way that a United States pack lists its states and territories, and a pack can list children at any depth below it. The coverage check reads the trees of the Compliance Packs, and a Boilerplate Pack can list its children in the same way, so that a module following a jurisdiction's procedure can tell whether that jurisdiction's procedure is installed.

## Coverage

A coverage check answers whether the installed packs cover a jurisdiction. A jurisdiction is covered when a pack for it is installed, whether the one its parent names or one that the organization designated for it, or when its parent marks it checked and the parent is covered. It is not covered when its parent marks it as having its own pack, or as not yet researched, and no pack for it is installed. A child that no one has researched is therefore treated like one with rules of its own, which is the cautious default.

An organization can override the answer for a jurisdiction, such as treating Texas as covered without the Texas pack because the organization has written its own Texas rules. Each override is recorded with who set it, when, and why, it applies to that one jurisdiction only, and it can be lifted the same way.

The coverage check is a Wax capability and holds no jurisdiction's values: the trees come from the installed packs. A domain decides what a record outside coverage means. For collections, [HiveAR Design Decision 13](../hivear/HIVE-0013-compliance-coverage-for-collections.md) holds a debt whose debtor may be in a jurisdiction that is not covered.

## Packs an Organization Writes

An organization can write its own pack for a jurisdiction, or its own Module where the rules need code, and designate it as the one for that jurisdiction. The coverage check then accepts it as that jurisdiction's pack, so that the organization's choice to satisfy a jurisdiction's rules with its own work is respected. The registry of [Wax Design Decision 10](WAX-0010-module-registry.md) records where every installed Module and Pack came from, whether the Collective, the organization, or a third party, so that the source of every rule in force is always visible.

## Delivered Packs and Instances

Every Pack, whether a Compliance, Boilerplate, Region, or Language Pack, is delivered read-only and serves as a template that is never used directly. Installing it creates an instance, which the organization owns and is encouraged to customize to its own operation, and the instance is what the platform reads. The model is a container that runs from an image: the delivered pack is what its publisher releases, and the instance is what the organization runs. A later delivered version reaches the instance only through a merge that the organization performs, by stable rule identifier, as [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) describes, and an instance's version shows both its delivered base and the organization's own revision. Modules are code and upgrade the ordinary way, by installing a new version under the registry of Wax Design Decision 10.

## Rule Records

Every rule or value that a Pack carries, and every rule that a Module provides, has a stable identifier and a rule record that travels with it.

> **RULE RECORD**
>
> **Identifier**: stable across versions and never reused, so that a merge, a report, or an audit can follow the rule from one version to the next.
>
> **Label**: a short name for the rule.
>
> **Description**: what the rule does, in plain language and not in code.
>
> **Justification**: why the rule is what it is, citing its source: the authority, the document, the section, and where useful the paragraph or line.

The record is not only for compliance. A Locale Module's format check for a national identity number cites the issuing authority's published rules and states them in plain words, such as the US Locale Module's check of the Social Security number. A Compliance Pack value adds its legal force, its effective dates, and its verification status to its rule record, and its justification is its source. A Module declares the records of the rules it provides in its manifest, as [Wax Design Decision 9](WAX-0009-module-contract-standard.md) describes.

## Construct Identifier Conventions

All extensibility constructs use a structured identifier following a consistent convention. Module identifiers use reverse domain notation: oar.core.us_locale, oar.core.business_class.healthcare, vendor.lexisnexis.address_verification. Pack identifiers use a structured dot-notation path: language.es_mx, region.us, compliance.us, compliance.us.tx, compliance.us.ca, boilerplate.us.collections, boilerplate.us.tx.legal_case_flow. Bundle identifiers follow the same reverse domain convention as Modules: bundle.us.standard for the standard US starting Bundle.

Compliance Pack identifiers use ISO 3166-1 alpha-2 country codes and ISO 3166-2 subdivision codes to ensure unambiguous jurisdiction identification: compliance.us for a country's national law, and compliance.us.tx, compliance.us.ca, compliance.ca.on, and compliance.gb.eng for subdivisions. This structured identifier is machine-readable, sortable, and unambiguous regardless of the language of the installation. A child below the subdivision level, such as a city or a county with rules of its own, has its place in its parent's tree, and how a pack for it is identified, since ISO 3166 codes stop at subdivisions, is recorded as an open question.

## Implementation Phasing

**Wax v1 (MVP):** Terminology established in all documentation and code comments. One Boilerplate Pack shipped and applied during initial setup rather than through a Pack installation pipeline, already as an instance that the organization owns, with the delivered version it came from recorded so that its first update can be merged. No Bundle concept (requires a module marketplace). No coverage check: records from jurisdictions that the installation does not serve are handled manually.

**Wax v2:** Pack installation pipeline, with read-only delivered versions, instances, and the merge of later versions. The jurisdiction tree, the coverage check, overrides, and packs that an organization writes and designates. Rule records for every Pack value and every rule a Module provides. Additional Boilerplate Packs.

**Wax v3+:** Bundles. Community-contributed Packs.

**Breaking change risk: LOW.** Pack data uses the same reference value tables regardless of installation method, and an instance installed in v1 records the delivered version it came from, so a later merge needs no guesswork.

## Implications For Contributors

A construct that adds a new database table or schema namespace is a Module. A construct that populates existing tables with data is a Pack. This distinction is not optional: the wrong classification will cause installation to use the wrong path and will fail validation.

Content goes where the four tests put it, and a cautious default lives with its mechanism while the law's value goes in a Compliance Pack and a conservative starting value in a Boilerplate Pack. A Locale Module, a Region Pack, and a Language Pack carry no compliance content. A Compliance Pack and a Boilerplate Pack carry values and templates for mechanisms that exist and never carry code. A subdivision gets a Compliance Pack for its compliance rules and a Boilerplate Pack for any procedure that a module follows there, and no Locale Module or Region Pack unless its formats or structure differ from its country's.

Every rule or value in a Pack, and every rule a Module provides, carries a stable identifier and a rule record, and an identifier is never reused for another rule.

A jurisdiction's pack lists its children and marks each one, and a child left unmarked counts as not yet researched. Code reads a Pack's instance, never its delivered version, and nothing writes to a delivered version.

Locale Modules must not assume that any other Locale Module is installed. Two Locale Modules may coexist on the same installation without knowing about each other. Schema extensions must not cross-reference another Locale Module's satellite tables.

Compliance Packs must carry the standard educational disclaimer in their manifest and in all installed content. No Compliance Pack may represent itself as legal advice or as a guarantee of compliance.

Compliance Pack identifiers must use ISO 3166 jurisdiction codes exactly. A Compliance Pack with an ambiguous or non-standard jurisdiction identifier will be rejected from the Collective repository.

Language Packs must cover all required translation keys defined in the Collective's core translation key registry. A Language Pack with missing keys will be flagged as i18n non-compliant and will not be listed in the Collective's directory.

Bundle manifests must declare exact version requirements for all components. A Bundle that declares imprecise version ranges is a compatibility risk and will not be accepted into the Collective repository without justification.
