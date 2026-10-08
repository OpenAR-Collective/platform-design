---
id: HIVE-0007
title: "Payment Application and Waterfall"
status: Accepted
version: 1.1
area: hivear
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 7: Payment Application and Waterfall

## Decision

HiveAR will apply each incoming payment or credit to an account's balance buckets through a configurable waterfall, an ordered priority that determines which buckets a payment pays down and in what order. Application is the distribution step that decides where money lands; the general ledger from [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) is the posting step that books the result. When a debtor owes multiple accounts and makes one payment, the payment is first allocated across accounts, honoring the consumer's directions and excluding any disputed account as Federal law requires, and then each account's waterfall runs. Any money remaining after all eligible buckets are satisfied becomes the consumer credit balance from [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md).

## Application Decides Where Money Lands; the Ledger Decides How It Books

This decision owns the distribution of a payment across buckets and produces the per-bucket paydown amounts. [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) then posts those amounts, recognizing commission on the debt paid down and splitting it according to each bucket's treatment. The separation is clean: application determines where the money goes, and the ledger determines how that money books. The same engine serves a fresh payment and the application of a held credit balance, because both are debt paydown, which is why a credit applied to another account flows through this waterfall exactly as a new payment would.

## The Waterfall Is a Configurable Ordered Priority Over Buckets

A waterfall is an ordered list of buckets, and a payment fills them in order until it is exhausted. Because the buckets from [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) are already typed, the familiar question of whether to pay off a whole bucket before the next or to pay a component such as interest across everything first collapses into ordering: paying interest before principal is simply ranking the interest buckets ahead of the principal buckets. The waterfall references bucket definitions from the agency registry and resolves against the buckets actually attached to the account, skipping any that are absent, so a waterfall that names a bucket the account does not carry passes over it without incident.

Defaults come from modules and overrides from configuration, consistent with the founding tenet. A debt-type module ships a sensible default waterfall for the buckets it contributes, and the agency or a client contract overrides it as versioned configuration under [Wax Design Decision 21](../wax/WAX-0021-configuration-management-and-environment-lifecycle.md). When more than one override applies, the contract takes precedence over the client, the client over the agency, and the agency over the module default. The contract is the finest configured grain, which keeps a bare install functional while letting clients impose the complex application sequences described in [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md).

## Per-Payment Override at Posting

The configured waterfall is the default path, not a constraint on the payment-taker. Whoever posts a payment, a cashier on the phone with the consumer, a file import, or an API caller, may override the waterfall by specifying explicit bucket amounts for that payment. There is no separate override permission, because the authority to take a payment is the authority to direct it: a payment-taker may at any moment be receiving the consumer's instructions about how to apply it, so the two cannot be separated. An override applies only to the payment that carries it and does not alter the account's configured waterfall.

## Multiple Debts and the Federal Floor

When a debtor owes more than one account and makes a single payment, Federal law governs how it is allocated across those accounts. Under the Fair Debt Collection Practices Act, a collector may not apply any part of the payment to a disputed account, and must apply the payment in accordance with the consumer's directions. A dispute may be raised orally, and the exclusion still binds. HiveAR treats this as a non-negotiable floor: the consumer's allocation directions are honored above any default, and an account flagged as disputed is excluded from any allocation the consumer did not specifically direct.

Above that floor, HiveAR offers configured cross-account allocation for the common case where the consumer gives no specific direction. Version 1 provides two options, an even split across the accounts in the set and oldest-first by list date, and later versions add more as agencies ask for them. The allocation across accounts runs first, and then each account's bucket waterfall runs on its share.

## Currency in Application

A payment carries one currency, and the waterfall runs in the currency of the account it pays. A payment in a currency other than the account's is converted first, and the conversion is an explicit recorded act under [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md), so a bucket is never paid in a currency it does not hold. The same holds when one payment is allocated across several accounts: the accounts share the payment's currency, or each share carries a recorded conversion, and an allocation that would mix currencies without one fails instead of guessing. In a single-currency installation every payment and every account share the one currency, and none of this is visible.

