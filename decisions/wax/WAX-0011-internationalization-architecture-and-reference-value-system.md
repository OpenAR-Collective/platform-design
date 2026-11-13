---
id: WAX-0011
title: "Internationalization Architecture and Reference Value System"
status: Accepted
version: 1.2
area: wax
date: 2026-11-12
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 11: Internationalization Architecture and Reference Value System

## Decision

The Wax will store all reference values, status codes, reason codes, and lookup values as language-neutral UUID surrogate keys. No English string or language-specific text will appear in entity tables or reference value tables. All human-readable labels, short codes, and descriptions will reside exclusively in the i18n schema, translated per locale. Views built over the i18n tables will expose translated values to queries, resolving locale through a three-level fallback chain.

## Design Principle

Even short codes that feel universally understood within the industry, such as ACTIVE or CLOSED, are English artifacts. The database does not know what language a user speaks. The numeric or UUID surrogate key is the only truly language-neutral identifier. This principle applies at every level: reference types, reference values, module names, and system labels. The only place English is permitted to appear in technical identifiers is in developer-facing configuration keys and locale codes themselves, which are standardized technical strings that never surface in the user interface.

## Core Schema: Reference Types and Values

Reference types define categories of lookup values (such as debt status, reason code category, or debt type). Reference values are the individual entries within each type. Neither table stores any language-specific text.

| **Table** | **Column** | **Type** | **Notes** |
| --- | --- | --- | --- |
| core.reference_type | reference_type_pk | UUID | Surrogate primary key. No name column. |
| core.reference_type | installed_by_module_fk | UUID | References core.module. Null if Core-defined. |
| core.reference_type | created_at | Timestamp |  |
| core.reference_value | reference_value_pk | UUID | Surrogate primary key. |
| core.reference_value | reference_type_fk | UUID | References core.reference_type. |
| core.reference_value | sort_order | Integer | Display ordering within the type. |
| core.reference_value | is_active | Boolean | Inactive values are hidden from selection but preserved for history. |
| core.reference_value | installed_by_module_fk | UUID | References core.module. Null if user-defined. |
| core.reference_value | created_at | Timestamp |  |

## i18n Schema: Translation Tables

All human-readable text lives in the i18n schema. Reference types and reference values each have their own translation table. Module translations are documented under [Wax Design Decision 10](WAX-0010-module-registry.md).

| **Table** | **Column** | **Type** | **Notes** |
| --- | --- | --- | --- |
| i18n.reference_type_translation | translation_pk | UUID | Surrogate primary key. |
| i18n.reference_type_translation | reference_type_fk | UUID | References core.reference_type. |
| i18n.reference_type_translation | locale_code | VARCHAR | e.g., en_US, es_US |
| i18n.reference_type_translation | label | VARCHAR | Display label for this type in this locale. |
| i18n.reference_type_translation | description | TEXT | Longer explanation in this locale. |
| i18n.reference_type_translation | installed_by_module_fk | UUID | References core.module. Null if user-defined. |
| i18n.reference_value_translation | translation_pk | UUID | Surrogate primary key. |
| i18n.reference_value_translation | reference_value_fk | UUID | References core.reference_value. |
| i18n.reference_value_translation | locale_code | VARCHAR | e.g., en_US, es_US |
| i18n.reference_value_translation | short_code | VARCHAR | Brief code shown in lists and reports (e.g., ACTIVE, CLOSED). |
| i18n.reference_value_translation | label | VARCHAR | Full display label in this locale. |
| i18n.reference_value_translation | description | TEXT | Longer explanation in this locale. |
| i18n.reference_value_translation | installed_by_module_fk | UUID | References core.module. Null if user-defined. |

## System Configuration and Locale Resolution

The system default locale is stored in a core configuration table, set at installation and manageable by an administrator. Views resolve locale through the following fallback chain, in order:

Session variable: app.locale if set for the current database session.

