---
id: HIVE-0001
title: "Entity Data Model, Person, Business, and Entity Relationships"
status: Accepted
version: 2.1
area: hivear
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 1: Entity Data Model, Person, Business, and Entity Relationships

## Decision

HiveAR models people and businesses as Entity records. Entity is the universal parent type. Person and Business are subtypes that inherit from Entity and extend it through Locale Module satellite tables. Wax owns no locale-specific schema: address fields, national identity number fields, and name component fields are entirely contributed by Locale Modules as satellite tables. Two bridge tables govern relationships between entities and between entities and debts. Entity aggregate fields are calculated when they are read and cover only responsible-party associations.

## Entity as the Universal Parent

Entity is the preferred term over Party, which has precedent in financial services MDM but reads awkwardly to AR practitioners. Every person and business in HiveAR is an Entity record. The entity type determines which Locale Module satellite tables are present and which fields are available for matching, display, and golden record computation.

Wax defines the entity scaffold with genuinely universal attributes only. Locale-specific attributes such as address structure, national identity numbers, and name components are contributed by Locale Modules as satellite tables per [Wax Design Decision 4](../wax/WAX-0004-schema-architecture-and-module-extension-pattern.md) and the Core Schema Neutrality principle of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). This means a Philippines-deployed HiveAR has different satellite tables than a US-deployed HiveAR, and neither carries meaningless schema columns inherited from the other.

> **CORE ENTITY SCHEMA**
>
> **entity_pk**: UUID surrogate primary key, auto-generated.
>
> **entity_type**: discriminator value, either person or business.
>
> **display_name**: a freeform text field used for general-purpose display. This is the only name field in Core. It is derived by Locale Module read model projections from the structured name component satellite tables contributed by the relevant Locale Module, and is updated whenever the underlying name components change.
>
> **organization_fk**: the organization this entity belongs to.
>
> **created_at**: UTC timestamp, auto-set on insert, immutable.
>
> **updated_at**: UTC timestamp, auto-updated on every write.
>
> **created_by_user_fk and updated_by_user_fk**: actor references.
>
> **is_active**: boolean, calculated when read from the entity's debt associations. True if the entity has at least one active debt.

A payer is an entity too. Every payment records its payer as an entity under [HiveAR Design Decision 7](HIVE-0007-payment-application-and-waterfall.md), and a payer who is not on file, such as a relative or an insurer who pays toward a debt that someone else owes, is added from the payment with the minimum that a refund needs: a name and a way to return the money, such as the payment it came from or a mailing address. Paying gives the payer no role on a debt and no authority over it. The is_responsible_party flag on the payer's own relationships to debts, described below, says which debts the payer is responsible for, and HiveAR Design Decision 7 lets money that the payer did not direct reach only those debts. Whether a person may discuss a debt is a matter of representation and authorization, which this decision does not settle.

## Person and Business Subtypes

Person and Business share the core entity schema but differ in which Locale Module satellite tables they carry. A US Person has us_name_components (given_name, family_name, middle_name, suffix), us_identity (ssn encrypted PII, ein for co-signers), and us_address satellite tables contributed by the US Locale Module. A Philippines Person has ph_name_components and ph_identity satellite tables contributed by a Philippines Locale Module. Neither knows about the other's schema.

Business entities have different name conventions from persons. Forcing a business name into a first_name field and leaving last_name blank is a common workaround in legacy systems and a schema defect. HiveAR handles this cleanly: a Business entity has business name satellite fields appropriate to its locale, distinct from person name satellite fields. The display_name core field serves both, derived by the Locale Module's read model projection from whichever name satellite table is present.

Person entities in the US require at minimum a given_name and family_name as declared by the US Locale Module's completeness validator for the name attribute type. Middle name and suffix are optional. Other locales declare their own completeness rules: a single-name culture declares that a primary_name field alone satisfies completeness. Completeness validation is always locale-specific and never hardcoded in Wax.

## Entity-to-Entity Relationships

A bridge table between two entity records defines their relationship. This is the relational graph of who knows whom, who works for whom, and who is legally related to whom. It is not a collections concept specifically: it is general-purpose entity graph infrastructure that the collections context uses in specific ways.

> **ENTITY-TO-ENTITY RELATIONSHIP BRIDGE SCHEMA**
>
> **entity_relationship_pk**: UUID surrogate primary key.
>
> **entity_a_fk**: one entity in the relationship.
>
> **entity_b_fk**: the other entity in the relationship.
>
> **relationship_type_fk**: reference value defining the relationship type: spouse, parent, child, sibling, employer, employee, attorney, authorized_representative, guarantor, co_signer, and others as defined by modules and agency configuration.
>
> **entity_a_role_fk**: optional label for entity A's role in this specific relationship when the type alone is insufficient.
>
> **entity_b_role_fk**: optional label for entity B's role.
>
> **is_active**: boolean, whether the relationship is currently in effect.
>
> **effective_date and end_date**: optional dates bounding the relationship.
>
> **created_at, updated_at, created_by_user_fk, updated_by_user_fk**: standard audit fields.

When viewing a person record, the entity relationship panel surfaces related entities and their relationship types. A spouse relationship shows Jane with role spouse. An employer relationship shows ACME Corp. An agent viewing John's entity record can see that Jane exists as John's spouse and navigate to Jane's entity record to see her summary. Jane's debts are not shown on John's record unless John has a direct entity-to-debt relationship on those debts.

## Entity-to-Debt Relationships and Role Types

A second bridge table governs relationships between entity records and debt records. This is distinct from entity-to-entity relationships and serves a different purpose: it defines who is associated with a debt and in what capacity. A debt can have multiple entity associations in different roles. An entity can appear on multiple debts in different roles.

