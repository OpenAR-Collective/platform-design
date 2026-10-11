---
id: HIVE-0004
title: "Debt Groups"
status: Accepted
version: 3.0
area: hivear
date: 2026-10-10
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 4: Debt Groups

## Decision

Every debt in HiveAR belongs to exactly one debt group at all times, and debt groups nest into a hierarchy of any depth that a grouping scheme defines. This is a core architectural invariant, not a configurable feature. A grouping scheme is an ordered list of grouping levels, such as patient, visit, and invoice for a physician practice, or a single level for an agency that never groups beyond one person's debts with one client. Schemes and their levels are defined independently of any client, and configuration decides where each scheme applies: agency-wide, to a debt type, or to a client. Exactly one level of every scheme is the working level. The debt group at the working level is the unit of coordinated collection activity: when an agency collects from a person who has multiple debts with the same client, those debts sit in one working-level group and collection activity addresses the group as a whole, while each debt retains individual sovereignty over its own balance, lifecycle, and identity. All debts in a working-level group are denominated in the same currency, so a person with debts in more than one currency has a separate group for each currency. The person stays associated with every one of those debts through the entity-to-debt relationships of [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), and only the grouping is by currency. Which records are debts, and which are only part of the itemization that supports a debt, depends on how the client tracks balances, as [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md) describes. The debt_group_fk on the debt table is non-nullable. No code path exists for a debt without a group.

## Debt Group as Core Architecture

The forced-single-group model is the correct design because it eliminates conditional logic throughout the system. Letter templates, reporting queries, workflow conditions, and agent UI panels never need to branch on whether a debt is grouped or on how deep the grouping goes. Every debt always has a group at every level of its scheme. A debt in a single-level scheme produces the same data structure as a debt in a five-level scheme, and a group with one debt produces the same structure as a group with a thousand. Aggregate fields on a one-debt group simply reflect that one debt's values.

When a debt is created, its group at each level of its scheme is found or created. A placement that carries an identifier for a level, such as a patient number or an invoice number, finds the group that already holds that identifier for that client, or creates it. A level for which the placement carries no identifier gets a new single-member group, exactly as a debt in an agency that never groups gets a single-member group at the working level. If the debt is subsequently grouped with other debts, the grouping operation moves the debt into an existing group. The original single-member group is then orphaned and administratively closed. This means debt groups are a background infrastructure concern: agencies that never explicitly group debts still benefit from the uniform data model because their debts are always single-member groups.

## Grouping Schemes and Levels

A grouping scheme is a named, reusable definition of the levels above the debt, ordered from the lowest to the highest. A grouping level carries an internationalized name and description under the full i18n architecture, a singular and a plural label, its position in the scheme, the identifier types that identify a group at that level, a flag that names it the working level, and a flag that says whether groups at that level keep aggregate balance fields. Every scheme has exactly one working level, and the working level always keeps aggregate balance fields. Schemes and levels are configuration, not code. They are versioned configuration items under [Wax Design Decision 21](../wax/WAX-0021-configuration-management-and-environment-lifecycle.md), and they are not stored on any client record, so one scheme can serve many clients, and a client can be assigned a different scheme for its new placements without anyone redefining levels.

Following the founding tenet that the framework is inert without modules, the core ships no named level beyond the one the invariant needs. It ships a built-in scheme with a single level, the working level, so that a bare install satisfies the invariant. Debt-type modules seed the schemes their debt thinks in, as they seed buckets and role types: a physician-billing configuration can seed a scheme whose levels are invoice, visit, and patient with the patient level as the working level, and a toll configuration can seed one whose levels are notice and vehicle. The agency can define its own schemes in the registry and extend the seeded ones. A scheme added for one purpose is reusable everywhere.

## Applying a Scheme

