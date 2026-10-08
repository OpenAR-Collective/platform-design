---
id: HIVE-0005
title: "Account Structure and Balance Composition"
status: Accepted
version: 1.1
area: hivear
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 5: Account Structure and Balance Composition

## Decision

HiveAR will classify every account on two independent axes and compose its balance from typed buckets rather than fixed columns. The two classifiers are debt type, the category of the obligation such as healthcare, auto deficiency, or credit card, and contract type, the basis on which the agency holds the account, servicing, third-party contingency, or purchase. An account's balance is the sum of typed, labeled buckets whose definitions come from the loaded debt-type modules and the agency's own registry, never from the framework core. The model keeps three distinct kinds of money apart: debtor balance buckets that are owed and paid down, internal-confidential amounts such as purchase price that are never owed and never shown by default, and informational fields such as the pre-placement totals that are reference values rather than balances. Balances are not stored as mutable numbers; they are the running projection of immutable financial postings.

## The Framework Is Inert Without Modules

The platform rests on the founding tenet that the framework does nothing on its own. Wax does nothing without HiveAR, and HiveAR does nothing without a configuration: a locale for laws and address conventions, a language pack, and at least one debt-type module. An agency whose debt is too unusual for any module defines its own bucket definitions by hand. The balance bucket registry is therefore sourced entirely from the loaded debt-type modules and from agency-defined definitions, and the framework ships no bucket of its own and no default balance. A working configuration always has at least one bucket source, because a configuration without one is not a working configuration.

## Two Classifiers: Debt Type and Contract Type

Debt type is the category of the obligation: healthcare, auto deficiency, personal loan, commercial, rental, credit card, utility, and so on. Debt type selects the debt-type module, and the module supplies the buckets that category thinks in. A healthcare module brings a patient balance bucket and an insurance balance bucket, while a lending module brings principal, interest, and fee buckets. The framework privileges none of these, because interest is meaningless on most healthcare debt and a patient balance is meaningless on a credit card.

Contract type is the basis on which the agency holds the account: servicing, third-party contingency, or purchase. It is delineated at the contract, which is the client or creditor relationship, so an account inherits its contract type from the client it belongs to, and an agency keeps the same creditor's first-party and third-party work under separate client identities. Contract type drives lifecycle, ownership, the existence of a purchase price, and whether a current-due amount is a subset of the balance or the whole balance is due. Purchase makes the agency the current creditor, with the seller as the prior creditor and possibly a different original creditor behind that. The two classifiers are independent: a healthcare account may be third-party today and purchased tomorrow.

## Balances Are Projections of Postings

An account's balance is never a number that someone edits. It is the running sum of immutable financial events, charges, payments, adjustments, and accruals, each posting to one or more buckets, exactly as every other aggregate in the platform derives its state from its events. The bucket balances form the receivables sub-ledger, dimensioned by bucket, and the general ledger is the formal double-entry record. Both derive from the same posted events, so they reconcile by construction. This is why the GAAP-compliant journal and general ledger, specified in their own decision, are a v1 partner to this one rather than a later addition: a collection platform that cannot keep clean double-entry books against its own balances is not shippable, and those books post against the composition defined here.

## The Balance Bucket

A balance bucket is a typed, labeled component of an account's balance that carries attributes rather than hard-coded meaning. A bucket definition records whether the bucket bears interest, whether it counts toward any current-due amount, how payments apply to it, how commission and remittance treat it, and its origin, whether it was placed by the client or assessed by the agency after acquisition. The client-interest-versus-agency-interest distinction is then an instance of the origin attribute rather than a special case, and the legal module's pre-judgment and post-judgment interest are two interest buckets with different origins and accrual rules.

Bucket definitions live in an agency-level registry, seeded by the loaded debt-type modules and extended by the agency, and a definition added for one purpose is reusable everywhere. Buckets attach to accounts sparsely and dynamically: a bucket attaches to an account only where it carries a balance, so defining a rental-fee bucket does not place a zero row on every credit card account. A bucket instance on an account is the running sum of the postings to that bucket on that account, and the account's balance is the sum of its attached instances.

## Three Amount Categories

Three kinds of money live on an account, and conflating any two of them is the classic data-model failure this decision forecloses. Debtor balance buckets are what the consumer owes and what payments apply to. Internal-confidential amounts, the purchase price above all, are never debtor balances, never paid down, and never shown to agents or consumers by default; they exist for finance and analytics. Informational fields, such as the pre-placement total charges, total payments, and total adjustments, the original loan amount, and the itemization-date figures, are dated reference values used on letters and for reconciliation rather than amounts that are owed. A bucket is owed, a purchase price is internal, and an informational figure is neither; the model keeps the three apart at the root. The dates these figures are keyed to, including the five reference dates described below, are civil dates, as defined in [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md).

## Denomination Currency

