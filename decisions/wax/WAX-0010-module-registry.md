---
id: WAX-0010
title: "Module Registry"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
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

Module uninstall is a destructive operation and must be treated with appropriate caution. The module registry and the installed_by_module_fk mechanism exist precisely to make uninstall safe and complete. A partial uninstall, where some contributed rows are removed and others are not, is not a valid system state and must never be permitted.

## The uninstall sequence is:

Identify every row across every table in the system where installed_by_module_fk matches the target module. This inventory is produced before any action is taken and presented to the administrator for review.

Check each contributed reference value against all core schema and module-owned tables to determine whether it is currently referenced on any live record. If live references exist anywhere in the system, present the administrator with a count of affected records per value and halt. The administrator must choose: resolve the references manually and retry the physical uninstall, or proceed with soft deletion.

If soft deletion is chosen, set is_active to false on all contributed reference_value rows. The values are immediately removed from all selection interfaces. The module is marked inactive in core.module rather than removed. No schema objects are dropped. This is the recommended path for production systems with active data.

If physical uninstall proceeds, remove all contributed rows from reference_values and all translation tables in dependency order: translations first, then values, then types. Remove all rows in module-owned schema tables in dependency order. Drop all views, functions, indexes, and other objects in the module-owned schema. Drop the module-owned schema namespace. Remove the module registry record and its translation rows from core.module and i18n.module_translation as the final step.

The last-step removal of the core.module record is intentional. The registry record must remain in place throughout the entire uninstall sequence so that installed_by_module_fk references can be resolved. Removing it early would break the foreign key chain and make it impossible to identify contributed rows. The registry record is the last thing removed because it is the key to everything else.

A module that has been soft-deleted can be fully uninstalled at a later time once all live references to its contributed values have been migrated to replacement codes. The Collective will publish guidance on migration patterns for agencies transitioning away from a module's reference values.

## Module Type Classifier

The module_type column on core.module is a technical classifier used by the platform runtime to determine how a module participates in the composition system. It is a developer-facing field and English values are acceptable because they are never surfaced in the user interface. The approved values are: language_pack, region_pack, business_class, debt_type, contract_type, treatment, vendor_integration, and seed_package. This list is fixed by the platform and may not be extended by module authors; contract_type was added per [Wax Design Decision 33](WAX-0033-module-composition-model.md) for the contract-type modules such as contingency, debt purchase, and servicing.

## Implementation Phasing

**Wax v1 (MVP):** Not implemented at runtime. Installed modules are known at compile time.

**Wax v2:** Full implementation. core.module_registry table, i18n module translations, module install and uninstall lifecycle.

**Breaking change risk: NONE.** The registry is additive infrastructure.

## Implications For Contributors

Every module must register itself in core.module during its installation migration. A module that does not register itself is not a valid Wax module.

Every module must provide translation records in i18n.module_translation for all installed language packs at installation time. Modules that do not will be flagged non-compliant immediately upon installation.

Every row a module contributes to any core or i18n table must carry an installed_by_module_fk reference to that module's core.module record. Rows without this reference are not reversible and will fail the module contribution audit.

Module authors are responsible for maintaining translation completeness as new language packs are released. The Collective will publish guidance on how to submit translation updates for existing modules.