System default: the default_locale value from core.system_configuration.

Hard fallback: the locale designated as the installation default if neither of the above is available.

A single-language deployment never requires session variables to be set. The system default handles all locale resolution transparently. A multilingual deployment sets the session variable per user connection at login time. In both cases the view definitions are identical.

| **Table** | **Column** | **Type** | **Notes** |
| --- | --- | --- | --- |
| core.system_configuration | configuration_pk | UUID | Surrogate primary key. |
| core.system_configuration | configuration_key | VARCHAR | Developer-facing technical key. Never surfaced in the UI. English is acceptable here. |
| core.system_configuration | configuration_value | VARCHAR | The stored value for this setting. |
| core.system_configuration | updated_at | Timestamp |  |
| core.system_configuration | updated_by_user_fk | UUID | References core.user. |

## Localized Views

All user-facing queries retrieve translated values through views rather than querying the translation tables directly. Views are defined once and resolve locale dynamically through the session variable and system configuration fallback chain described above. The same view serves all locales: the resolved locale determines which translation rows are returned.

## An illustrative view definition for debt status:

> **vw_debt_status -- resolves locale dynamically**
>
> ```sql
> CREATE VIEW vw_debt_status AS
> SELECT
> rv.reference_value_pk,
> rv.sort_order,
> rv.is_active,
> t.short_code,
> t.label,
> t.description
> FROM core.reference_value rv
> JOIN core.reference_type rt
> ON rv.reference_type_fk = rt.reference_type_pk
> JOIN i18n.reference_type_translation rtt
> ON rtt.reference_type_fk = rt.reference_type_pk
> AND rtt.locale_code = COALESCE(
> current_setting('app.locale', true),
> (SELECT configuration_value FROM core.system_configuration
> WHERE configuration_key = 'default_locale'),
> 'en_US')
> JOIN i18n.reference_value_translation t
> ON t.reference_value_fk = rv.reference_value_pk
> AND t.locale_code = COALESCE(
> current_setting('app.locale', true),
> (SELECT configuration_value FROM core.system_configuration
> WHERE configuration_key = 'default_locale'),
> 'en_US')
> WHERE -- filter to debt_status reference type
> ```

## User-Defined Code Creation

When a user creates a new reference value, the system enforces translation completeness at the point of creation. The workflow is:

The system generates a new reference_value_pk UUID.

The system detects all installed Language Pack modules.

If one language pack is installed, the user sees a single form: short code, label, and description in that language.

If multiple language packs are installed, the interface presents one form section per language. All sections must be completed before the record can be saved.

Saving is atomic: the reference_value row and all required translation rows are written together in a single transaction. A reference value with missing translations for any installed language is not permitted.

## Packs

Wax delivers no default reference values. A freshly installed system has an empty code table. Every agency defines the values appropriate to their own operations. This is intentional: it avoids encoding assumptions about how agencies work into the platform and keeps Wax free of English-language defaults.

The practical consequence, however, is that a practitioner evaluating HiveAR who opens a blank system for the first time has no reference point. There are no debt statuses to select, no reason codes to apply, no debt types to choose. The system is structurally correct but operationally empty. For a practitioner who does not yet know what they want, seeing an example of a well-designed configuration is the most effective way to learn what is possible.

Packs address this directly. A Pack is an optional, separately installable collection of well-designed reference values and their translations representing a thoughtful starting point for a specific type of collections operation. Installing a Pack transforms an empty system into a fully configured, immediately navigable environment that an agency can evaluate, adapt, and build on.

## What a Pack Contains

A Pack contributes rows to reference_value and the i18n translation tables. It does not add schemas, tables, views, or application logic. It is pure data. A generic third-party collections Pack might contribute values across all of the following reference type categories:

**Debt statuses**: active, closed, disputed, pending validation, ceased and desisted, deceased, legal hold, and others representing the full lifecycle of a collection debt.

