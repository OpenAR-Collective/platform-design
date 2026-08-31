---
id: HIVE-0004
title: "Account Sets"
status: Accepted
version: 1.0
area: hivear
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 4: Account Sets

## Decision

Every account in HiveAR belongs to exactly one Account Set at all times. This is a core architectural invariant, not a configurable feature. Account Sets are the unit of coordinated collection activity: when an agency collects from a person who has multiple accounts with the same client, those accounts are grouped in a set and collection activity addresses the set as a whole while each account retains individual sovereignty over its own balance, lifecycle, and debt identity. The account_set_fk on the account table is non-nullable. No code path exists for an account without a set.

## Account Set as Core Architecture

The forced-single-set model is the correct design because it eliminates conditional logic throughout the system. Letter templates, reporting queries, workflow conditions, and agent UI panels never need to branch on whether an account is grouped. Every account always has a set. A single-account set produces the same data structure as a thousand-account set. Aggregate fields on a single-account set simply reflect that one account's values.

A set is created automatically when an account is created. The new set receives the new account as its sole member. If the account is subsequently grouped with other accounts, the grouping operation moves the account into an existing set. The original single-member set is then orphaned and administratively closed. This means account sets are a background infrastructure concern: agencies that never explicitly group accounts still benefit from the uniform data model because their accounts are always single-member sets.

## Account Set Schema

> **ACCOUNT SET CORE FIELDS**
>
> **account_set_pk**: UUID surrogate primary key. i18n name and description: follow the full i18n architecture. Agency-defined set names are optional but supported for named groups such as 'Jones Family' or 'Northside Medical Group'.
>
> **status_fk**: reference value pointing to an agency-defined status code. Status represents the operational collection posture of the set: payment_arrangement, dispute, holding, bankruptcy, legal, and others the agency defines. The standard seed pack delivers a starting set of status codes. Status is separate from and orthogonal to the is_active flag.
>
> **is_active**: boolean. True if one or more member accounts are active. False if all member accounts are inactive. Maintained by the event-driven workflow path.
>
> **is_locked**: boolean. True when a lock is in effect, typically from a legal hold. Prevents accounts from being added to or removed from the set while locked.
>
> **is_orphaned**: boolean. True when no accounts reference this set. Set by the orphan detection workflow when the last account leaves the set.
>
> **active_account_count**: integer. Count of active member accounts. Maintained by event-driven workflows.
>
> **inactive_account_count**: integer. Count of inactive member accounts.
>
> **client_scope_fk**: the client this set belongs to. Default is the client of the founding account. Cross-client sets are reserved for future client hierarchy work.
>
> **ACCOUNT SET AGGREGATE BALANCE FIELDS**
>
> **total_initial_balance**: sum of placement amounts for all member accounts regardless of status.
>
> **open_accounts_initial_balance**: sum of placement amounts for active member accounts only.
>
> **total_unpaid_balance**: sum of current balances across all member accounts, excluding SIF writeoff remaining amounts.
>
> **open_accounts_unpaid_balance**: unpaid balance for active member accounts only.
>
> **total_balance_canceled**: sum of balances on member accounts closed with a canceled status.
>
> **total_sif_writeoff_amount**: the forgiven portion across all settled member accounts.
>
> **total_purchase_amount**: sum of purchase prices for member accounts in debt buyer deployments. Contributed by the debt buyer module.

All aggregate fields are maintained by event-driven workflows through the command handler path. A payment posted to a member account fires a workflow that updates the set's total_unpaid_balance. An account closing fires a workflow that decrements active_account_count and recalculates is_active. Read queries against the set record read cached values. No aggregate computation happens at query time.

## Set Lifecycle and State Flags

is_active and is_locked are independent boolean flags. is_active reflects member account composition. is_locked reflects an external hold condition. A set can be any combination: active and unlocked (normal working set), active and locked (legal hold on a set with open accounts), inactive and unlocked (all accounts closed, no hold), inactive and locked (all accounts closed but legal proceedings still open pending court closure).

