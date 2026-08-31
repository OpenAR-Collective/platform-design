---
id: HIVE-0006
title: "GAAP Journal and General Ledger"
status: Accepted
version: 1.0
area: hivear
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 6: GAAP Journal and General Ledger

## Decision

HiveAR will maintain a GAAP-compliant double-entry journal and general ledger for the AR money it handles, as a subsystem of the agency's true accounting system rather than a replacement for it. It keeps its own internal, AR-focused chart of accounts so it can post balanced double-entry and reconcile, maps those accounts to the agency's external chart-of-account codes by configuration, and exports journal entries to the agency's accounting system. The ledger records the agency's own money: consumer payments and reversals, the commission split, client balances, and the funds held in trust. It is the authoritative record of those AR transactions, and it feeds the enterprise books rather than becoming them.

## A Subsystem, Not an Accounting System

Agencies treat the AR system as a subsystem that tracks the general ledger, not as the accounting system, and HiveAR follows that expectation. It does not handle payroll, vendor payments, or the rest of enterprise accounting, because none of those touches an AR event. It does track what is genuinely AR: client invoices and payments, the commission split, and the trust and client balances. Money the agency cares about that is not a ledger concern, such as cost-to-collect, lives in reporting rather than the general ledger, and agent goals, bonuses, and time cost stay out as well. The agency's real accounting system remains the books of record, and HiveAR posts to it through export. HiveAR maintains its own internal chart of accounts for the AR domain so that it can produce balanced entries and self-reconcile, and a configurable mapping translates those internal accounts to the agency's external account codes when entries are exported.

## The Ledger Moves When Money Moves

The governing rule is that the ledger moves when money moves, not when a balance changes. Loading an account, a debit or credit balance adjustment, an agency-assessed fee, and agency-accrued interest all change what the consumer owes in the bucket sub-ledger from [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md), and they post nothing to the general ledger. The reason is that in contingency and servicing the agency does not own the debt, so the consumer's balance is the client's receivable rather than an asset of the agency, and on purchased debt the cost basis is deferred to the debt-purchase module. Revenue is recognized when money is collected, not when a charge or fee is assessed, which is correct for a collector and keeps the ledger clean. A consumer payment, a reversal, the collection of an agency fee or accrued interest, and a remittance are the events that move the ledger.

This is the same financial event stream that [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) projects into bucket balances, now projected a second way into double-entry. One payment event reduces a bucket in the sub-ledger and posts a journal entry in the general ledger, so the two reconcile because they share an origin. For agency-assessed fees and agency-accrued interest, the bucket's origin and treatment attributes determine the posting when the money is collected: agency revenue if the agency keeps it, a split if it is remittable.

## Contract Type Drives the Posting

The contract type on the account selects how a consumer payment posts. On a third-party contingency account, a collected payment debits trust cash, credits the client's due-to-client balance for the client's share, and credits commission revenue for the agency's share. On a purchased account, the agency owns the balance, so a collected payment debits operating cash and credits recovery revenue, with no trust liability and no commission. Servicing, a fee-based model, joins in v2 with its own posting rule. The same payment is a different transaction depending on the contract type, which is how the classifier from [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) reaches into the ledger.

## Trust Accounting and Three-Way Reconciliation

Funds collected on contingency accounts are client money held in trust, not the agency's own. HiveAR records them as a client-dimensioned trust liability and tracks the trust cash balance on its books, which are two of the three legs of a three-way reconciliation. The third leg, the trust bank statement, is external, and the bank reconciliation itself is the agency's accounting-system task. HiveAR provides the two internal legs cleanly, client-dimensioned, so the agency can reconcile its trust account against its bank; it does not model physical bank accounts, import statements, or encode state-specific trust rules.

HiveAR does not hold funds for a clearing period before recognizing or remitting them. Payments post on receipt and are remitted as posted, which matches how most agencies operate now that card and electronic payments dominate and check NSF risk is small. A returned payment posts a reversal, a compensating event that backs out the original entries, and the reversal reduces the next remittance by that amount, carried by the client-dimensioned balance. An optional hold-for-clearing is a v2 consideration for agencies that still want one.

## Client Balances: Held Funds, Remittance, and Client AR

Client balances are modeled as one thing: client-dimensioned funds held and owed. The same structure carries the remittance payable, the funds a client advances for costs such as court fees, and client AR, what a client owes the agency. Remittance supports both models in v1. Under net remit, the agency deducts its fee and remits the net with a statement showing the deduction. Under gross remit, the agency remits the full amount and invoices the client for the fee, which creates client AR. A direct payment, where the consumer pays the client and the agency is still owed its fee, nets against the next remittance or is invoiced when there is no remittance that period. Cost advances use the same held-funds model, so the legal module can track court-fee advances without a new mechanism.

## Commission Follows Debt Paydown

Commission is recognized when money pays down real debt, not when a payment is received. It attaches to the act of satisfying actual debt, regardless of where the money came from or when it arrives. This single rule is what makes overpayments and credit balances tractable, and it determines the commissionable portion of every collection, which the client statement reports so the client sees the correct share and the agency the correct commission. The commission rates and the rules that calculate them are set by the client-billing decision; the ledger consumes their result to post the split.