**Contact result codes**: answered, no answer, left message, wrong number, number disconnected, refused to pay, promise to pay, call back requested, and similar outcome codes used to log every contact attempt.

**Reason codes**: the full set of why-did-this-change codes used by the event store, covering balance adjustments, status transitions, contact updates, assignment changes, and regulatory events.

**Dispute types**: identity theft claim, debt not mine, balance dispute, and other categories relevant to the dispute workflow. A dispute type named for a statute, such as an FDCPA or FCRA dispute in the United States, comes from that jurisdiction's Compliance Pack.

**Closure reasons**: paid in full, settled, returned to creditor, sold, deceased, statute of limitations, and other standard closure categories.

**Communication channel types**: outbound call, inbound call, letter, email, text message, and other contact modalities.

**Document types**: cease and desist confirmation, settlement agreement, payment receipt, and other document categories. A document that a law prescribes, such as the United States validation notice, comes from that jurisdiction's Compliance Pack.

Each contributed value includes translations for every Language Pack installed on the system. A system with only the English US Language Pack sees English labels throughout. A system with English and Spanish Language Packs sees both, and every Pack value is fully translated in both.

## Multiple Packs

The Collective will develop and maintain multiple Packs targeting different operation types. These packages are independently installable and can be layered: an agency doing healthcare collections might install the generic third-party Pack as a foundation and then install the healthcare-specific Pack on top, which adds healthcare-specific values without duplicating the generic ones. The packs for operation types below are Boilerplate Packs, and the packs for the compliance rules of jurisdictions are Compliance Packs, as [Wax Design Decision 8](WAX-0008-extensibility-construct-nomenclature.md) distinguishes them.

## Planned Packs include:

**Generic Third-Party Collections**: a well-rounded starting point suitable for most collection agencies doing traditional third-party contingency work.

**First-Party Collections**: values oriented toward creditors and original creditors managing their own receivables, with different status and closure vocabularies.

**Healthcare Collections**: extends the generic package with medical-specific debt statuses, insurance-related reason codes, HIPAA-relevant document types, and healthcare-specific dispute categories.

**Legal Collections**: extends the generic package with pre-legal and legal workflow statuses, court-related reason codes, judgment and garnishment document types, and attorney assignment codes.

**Debt Purchase**: values oriented toward debt buyers, including purchased portfolio statuses, chain-of-title document types, and purchase price allocation codes.

**United States Federal Compliance Pack**: compliance.us, a suggested set of workflow reference values, reason codes, and status definitions reflecting common industry interpretation of federal collection law requirements, including the FDCPA and Regulation F. Labeled explicitly as educational reference material. Not a compliance guarantee.

**State Compliance Packs**: individual Compliance Packs for each US state, layered on the federal pack, providing suggested reference values reflecting common interpretations of state-specific collection statutes, licensing requirements, and consumer protection provisions. Each is separately installable, labeled as educational reference material, and reflects the Collective's understanding of current law at the time of publication. Agencies are responsible for independent legal review before relying on any state Compliance Pack for compliance purposes.

## Compliance Packs and the Liability Boundary

The decision to deliver compliance reference configurations as Packs rather than as installed modules is deliberate and principled. Modules are architectural components. Their behavior is part of the system. A compliance module would imply that the system itself guarantees compliance with the encoded rules, which is a claim no software can honestly make.

Packs are explicitly educational reference material. They represent the Collective's best effort to document common industry practice and prevailing legal interpretation at the time of publication. They are starting points for agency configuration, not finished compliance programs. An agency that installs a state-level Compliance Pack and modifies it based on guidance from its own legal counsel is using the platform correctly. An agency that installs it and treats it as a substitute for legal counsel is not.

Every Compliance Pack will carry a prominent disclaimer, both in the installation interface and in the Pack documentation, stating that the configuration reflects the Collective's educational interpretation of applicable law at the time of publication, that law changes and interpretations vary, and that agencies are solely responsible for ensuring their own compliance with all applicable federal and state requirements. This disclaimer is not a legal footnote. It is a structural feature of how compliance configuration is delivered.