The status code is the third independent dimension. It represents the operational approach to the collection effort on the set, not the composition of the set or the presence of a lock. A set can be in payment_arrangement status while is_locked is false and is_active is true. A set can be in dispute status while all its accounts have individually resolved. The status is the agency's declared posture; the flags are the system's derived state.

is_orphaned is set by the orphan detection workflow when active_account_count plus inactive_account_count reaches zero. An orphan occurs when all member accounts have been moved to other sets. The orphaned set is administratively closed but its record is preserved for audit purposes. Its aggregate field snapshots remain as a historical record of what the set contained before it was emptied.

## Account Movement: The Single Code Path

Moving an account from one set to another is the single operation for all set membership changes. There is no separate merge operation, no separate split operation, and no separate dissolve operation. All of these are achieved by moving accounts one by one between sets. When all accounts from Set A have been moved to Set B, Set A becomes orphaned and is automatically closed. When some accounts from Set A are moved to a new Set C while others remain in Set A, Set A is effectively split.

The move account operation checks whether the source set is locked before executing. A locked set does not permit account movement. The lock must be released through the appropriate event (legal case closure, hold release) before accounts can move.

## Split Behavior and New Set Initialization

When accounts are moved from an existing set to a newly created set, the new set inherits the status_fk of the source set as an initial value. Status inheritance is pragmatic: if an agency splits a set in dispute status, it is likely that both resulting sets are also in dispute until further action resolves one. Status is not permanently bound by inheritance; either set's status can be changed independently after the split.

is_active on the new set is computed fresh from its member accounts at creation time. If a closed account is moved from an active set into a new set, the new set starts as inactive because its only member is inactive. is_locked is not inherited: the lock condition applies to the original set and is not automatically propagated to a new set created by moving accounts out. Accounts that are locked cannot be moved in the first place, so accounts arriving in a new set are by definition unlocked.

Aggregate balance fields on the new set are computed fresh from its member accounts at creation time. The source set's aggregate fields are updated to reflect the removal of the moved accounts.

## Legal Module and Set Locking

When a set of accounts is included in a legal case, the legal module sets is_locked to true on the account set. This prevents accounts from being added to or removed from the set while the legal action is pending. All accounts named in a legal case must be in the same account set, and the set's membership is treated as a defined legal unit. Adding or removing accounts from a case after filing requires a formal legal event (amendment, partial dismissal) which triggers a corresponding change to the set lock and membership through the command handler path.

## Side Notes Captured For Future Discussion

**Legal module architecture**: the full legal case lifecycle, how accounts are associated with cases, what happens to set membership and lock state during appeals and re-filings, and the interaction between legal status and account status codes.

**Account lineage**: prior instances of an account created by rollover or re-placement are a distinct concept from account set membership. A prior instance relationship records that Account B is a re-placement of Account A. Prior instances are never simultaneously active. The display label for this relationship is Account Lineage.

## Implementation Phasing

**HiveAR v1 (MVP):** Full implementation, simplified. ar.account_set table with the full schema. Forced single-set architecture (every account belongs to exactly one set). is_active, is_locked, is_orphaned as independent boolean flags. The single code path for all set membership changes. Basic set lifecycle. No legal module set locking in v1: the is_locked flag exists but nothing sets it automatically. No automated split detection.

**HiveAR v2:** Legal module integration (automatic set locking on legal placement). Automated orphaned set detection. Set-level aggregate calculations.

**HiveAR v3+:** Complex set splitting rules. Set-level workflow triggers.

**Breaking change risk: LOW.** Account Sets are a well-understood concept. The schema is stable.

## Implications For Contributors

The account_set_fk on the account table is non-nullable. Any command handler that creates an account must also create a single-member account set and assign the new account to it within the same atomic transaction.

Account aggregate field updates must flow through the event-driven workflow path. No module may directly write to account set aggregate fields.

Wax-delivered workflows that maintain set aggregate fields are system infrastructure. Module authors must not create workflows that conflict with or duplicate these Wax workflows. The Wax workflow registry documents which events are handled by system workflows.

The set status code reference type is agency-defined. The seed pack delivers standard starting codes. Module authors may add module-specific status codes through the Collective's contribution process but should not define status codes that duplicate or contradict the standard seed pack codes.