A scheme assignment is a configuration record that says where a scheme applies. A scheme can be assigned agency-wide as the default, to a debt type, which the industry also calls the asset class, or to a client. When more than one assignment applies to a debt, the most specific one wins: the client over the debt type, the debt type over the agency, and the built-in single-level scheme as the final fallback. This is the same override ladder that [HiveAR Design Decision 7](HIVE-0007-payment-application-and-waterfall.md) uses for waterfalls. An assignment can carry label overrides for the levels of its scheme, so that one client's staff see that client's own word for a level, such as an encounter where another client says a visit.

The scheme is recorded on the debt when the debt is created and does not change afterward, because every group belongs to the levels of one scheme. Changing a debt's scheme after placement is a regrouping that this decision leaves to later work.

## Identifiers

A debt does not have to carry an account number. Debts and debt groups carry any number of typed identifiers, drawn from an identifier type registry that debt-type modules seed and the agency extends: a charge identifier, a claim number, a visit identifier, an invoice number, a patient number, a plate and state, a client reference. An identifier type has an internationalized name and a value type, and an assignment can relabel it for a client in the same way it relabels a level. The core requires no identifier. The identifiers a placement carries are what the find-or-create step uses to place a debt into its groups, and every identifier is searchable. A visit date is an identifier whose value is a civil date, as defined in [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md). The other dates that describe a visit, a service, or a transaction belong to the structure that a debt-type module attaches under [HiveAR Design Decision 9](HIVE-0009-debt-type-structure-extension.md) and are not identifiers.

## Debt Group Schema

> **DEBT GROUP CORE FIELDS**
>
> **debt_group_pk**: UUID surrogate primary key. i18n name and description: follow the full i18n architecture. Agency-defined group names are optional but supported for named groups such as 'Jones Family' or 'Northside Medical Group'.
>
> **grouping_level_fk**: the level of the debt's scheme at which this group sits.
>
> **parent_debt_group_fk**: the group one level up. Null only for a group at the highest level of its scheme.
>
> **status_fk**: reference value pointing to an agency-defined status code. Status represents the operational collection posture of the group: payment_arrangement, dispute, holding, bankruptcy, legal, and others the agency defines. The standard Boilerplate Pack delivers a starting set of status codes. Status is separate from and orthogonal to the is_active flag. Status is carried by working-level groups.
>
> **is_active**: boolean. True if one or more debts beneath the group are active. False if all of them are inactive. Maintained by the event-driven workflow path.
>
> **is_locked**: boolean. True when a lock is in effect, typically from a legal hold. Prevents debts from being added to or removed from the group, or from any group beneath it, while locked.
>
> **is_orphaned**: boolean. True when no debts remain beneath this group. Set by the orphan detection workflow when the last debt leaves.
>
> **active_debt_count**: integer. Count of active debts beneath the group at any depth. Maintained by event-driven workflows.
>
> **inactive_debt_count**: integer. Count of inactive debts beneath the group at any depth.
>
> **client_scope_fk**: the client this group belongs to. Default is the client of the founding debt. Cross-client groups are reserved for future client hierarchy work.
>
> **currency_code**: the ISO 4217 code of the currency in which every debt beneath the group is denominated. It is set from the founding debt when the group is created and does not change. Every working-level group has one. A group above the working level has one only when its level keeps aggregate balance fields.
>
> **DEBT GROUP AGGREGATE BALANCE FIELDS**
>
> **total_initial_balance**: sum of placement amounts for all debts beneath the group regardless of status.
>
> **open_debts_initial_balance**: sum of placement amounts for active debts beneath the group only.
>
> **total_unpaid_balance**: sum of current balances across all debts beneath the group, excluding SIF writeoff remaining amounts.
>
> **open_debts_unpaid_balance**: unpaid balance for active debts beneath the group only.
>
> **total_balance_canceled**: sum of balances on debts beneath the group closed with a canceled status.
>
> **total_sif_writeoff_amount**: the forgiven portion across all settled debts beneath the group.
>
> **total_purchase_amount**: sum of purchase prices for debts beneath the group in debt buyer deployments. Contributed by the debt buyer module.