> **ENTITY-TO-DEBT RELATIONSHIP BRIDGE SCHEMA**
>
> **entity_debt_relationship_pk**: UUID surrogate primary key.
>
> **entity_fk**: the entity associated with this debt.
>
> **debt_fk**: the debt.
>
> **role_type_fk**: reference value defining the role: responsible_party, co_maker, guarantor, patient, authorized_contact, deceased_estate_contact, and others.
>
> **is_responsible_party**: boolean flag. True for roles that carry financial liability for the debt. Drives entity aggregate balance calculations. Responsible party, co-maker, and guarantor are typically flagged true. Patient and authorized contact are typically false.
>
> **is_primary**: boolean, whether this is the primary responsible party when multiple responsible parties exist.
>
> **created_at, updated_at, created_by_user_fk, updated_by_user_fk**: standard audit fields.

Multiple relationship records between the same entity and the same debt are valid when the entity occupies multiple roles. A person who is both the responsible party and the patient on their own medical bill has two entity-to-debt relationship records for that debt. The is_responsible_party flag on each record determines whether each role contributes to entity aggregate balance calculations. The responsible-party role does. The patient role does not. No double-counting occurs because aggregates are computed by summing across debts where is_responsible_party is true, not across relationship records.

When an agent works a person, they see all debts where that person has any entity-to-debt relationship, labeled by role. John is shown as Primary RP on Debt A, Co-Maker on Debt B, and Patient on Debt C (the last of which carries no liability). The agent works John with full visibility of all associations without needing to navigate through separate screens.

## Entity Aggregate Fields

The entity record shows aggregate fields spanning all debts where the entity is a responsible party. Like the totals of a debt group, they are calculated when they are read and are never stored, and they are scoped to one entity's responsible-party associations across all debt groups.

> **ENTITY AGGREGATE BALANCE FIELDS**
>
> **total_initial_balance**: sum of placement amounts across all responsible-party debts.
>
> **open_debts_initial_balance**: sum of placement amounts for open responsible-party debts.
>
> **total_unpaid_balance**: sum of current balances across all responsible-party debts, excluding SIF writeoff remaining amounts.
>
> **open_debts_unpaid_balance**: unpaid balance for open responsible-party debts only.
>
> **total_balance_canceled**: sum of balances on responsible-party debts closed with a canceled status.
>
> **total_sif_writeoff_amount**: the forgiven portion across all settled responsible-party debts.
>
> **total_purchase_amount**: sum of purchase prices for responsible-party debts in debt buyer deployments. Contributed by the debt buyer module.
>
> **active_debt_count**: count of open responsible-party debts.
>
> **inactive_debt_count**: count of closed responsible-party debts.

Every amount field above is a sum of typed monetary values and is calculated per currency, as [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md) requires of any sum. A debt group holds debts of one currency ([HiveAR Design Decision 4](HIVE-0004-debt-groups.md)), so an entity whose responsible-party debts are in more than one currency has a debt group for each currency and stays associated with all of those debts. Such an entity has one value of each amount field for each currency, and no field adds amounts of different currencies. An entity whose responsible-party debts all share one currency, which is every entity in a single-currency installation, has one value of each amount field. The count fields are not amounts and are unaffected.

Aggregate fields are calculated when they are read, not maintained by workflows. When a payment posts to Debt A and John is a responsible party on Debt A, the payment changes the buckets of Debt A and nothing else, and John's fields reflect it the next time they are read. Whether any calculated field should also be materialized for speed is a later decision, recorded as the open question on materialized calculations.

## Side Notes Captured For Future Discussion

**Debt lineage**: prior instances of a debt (rollover, re-placement) need a separate relationship mechanism distinct from entity-to-debt relationships. The label for this mechanism is Debt Lineage.

**Itemization and service lines**: whether a charge is itself a debt, or only part of the itemization that supports one, depends on how the client tracks balances, as [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md) describes. An itemization is a core structure of static lines attached to the debt, and a debt-type module extends its lines, as a hospital's service lines do under [HiveAR Design Decision 9](HIVE-0009-debt-type-structure-extension.md). A charge that the client collects against is a debt, grouped with its siblings under [HiveAR Design Decision 4](HIVE-0004-debt-groups.md).

## Implementation Phasing

**HiveAR v1 (MVP):** Core implementation. ar.entity as the universal parent table. Person and Business subtypes with basic fields. Entity-to-debt relationships with role types (debtor, co-signer, guarantor, authorized contact). is_responsible_party flag on relationships. Entity aggregate fields (total balance, debt count) calculated when read. Entity-to-entity relationship table exists in the schema but can remain empty until v2 surfaces it in the UI.

**HiveAR v2:** Entity-to-entity relationships with UI. Business entity hierarchy support. Entity search and filtering. Materialized aggregate fields, if the open question on materialized calculations decides for them.

**HiveAR v3+:** Complex organizational structures. Entity timeline visualization.

**Breaking change risk: LOW.** The entity scaffold is straightforward. Ship the relationship tables even if empty.

## Implications For Contributors

Wax defines the entity scaffold only. Locale Module authors contribute name, address, and identity satellite tables. No module other than a Locale Module may contribute to the entity name or identity schema.

The is_responsible_party flag on entity-to-debt relationships is the single source of truth for whether a relationship feeds entity aggregate balance calculations, and for which debts a payer's undirected money may reach under HiveAR Design Decision 7. Module authors who contribute new role types must declare whether the role is a responsible-party role in the role type registry.

Entity aggregate amount fields are calculated per currency, and no calculation adds amounts of different currencies.

Entity aggregate fields are calculated when they are read and are never stored, so no workflow maintains them and no module writes to them.