## Delivered Packs and Agency Instances

A delivered Pack, the version that the Collective or another publisher releases, is stored read-only. It serves as a template and is never used directly. Installing it creates an instance, recorded with the delivered version it came from, and the instance is what the platform reads. Every Pack works this way, whether a Compliance, Boilerplate, Region, or Language Pack, as [Wax Design Decision 8](WAX-0008-extensibility-construct-nomenclature.md) provides, while Modules, which are code, upgrade the ordinary way.

Once installed, an instance's records behave like any other agency-defined record from the system's operational perspective. Agencies may modify the translations, adjust sort orders, deactivate values they do not use, and add their own values alongside the delivered ones, and they are encouraged to customize the instance to their own operation. The instance is a starting point, not a locked configuration. The delivered version stays unchanged beside it, so that a later merge can tell the agency's changes from the publisher's.

The installed_by_module_fk on instance rows serves only the reversibility function. It identifies which rows the Pack contributed so they can be managed cleanly at uninstall time. It does not restrict the agency from modifying those rows in any way.

Agencies that outgrow a Pack configuration entirely may uninstall it and replace its values with their own. The uninstall sequence described in the Reversibility section applies: if Pack values are in use on live records, soft deletion is the appropriate path. Over time, as the agency defines their own replacement codes, they can migrate records off the Pack values and eventually remove the soft-deleted values when no live references remain. A Region Pack follows its own rule for deactivation and removal, which [Wax Design Decision 10](WAX-0010-module-registry.md) defines.

## Updates and Merges

Downloading an update stores the new delivered version alongside the earlier ones and leaves the instance untouched. The agency then merges: the merge compares the agency's current instance with the new delivered version, using the delivered version that the instance was based on as their common ancestor, and brings each change across. Version control is the model, adapted to pack data. Each rule or value merges by the stable identifier that [Wax Design Decision 8](WAX-0008-extensibility-construct-nomenclature.md) gives it, never by lines of text, so a rule that only the publisher changed is taken, a rule that only the agency changed is kept, and a rule that both changed is a conflict that the agency resolves. An agency is encouraged to keep every delivered version since its installation and is not required to. The merge needs only the instance's base version, and when that version has been deleted, the merge fetches it again from its publisher, which keeps every version it has delivered.

A pack update is a publisher's change from one delivered version to the next. It is made of rule changes, such as adding a rule, retiring one, or changing a value or the dates on which it is effective, and each change names the stable identifier of its rule. A pack update is not a database schema migration, which changes the platform's tables.

An instance's version shows both its delivered base and the agency's own revision, written as the base version, a plus sign, and the letter a followed by the revision number. Installing delivered version 2.4 gives 2.4+a0. Every change that the agency saves to the instance raises the revision by one, so 2.4+a8 is an instance based on 2.4 that has changed eight times. A merge is also a change: merging delivered version 2.5 into 2.4+a8 gives 2.5+a9. The revision never resets, so the number always shows both what the instance was built from and how far the agency has taken it.

## Packs and the Evaluation Experience

The Pack concept is also the Collective's primary tool for making HiveAR evaluable without requiring significant upfront configuration work. An agency evaluating the platform can install Wax and HiveAR, select their module combination, install a Pack that matches their operation type, and immediately have a navigable, realistic system to explore. Collector queue views have statuses. Reason code dropdowns have values. Reports have categories to group by. The platform feels operational from the first session.

This matters for adoption. A platform that requires weeks of configuration before it can be evaluated is a platform that most agencies will not evaluate. Packs compress that timeline to hours, creating a realistic first impression that a blank system cannot provide.

## Reversibility

