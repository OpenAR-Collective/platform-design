---
id: WAX-0010
title: "Module Registry"
status: Accepted
version: 1.1
area: wax
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 10: Module Registry

## Decision

The Wax will maintain a module registry in the core schema. Every installed module, including Language Packs, Region Packs, Business Class modules, Treatment Module, Vendor Integrations, and Packs, is recorded in the registry as a first-class entity with a UUID surrogate key. Module names, labels, and descriptions follow the same i18n pattern as all other reference data: no English text is stored in the registry table itself. All human-readable module information lives in the i18n schema.

## Design Principle

Modules are not second-class citizens identified by string constants. They are entities in the system with their own identity, audit trail, and localized descriptions. The module registry is the authoritative record of what is installed, when it was installed, who installed it, what version is running, and whether it meets the platform's i18n compliance standard. It is also the foreign key target for every installed_by_module_fk reference in the system, making the ownership of every contributed row traceable back to a specific registered module.

## Core Schema: Module Registry

| **Table** | **Column** | **Type** | **Notes** |
| --- | --- | --- | --- |
| core.module | module_pk | UUID | Surrogate primary key. |
| core.module | module_version | VARCHAR | Semantic version string of the installed module. |
| core.module | module_type | VARCHAR | Technical classifier: language_pack, region_pack, business_class, debt_type, treatment, vendor_integration, seed_package. Developer-facing only. |
| core.module | is_i18n_compliant | Boolean | True if the module has provided translations for all installed language packs. |
| core.module | is_active | Boolean | False if the module has been deactivated but not fully uninstalled. |
| core.module | is_removed | Boolean | True for a Region Pack that has been removed and whose registry record is kept because retained rows still depend on it. False for every other module. |
| core.module | installed_at | Timestamp | When the module was installed. |
| core.module | installed_by_user_fk | UUID | References core.user. Who performed the installation. |
| core.module | updated_at | Timestamp | Last modification to the registry record. |

## i18n Schema: Module Translations

| **Table** | **Column** | **Type** | **Notes** |
| --- | --- | --- | --- |
| i18n.module_translation | translation_pk | UUID | Surrogate primary key. |
| i18n.module_translation | module_fk | UUID | References core.module. |
| i18n.module_translation | locale_code | VARCHAR | e.g., en_US, es_US |
| i18n.module_translation | short_code | VARCHAR | Brief identifier shown in admin lists. |
| i18n.module_translation | label | VARCHAR | Full display name in this locale. |
| i18n.module_translation | description | TEXT | Longer explanation of what this module does, in this locale. |

## i18n Compliance Checking

When a module is installed, the platform checks whether it has provided translation records in i18n.module_translation for every locale currently served by an installed Language Pack. If all locales are covered, is_i18n_compliant is set to true. If any locale is missing, it is set to false and the module is flagged in the administration interface.

Compliance is re-evaluated automatically when a new Language Pack is installed. Any existing module that lacks translations for the newly added locale is immediately flagged non-compliant. Module authors receive a clear signal about what translations are missing.

Non-compliant modules are installable and functional. The compliance flag is informational, not a gate. However, the platform surfaces the flag clearly wherever the module appears in administrative views, generating practical pressure on module authors to maintain translation completeness. A module that remains non-compliant across multiple language pack installations is a signal to the community about the quality of its maintenance.

## Module Uninstall and Reversibility

Module uninstall is a destructive operation and must be treated with appropriate caution. The module registry and the installed_by_module_fk mechanism exist precisely to make uninstall safe and complete. A partial uninstall, where some contributed rows are removed and others are not, is not a valid system state and must never be permitted. The one exception is the removal of a Region Pack, described under Region Pack Deactivation and Removal below.

## The uninstall sequence is:

Identify every row across every table in the system where installed_by_module_fk matches the target module. This inventory is produced before any action is taken and presented to the administrator for review.

Check each contributed reference value against all core schema and module-owned tables to determine whether it is currently referenced on any live record. If live references exist anywhere in the system, present the administrator with a count of affected records per value and halt. The administrator must choose: resolve the references manually and retry the physical uninstall, or proceed with soft deletion.