Every debt beneath a group that keeps aggregate balance fields is denominated in the group's currency, so each amount field above is a sum of monetary values in that one currency, stored with the group's currency_code as [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md) provides for a row whose amounts share one currency. No group adds amounts of different currencies. The count fields are not amounts and are unaffected.

Only the levels that keep aggregate balance fields carry the aggregate fields above, and the working level always does. A level above the working level can keep them when the agency wants totals there, such as a patient total across visits, and leaves them off otherwise. Keeping fewer aggregates means fewer rows to update when a payment posts.

All aggregate fields are maintained by event-driven workflows through the command handler path. A payment posted to a debt fires a workflow that updates the aggregate fields of every group above the debt that keeps them. A debt closing fires a workflow that decrements the active count and recalculates is_active in each of those groups. Read queries against a group record read cached values. No aggregate computation happens at query time.

## Group Lifecycle and State Flags

is_active and is_locked are independent boolean flags. is_active reflects the composition of the debts beneath the group. is_locked reflects an external hold condition. A group can be any combination: active and unlocked (normal working group), active and locked (legal hold on a group with open debts), inactive and unlocked (all debts closed, no hold), inactive and locked (all debts closed but legal proceedings still open pending court closure).

The status code is the third independent dimension. It represents the operational approach to the collection effort on the working-level group, not the composition of the group or the presence of a lock. A group can be in payment_arrangement status while is_locked is false and is_active is true. A group can be in dispute status while all its debts have individually resolved. The status is the agency's declared posture; the flags are the system's derived state.

is_orphaned is set by the orphan detection workflow when the count of debts beneath a group reaches zero. An orphan occurs when all debts have been moved to other groups. The orphaned group is administratively closed but its record is preserved for audit purposes, at every level. Its aggregate field snapshots remain as a historical record of what the group contained before it was emptied.

## Debt Movement: The Single Code Path

Moving a debt from one debt group to another is the single operation for all group membership changes. There is no separate merge operation, no separate split operation, and no separate dissolve operation. All of these are achieved by moving debts one by one between groups. When all debts from Group A have been moved to Group B, Group A becomes orphaned and is automatically closed. When some debts from Group A are moved to a new Group C while others remain in Group A, Group A is effectively split. A debt moves from its group at the lowest level to another group at that level of the same scheme, and its membership at every level above changes with it.

The move operation checks whether any group on the source path or the target path is locked before executing. A locked group does not permit a debt to move into or out of it, or out of any group beneath it. The lock must be released through the appropriate event (legal case closure, hold release) before debts can move.

The move operation also checks currency. A debt moves only into a group chain that has its currency, and a move that would mix currencies in the working-level group, or in any group above it that keeps aggregate balance fields, is refused. A person's debts in another currency stay in groups of their own. A move also stays within one scheme and one client.

## Split Behavior and New Group Initialization

When debts are moved from an existing group to a newly created group, the new group inherits the status_fk of the source working-level group as an initial value. Status inheritance is pragmatic: if an agency splits a group in dispute status, it is likely that both resulting groups are also in dispute until further action resolves one. Status is not permanently bound by inheritance; either group's status can be changed independently after the split. The new group takes the currency of the debts moved into it, which all share one.

is_active on the new group is computed fresh from the debts beneath it at creation time. If a closed debt is moved from an active group into a new group, the new group starts as inactive because its only debt is inactive. is_locked is not inherited: the lock condition applies to the original group and is not automatically propagated to a new group created by moving debts out. Debts that are locked cannot be moved in the first place, so debts arriving in a new group are by definition unlocked.

Aggregate balance fields on the new group are computed fresh from the debts beneath it at creation time. The source group's aggregate fields are updated to reflect the removal of the moved debts.

## Legal Module and Group Locking