## Overpayments and Credit Balances

Overpayments cannot wait, so v1 tracks credit balances as a first-class consumer credit liability. When a consumer pays more than is owed, the portion that pays real debt is commissionable and posts the normal split, and the excess posts to a consumer credit liability and is not commissionable, because it did not satisfy debt. A credit balance can be left in place, refunded to the consumer, or applied to another of the same debtor's accounts.

Because commission follows debt paydown, the difficult case resolves itself. When a held credit is later applied to debt, whether because the client sends a balance-increasing adjustment or because the credit is moved to another account, that application is a debt-paydown event, so it recognizes commission on exactly the amount that now pays real debt and lands the balance correctly in the same posting. No pair of offsetting correction transactions is needed, and none is introduced. Applying a credit to another account recognizes commission under that account's client terms even when it belongs to a different client, and the event model handles the cross-client move within one posting.

## The Chart of Accounts and Export

HiveAR's internal chart of accounts covers the AR domain: trust cash, operating cash, the client-dimensioned funds held and owed, commission revenue, recovery revenue, fee and interest revenue, and the consumer credit liability. A configurable mapping associates each internal account, and the bucket and event types that post to it, with the agency's external account codes, so exported entries arrive in the agency's own chart of accounts. Export in v1 is a generic flat tab-delimited journal-entry file, normally as summarized period entries with the underlying transaction detail kept in HiveAR for drill-down. Named-format exports follow in v2, targeting QuickBooks and a modern mid-market accounting system such as Dynamics 365 Business Central, Sage, or Xero. The generic file serves any other system, including the installed base of older platforms, without a dedicated integration.

## Scope and What Composes From This

This decision establishes the ledger and the money model and leaves the rest to compose from it. Commission and fee rates and the rules that calculate them are the client-billing decision, and the ledger posts their result. The legal module assembles its accounting from these primitives: court, attorney, and service fees are buckets with origins and treatments, client cost advances use the held-funds model, post-judgment amounts route to their own ledger accounts through the configurable mapping, and a judgment for less than the balance is a balance adjustment with no revenue reversal, since the written-off amount was never collected. The debt-purchase contract-type module owns purchased-debt accounting: v1 posts purchased collections as gross recovery revenue, and the GAAP cost-recovery treatment, purchase funding, and cost recovery by file are advanced features that module adds later, so the portfolio's true net income lives in the agency's real books until then. Payroll, vendor payments, cost-to-collect, and agent goals, bonuses, and time cost remain outside the ledger entirely.

## Implementation Phasing

**HiveAR v1 (MVP):** The internal AR chart of accounts and self-balancing double-entry ledger, posting from the [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) financial event stream. The money-moves rule, with account load, balance adjustments, fee assessment, and interest accrual as sub-ledger events. Contract-type posting for third-party contingency and purchase. The client-dimensioned trust liability and trust cash balance for two-leg reconciliation support, with post-on-receipt, remit-as-posted, and reversals that reduce the next remittance. Net and gross remit with client AR and cost advances on the shared funds-held model. Commission recognized on debt paydown. Credit balances and overpayment handling with refund and cross-account application. The configurable external account mapping and the generic flat tab-delimited export.

**HiveAR v2:** The servicing contract type and its posting rule. Named-format exports for QuickBooks and a modern mid-market system. An optional hold-for-clearing for agencies that want one.

**HiveAR v3+:** Additional export targets as demand warrants. The debt-purchase module's advanced accounting, cost-recovery treatment and purchase funding, is that module's own later work rather than the ledger's.

**Breaking change risk: LOW to MEDIUM. The ledger consumes the existing financial event stream and adds projection and posting rules rather than changing the event model, and the chart of accounts, the mapping, and the remit options are additive. The risk that warrants attention is getting the posting rules and the account model right at the foundation, since commission recognition, the trust liability, and the credit-balance treatment are correctness-critical and other financial work builds on them. The money-moves rule and the contract-type posting are stable, because they follow GAAP and the [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) model directly.**

## Implications For Contributors

The ledger moves only on money movement. Account load, balance adjustments, fee assessment, and interest accrual are sub-ledger events and post nothing to the general ledger. No code path may post a consumer balance change to the ledger.

The consumer balance is not a general ledger asset. On contingency and servicing the agency does not own the debt, so its balance never appears as an agency receivable. Purchased-debt cost basis is the debt-purchase module's concern, not the core ledger's.

Commission is recognized on debt paydown, never on payment receipt. The overpaid portion of a payment is non-commissionable until it later pays real debt, and no code may take commission on a credit balance.

Client balances are one model. Remittance payable, cost advances, and client AR all use the client-dimensioned funds-held-and-owed structure. Contributors must not create a parallel client-money mechanism.

Every posting is balanced double-entry and maps to the external chart of accounts through configuration. Contributors must not hard-code external account codes or emit unbalanced entries.