## Payment Arrangements Carry a Persisted Application Directive

A consumer's direction can endure rather than apply only once. When a consumer sets up a payment arrangement and states how the payments should be applied, that instruction persists, so each scheduled payment applies the same way without re-asking. This decision models that persisted application directive, the standing instruction an arrangement payment carries into the waterfall, because honoring it is a continuation of the same consumer-direction rule that governs a single payment. It does not model the arrangement itself, the installment schedule, the amounts and due dates, promise tracking, and broken-arrangement handling, which is a separate decision that will reuse this directive.

## Reversals Unwind the Original Distribution

A returned payment is reversed by backing out the exact distribution the original application produced, both the allocation across accounts and the per-bucket paydown within each, rather than by recomputing against the current configuration. Because the original distribution is recorded in the event stream, the reversal is faithful even when the waterfall configuration has changed since the payment posted. The ledger entries reverse in step, as described in [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md), and the reversal reduces the next remittance.

## Scope and Boundaries

This decision covers the distribution of payments and credits across accounts and buckets, the configurable waterfall, the per-payment override, the Federal multiple-debt floor, the v1 cross-account allocation options, and the persisted application directive. It does not set commission rates or the rules that calculate the split, which belong to the client-billing decision and which the ledger consumes. Settlements, where a consumer resolves an account for less than the full balance, are a complex area with their own decision; this waterfall applies the settlement payment, and the forgiven remainder is a balance adjustment under HiveAR Design Decisions 5 and 6 with no revenue reversal, since it was never collected. The full payment-arrangement definition is likewise its own decision and reuses the directive defined here. The interaction between the waterfall and itemized line-item charge detail is deferred to the charge-detail decision, since this waterfall operates over an account's buckets.

## Implementation Phasing

**HiveAR v1 (MVP):** The configurable bucket waterfall with module-supplied defaults and contract-over-client-over-agency overrides. The per-payment bucket-amount override available to any payment-taker, whether cashier, file import, or API. The Federal multiple-debt floor of consumer-directed allocation and disputed-account exclusion. Two cross-account allocation options, even split across the set and oldest-first by list date. Application of held credit balances through the same waterfall. The persisted application directive that an arrangement payment carries. Reversals that unwind the original distribution.

**HiveAR v2:** Pro-rata distribution across equal-priority buckets within a waterfall tier, with its rounding rule, which rounds each share to the currency's minor unit under the rounding convention that the currency's Region Pack supplies. Additional cross-account allocation options as agencies request them.

**HiveAR v3+:** Further allocation strategies and sequencing refinements as feedback warrants, all additive to the waterfall model defined here.

**Breaking change risk: LOW. Application consumes the [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) buckets and feeds the [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) ledger without changing either, and the waterfall, the allocation options, and the override are additive. The Federal multiple-debt floor is a correctness-critical behavior to get right at the start, since misapplied or wrongly directed payments are a compliance exposure, but the model itself is stable because it rests on the existing bucket and event-sourcing foundations.**

## Implications For Contributors

Application distributes; the ledger posts. This decision produces per-bucket paydown amounts, and [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) books them. No code in the application path may post to the general ledger or compute commission directly.

The Federal multiple-debt floor is absolute. Consumer allocation directions are honored above any default, and a disputed account is never paid from a payment the consumer did not direct to it. This rule may not be overridden by configuration.

A payment-taker may always direct a payment. The right to post a payment includes the right to override the waterfall with explicit bucket amounts, and no separate permission gates it.

Reversals unwind the recorded distribution, never a recomputed one. A reversal backs out the exact allocation and per-bucket amounts the original application produced, read from the event stream.

The waterfall runs in the account's currency. A payment in another currency is converted by a recorded act before it applies, and no allocation mixes currencies without one.