If soft deletion is chosen, set is_active to false on all contributed reference_value rows. The values are immediately removed from all selection interfaces. The module is marked inactive in core.module rather than removed. No schema objects are dropped. This is the recommended path for production systems with active data.

If physical uninstall proceeds, remove all contributed rows from reference_values and all translation tables in dependency order: translations first, then values, then types. Remove all rows in module-owned schema tables in dependency order. Drop all views, functions, indexes, and other objects in the module-owned schema. Drop the module-owned schema namespace. Remove the module registry record and its translation rows from core.module and i18n.module_translation as the final step.

The last-step removal of the core.module record is intentional. The registry record must remain in place throughout the entire uninstall sequence so that installed_by_module_fk references can be resolved. Removing it early would break the foreign key chain and make it impossible to identify contributed rows. The registry record is the last thing removed because it is the key to everything else.

A module that has been soft-deleted can be fully uninstalled at a later time once all live references to its contributed values have been migrated to replacement codes. The Collective will publish guidance on migration patterns for agencies transitioning away from a module's reference values.

## Region Pack Deactivation and Removal

A Region Pack contributes data and no code, and it contributes much more than reference values: currencies with their minor-unit scales and rounding conventions, date and number format preferences, locale configuration defaults, and translated standard labels. Deactivating a Region Pack is therefore an act on the whole pack. It applies soft deletion to everything the pack contributes. Reference values are set inactive as described above, and every other row that the pack owns is ignored wherever the platform resolves a setting, so the resolution falls through to the next source, as the locale chain of [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) falls from the system default to the hard fallback. Nothing is removed and nothing stored changes. The pack's registry record is marked inactive, and reactivating the pack restores everything it contributed.

Removal of a Region Pack follows a different rule from the sequence above, because stored values depend on what a Region Pack defines in ways that cannot be migrated away. An event that names a currency names it permanently, and events are never deleted. Live references therefore do not halt the removal. The system first applies the soft deletion above. It then removes, in dependency order, every row that the pack contributed and that no stored value references. Each row that a stored value still references is kept, inactive and read-only, so that every stored value stays readable and verifiable and the kept row cannot be applied to a new record. The pack's registry record stays as the owner of the kept rows so that installed_by_module_fk references continue to resolve, and it is marked removed. Because rows of the pack are gone, a removed pack cannot be reactivated in place. Loading the Region Pack again reuses its kept registry record, restores the rows that were removed, and makes the kept rows usable again. A kept row is removed at a later time if every reference to it is ever migrated away, which can never happen for a row that an event references.

This is the one exception to the rule that a partial uninstall is not a valid system state. It applies to Region Packs only, and every other module and Pack follows the sequence above. [Wax Design Decision 34](WAX-0034-monetary-values-and-currency.md) states what the rule means for currencies.

## Module Type Classifier

The module_type column on core.module is a technical classifier used by the platform runtime to determine how a module participates in the composition system. It is a developer-facing field and English values are acceptable because they are never surfaced in the user interface. The approved values are: language_pack, region_pack, business_class, debt_type, contract_type, treatment, vendor_integration, and seed_package. This list is fixed by the platform and may not be extended by module authors; contract_type was added per [Wax Design Decision 33](WAX-0033-module-composition-model.md) for the contract-type modules such as contingency, debt purchase, and servicing.

## Implementation Phasing

**Wax v1 (MVP):** Not implemented at runtime. Installed modules are known at compile time.

**Wax v2:** Full implementation. core.module_registry table, i18n module translations, module install and uninstall lifecycle, including the deactivation and removal of Region Packs.

**Breaking change risk: NONE.** The registry is additive infrastructure.

## Implications For Contributors

Every module must register itself in core.module during its installation migration. A module that does not register itself is not a valid Wax module.

Every module must provide translation records in i18n.module_translation for all installed language packs at installation time. Modules that do not will be flagged non-compliant immediately upon installation.

Every row a module contributes to any core or i18n table must carry an installed_by_module_fk reference to that module's core.module record. Rows without this reference are not reversible and will fail the module contribution audit.

Module authors are responsible for maintaining translation completeness as new language packs are released. The Collective will publish guidance on how to submit translation updates for existing modules.

A Region Pack can be deactivated or removed while its rows remain in use. Code that reads a row a Region Pack contributed does not assume that the pack is active.