An account is denominated in one currency, and every amount on it is a typed monetary value in that currency, as defined in [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md): the bucket balances, the informational figures such as the pre-placement totals and the original loan amount, and the postings that move them. In an installation whose Region Packs name one currency, the account takes that currency as its default and no one specifies it. In an installation that holds more than one currency, the account takes its currency from its contract or client, so that a payment, an import, and a statement never have to guess it. All accounts in an account set share one currency, as [HiveAR Design Decision 4](HIVE-0004-account-sets.md) provides, so a person with accounts in two currencies has a set for each. Purchase price is typed money like every other amount and names its own currency, the one in which the purchase was paid, which need not be the account's.

## The Itemization Date

Regulation F requires a validation notice to itemize the current amount of the debt as interest, fees, payments, and credits since an itemization date, and that itemization is expected to reconcile to the current balance. The itemization date is one of five reference dates: the last statement date, the charge-off date, the last payment date, the transaction date, or the judgment date. HiveAR stores all five candidate dates that the client provides and lets the agency configure a rank order, selecting the highest-ranked non-null candidate as the account's itemization date. A collector must choose a reference date and use it consistently, which the rank order satisfies while degrading gracefully when a client omits some dates. The itemization date is required at account approval, alongside a balance and a responsible party, and the pre-placement informational totals key to it.

## Purchase Price and Internal Confidentiality

Purchase price is a confidential field on the account aggregate, not a separate hidden structure. Its visibility is governed by role-based access control and the view layer, so agent-facing and consumer-facing views never project it by default, and an agency that wants its agents to see it can build a screen that does. Account-level purchase price supports portfolio return analysis, cross-portfolio grouping such as return by jurisdiction, and the refund owed on a buyback. It is stored per account even when a portfolio is bought for a single lump sum, because the analytical value lies in the per-account figure. Purchase price introduces a sensitivity axis the platform has not needed before: internal-confidential data is commercially sensitive rather than personal, a role-gated visibility distinct from the personal-information protection that encryption and crypto-shredding provide.

## Current Due Is Derived

The amount currently due is derived, not stored, and its derivation depends on contract type. For third-party contingency and purchased accounts, the whole balance is due, so the current-due amount is the full balance. For serviced accounts, the current-due amount is the scheduled next payment, a subset of the balance. HiveAR ships third-party and purchase first, so v1 computes whole-balance-due, and the current-due-as-a-subset concept is carried as a known-future capability that arrives with the servicing contract type in v2. Modeling current-due as derived from the start means that adding servicing later changes a derivation rather than the stored shape.

## Scope and What Branches Off

This decision establishes the composition framework and deliberately stops there. It does not specify payment application and waterfall sequencing, which is its own decision consuming bucket attributes; the GAAP journal and general ledger, the v1 partner decision that posts from the same events; client commission, fee retention, and remittance, including gross-versus-net remit and per-account or per-seat billing; interest accrual, which is a process that writes to interest buckets; or the buy, sell, and buyback portfolio transactions, which straddle account lineage and the ledger. It is distinct from itemized charge detail and service lines, the line-item breakdown of original charges such as hospital service lines and procedure codes, which is a separate sub-account structure and remains its own pending decision. The debt-type modules supply their own buckets and domain detail, and the legal module stays a module so that an agency that does not litigate carries none of its buckets; this decision's only obligation to those modules is to prove the bucket model can absorb their buckets, which it does.

## Implementation Phasing

**HiveAR v1 (MVP):** The two classifiers, with contract types third-party contingency and purchase, the balance bucket primitive and the agency-level registry, sparse and dynamic attachment, the three-category amount taxonomy, the denomination currency of each account, the itemization-date model, purchase price as a confidential account field, and whole-balance-due. At least one debt-type module is required for a working install. This composition is the foundation the v1 GAAP journal and general ledger post against.

**HiveAR v2:** The servicing contract type and the current-due-as-a-subset derivation.

**HiveAR v3+:** Additional contract types and amount categories as the platform's reach expands, all of them additive to the model defined here.

**Breaking change risk: LOW. The model is additive: new buckets, new bucket attributes, new debt types, and new contract types extend it without disturbing existing data. The foundational commitments, balances as projections of postings and the separation of the three amount categories, are stable because they derive from the event-sourcing the platform already rests on. Getting the bucket primitive and the amount taxonomy right early matters, since they are the base the journal, payment application, and client billing all build on.**

## Implications For Contributors

Balances are computed, never stored and edited. Every change to a balance flows through a posted financial event to a bucket, and no code path may set a balance directly.

The core ships no buckets. Bucket definitions come from debt-type modules and the agency registry. A contributor must not bake a default bucket or a default balance into the framework.

The three amount categories stay separate. Purchase price and informational totals are never treated as debtor balance, never paid down, and never summed into the owed amount.

Purchase price is internal-confidential. It must never be projected into an agent-facing or consumer-facing view by default, and its visibility is governed only through role-based access control.

Every amount on an account is a typed monetary value in the account's denomination currency, except purchase price, which names its own. No bucket, informational figure, or posting is a bare number, and the five reference dates are civil dates.