When debts are included in a legal case, the legal module sets is_locked to true on the working-level debt group. This prevents debts from being added to or removed from the group while the legal action is pending. All debts named in a legal case must be in the same working-level debt group, and the group's membership is treated as a defined legal unit. Adding or removing debts from a case after filing requires a formal legal event (amendment, partial dismissal) which triggers a corresponding change to the group lock and membership through the command handler path.

## Side Notes Captured For Future Discussion

**Legal module architecture**: the full legal case lifecycle, how debts are associated with cases, what happens to group membership and lock state during appeals and re-filings, and the interaction between legal status and debt status codes.

**Debt lineage**: prior instances of a debt created by rollover or re-placement are a distinct concept from debt group membership. A prior instance relationship records that Debt B is a re-placement of Debt A. Prior instances are never simultaneously active. The display label for this relationship is Debt Lineage.

**Compliance unit**: when each charge is a debt, which level of the hierarchy a validation notice, a dispute, a cease-communication request, and a payment arrangement attach to, so that a charge-level debt does not multiply notices. The regional rules that bear on this need verification by someone with compliance standing. This is recorded as an open question.

**Group-level entity relationships**: in version 1 an entity is related to debts, as [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md) describes. Whether an entity can instead be related to a group and inherited by every debt beneath it, such as a guarantor for a patient, is recorded as an open question.

## Implementation Phasing

**HiveAR v1 (MVP):** Full implementation, simplified. ar.debt_group with the full schema, including grouping_level_fk and parent_debt_group_fk. The grouping scheme and level registry with the built-in single-level scheme, and scheme assignment at the agency, debt type, and client scopes. The typed identifier registry and identifiers on debts and groups. Find-or-create of groups at every level when a debt is placed. Forced single-group membership at every level. Aggregate fields at the working level and at any level that asks for them. is_active, is_locked, and is_orphaned as independent boolean flags. The single code path for debt moves. Basic group lifecycle. No legal module group locking in v1: the is_locked flag exists but nothing sets it automatically. No automated split detection.

**HiveAR v2:** Moving a whole group, with everything beneath it, to another parent. Legal module integration (automatic group locking on legal placement). Automated orphaned group detection at every level. Group-level aggregate calculations.

**HiveAR v3+:** Changing a debt's scheme after placement. Complex group splitting rules. Group-level workflow triggers.

**Breaking change risk: LOW.** The hierarchy is part of the schema from the start, so adding a scheme, a level, or an identifier type changes configuration and not structure. The elements to get right at the foundation are the working level and the one-group-per-debt invariant at every level.

## Implications For Contributors

The debt_group_fk on the debt table is non-nullable. Any command handler that creates a debt must find or create the debt's group at every level of its scheme, and assign the debt to its lowest-level group, within the same atomic transaction.

Never assume a level by name. Code reads the working level, the level order, and the labels from the debt's scheme, and does not assume levels called account, set, patient, or anything else. The core ships one level, and everything else is configuration.

Debt group aggregate field updates must flow through the event-driven workflow path. No module may directly write to debt group aggregate fields.

A working-level debt group holds debts of one currency, and so does any group above it that keeps aggregate balance fields. Any command handler that creates a debt or moves one between groups keeps that true, and a move that would mix currencies is refused.

Wax-delivered workflows that maintain group aggregate fields are system infrastructure. Module authors must not create workflows that conflict with or duplicate these Wax workflows. The Wax workflow registry documents which events are handled by system workflows.

The group status code reference type is agency-defined. The Boilerplate Pack delivers standard starting codes. Module authors may add module-specific status codes through the Collective's contribution process but should not define status codes that duplicate or contradict the standard Boilerplate Pack codes.

Schemes, levels, and identifier types seeded by a module are registry entries, not hard-coded structure, the same discipline as buckets, role types, and reason codes. A module that seeds a scheme declares which level is the working level.