Every row contributed by a module or Pack to reference_values, any translation table, or any other core or i18n table carries an installed_by_module_fk reference pointing to that module's record in core.module. This foreign key is the connective tissue that makes the entire contribution system reversible. It is not optional and it is not a convention: a row without an installed_by_module_fk is an orphan with no known owner and cannot be safely managed.

When a module is uninstalled, the system executes the following sequence before removing any data:

Identify all rows across all tables where installed_by_module_fk matches the target module.

For each reference value owned by the module, check whether that value is currently referenced on any live record in any core schema or module-owned table. This check spans the entire schema, not just the tables the module itself created.

If any live references exist, present the administrator with a count of affected records per reference value and block the uninstall. The administrator must resolve those references manually before the uninstall can proceed, or choose soft deletion as described below.

If no live references exist, or after the administrator has resolved them, proceed with physical deletion of all contributed rows in dependency order, followed by dropping the module-owned schema namespace.

Soft deletion is available as an alternative to blocking when live references exist. Rather than physically removing the reference value, the system sets is_active to false on the affected core.reference_value row. The value is removed from all selection interfaces and cannot be applied to new records. Existing records that carry the value are unaffected and retain their historical integrity. The module registry record is marked inactive rather than removed. This preserves referential integrity while effectively retiring the module's contributions from active use.

Soft deletion is the recommended path in production systems with active data. Physical uninstall is appropriate for development environments, for modules that were installed in error and never used, and for Packs whose contributed values have been fully replaced by agency-defined codes.

A Region Pack is the exception to blocking and to the rule that a partial uninstall is invalid. Deactivating a Region Pack applies soft deletion to everything the pack contributes, including its currencies, format preferences, locale configuration defaults, and translated standard labels. Removing a Region Pack never blocks on live references. The system removes every contributed row that no live record references and keeps each row that one does, inactive and read-only, under the pack's registry record, which is marked removed. [Wax Design Decision 10](WAX-0010-module-registry.md) defines the sequence, and [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md) states what it means for currencies.

## Implementation Phasing

**Wax v1 (MVP):** Schema ships complete, English only. This is the canonical example of the "schema now, features later" principle. Ship: core.reference_type and core.reference_value tables with UUID surrogate keys; i18n.reference_value_translation table populated with en-US rows only; the three-tier locale resolution chain in code (system default, type override, value override) even though only one locale exists; all status codes, reason codes, debt types, and domain lookups stored as UUID references with translations, never as hardcoded strings. No locale resolution UI. No Language Pack installation pipeline. No RTL support. The one Boilerplate Pack applied at setup is installed as an instance, with the delivered version it came from recorded.

**Wax v2:** User locale preference setting. Language Pack installation pipeline. Read-only delivered versions, instances with their base version and agency revision, and the merge of pack updates. Spanish Language Pack as first additional language. RTL CSS logical properties (structural only).

**Wax v3+:** Full RTL Language Packs (Arabic, Hebrew). CJK font fallback system. Locale-aware entity matching field registries for non-US Locale Modules.

**Breaking change risk: HIGH if deferred. NONE if schema ships in v1.** Retrofitting i18n tables onto a system that hardcoded English strings is a rewrite, not a migration.

## Implications For Contributors

No module may store language-specific text in any core schema entity table or reference value table.

Every reference value contributed by a module must include translation records for all installed language packs at installation time.

Modules that fail to provide complete translations for all installed locales will be flagged as i18n non-compliant in the module registry ([Wax Design Decision 10](WAX-0010-module-registry.md)).

All foreign key references to reference values in module-owned tables must reference reference_value_pk. Short codes and labels are never stored as foreign keys or repeated in module tables.

Code that reads a value contributed by a Region Pack must not assume that the pack is active, because a Region Pack can be deactivated or removed while its rows remain in use.

Code reads a Pack's instance, never its delivered version, and nothing writes to a delivered version.

A pack update names every change by the stable identifier of the rule it adds, changes, or retires.
