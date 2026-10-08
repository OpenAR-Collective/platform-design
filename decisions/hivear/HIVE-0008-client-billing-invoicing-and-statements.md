---
id: HIVE-0008
title: "Client Billing, Invoicing, and Statements"
status: Accepted
version: 1.1
area: hivear
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 8: Client Billing, Invoicing, and Statements

## Decision

HiveAR will treat the client as a posting-driven financial aggregate, symmetric with the debtor account, whose balances are the projection of immutable client transactions. The client balance has two structurally distinct sides because the accounting demands it: a payable side, what the agency owes the client through collections held in trust, and a receivable side, what the client owes the agency through client AR. Operators post client transactions much as they post debtor transactions, and the variation among them is carried by extensible client transaction types rather than a fixed set of balance buckets. This decision also sets the commission and fee rate structure that HiveAR Design Decisions 6 and 7 defer to, and it defines the statement run that periodically settles and bills each client.

## The Client Is a Posting-Driven Aggregate

Just as a debtor account's balances are the running projection of immutable postings, a client's balances are the projection of immutable client transactions, on the same event-sourced foundation and reusing the client-dimensioned funds-held-and-owed model from [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md). Posting a client transaction is the same act as posting a debtor transaction, against a different aggregate. The one difference is that the client balance is two-sided: a debtor only owes, while a client can be owed money by the agency through the remittance payable and can owe money to the agency through client AR, so the client's net position swings between the two. Those two sides are kept structurally distinct because the payable is a trust liability and the receivable is an operating asset, and collapsing them into one signed balance would lose the trust character that [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) and three-way reconciliation depend on. Everything else is carried by extensible transaction types, the way debtor variation is carried by module-supplied buckets, so an agency or a module can define custom client transaction types as needed.

## Client Transactions

Client transactions arrive in two streams. Some post automatically from debtor-side events and need no operator: a collection accrues the client's share into the remittance payable and the agency's share into commission, the statement run pays the payable down, and a reversal backs both out. The rest are posted directly by an operator, an import, or the API, on the same surface and with the same permission discipline as debtor payments, since the authority to post a client transaction is also the authority to direct it. The four operator-posted types are the invoice, which bills the client and creates client AR; the client payment, money received from the client and applied to open invoices oldest-first with a directed override; the adjustment or credit, a manual correction to a client balance carrying a reason code from the [Wax Design Decision 20](../wax/WAX-0020-reason-code-registry.md) registry; and the client AR write-off, which writes off uncollectible client AR as bad debt. These seed types are extensible in the same way the rest of the model is.

Invoice payment and AR tracking are the agency's own receivables ledger turned on the client, where the agency is the creditor and the client is its debtor. An invoice creates client AR, a client payment applies against open invoices, and aging, open-versus-paid status, and the client's running balance fall out of the posting stream. Invoices arise from gross remit, from a fee on a direct payment the consumer made to the client, from cost reimbursement, and from any non-contingency billing model.

## The Commission and Fee Rate Structure

This decision sets the rates and the rules that select them, and the ledger and the waterfall consume the result. Version 1 is a flat per-contract contingency rate combined with per-bucket commissionability, which [HiveAR Design Decision 5](HIVE-0005-account-structure-and-balance-composition.md) already carries as the bucket treatment, so a rule such as commission on principal only with all of a given fee bucket remitted is expressed in the buckets and priced here. Tiered and graduated rate rules, by account age, balance, or cumulative recovery, are deferred to v2, where the bulk of rate-rule requests are expected to land. Contract type selects the model: contingency earns commission, purchase earns none because the agency owns the balance, and the servicing fee models, including per-account and per-seat billing, arrive with the servicing contract type in v2.

## Net and Gross Remit

Both remittance models are supported in v1. Under net remit, the agency deducts its computed fee and remits the net, with the statement showing the deduction. Under gross remit, the agency remits the full amount and invoices the client for the fee, which creates client AR. A direct payment, where the consumer pays the client and the agency is still owed its fee, nets against the next remittance or is invoiced when there is no remittance that period. The rate structure above computes the fee that each model applies.

## The Statement Run

Billing and remittance happen through a statement run, a process the agency initiates when it is ready, at roughly monthly or any other cadence, rather than on a rigid automated cycle. A run takes a through date and sweeps up everything not already invoiced or stated through that date for the selected clients. Selection is driven by user-defined statement frequency codes, labels the agency assigns to clients so it can run a whole group at once, run groups separately, or run a single client. The frequency code is purely a grouping-and-selection label, independent of the client's net-or-gross remit setting. A run also takes options, including whether to include washed reversals, the payment-and-reversal pairs that net to zero within the period, which some agencies want shown for transparency and others want suppressed for a clean statement, and the due date to stamp on the invoices the run produces.

The through date is a civil date, as defined in [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md), and the run compares it with the civil effective date of each transaction, so the cut-off is a comparison of days and does not depend on the zone of whoever starts the run. A transaction whose command supplied no effective date has one derived once, when it is written, from its occurred_at instant in the organization's business zone, so the same transaction falls on the same side of the same through date for everyone. The due date stamped on the invoices a run produces is a civil date as well.

What a run produces follows from each client's remit model. It computes what is owed through the date, generates the statement document, and posts the period's transactions: the remittance that discharges the payable, and, under gross remit, the fee invoices that create client AR with the run's due date. The remittance posting discharges the payable in HiveAR's books and tells the agency what to pay; the physical disbursement from the trust bank account is the agency's own step, consistent with HiveAR being the AR subsystem rather than the bank. Because a run is initiated on demand for a chosen selection and through date, off-cycle situations need no separate mechanism: closing out a departing client, an expedited payout, and a correcting make-whole are each a statement run with the selection and through date that fit the case.

An invoice, a remittance, and a statement each state one currency. A client whose accounts are held in more than one currency receives a separate invoice, remittance, and statement for each, because no total mixes currencies without a conversion recorded under [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md). A single-currency installation states its one currency without anyone choosing it.

## Client Statements

Version 1 ships a single canned statement format. The statement lists the transactions it includes, so the client and the agency can see exactly what the figures rest on, and because the underlying data lives in the view layer from [Wax Design Decision 32](../wax/WAX-0032-reporting-and-business-intelligence.md), anyone who wants a custom presentation runs a query against that data rather than waiting on the platform. A configurable statement designer is therefore a later concern, not a v1 requirement.

## Scope and Boundaries

This decision covers the client aggregate, the operator-posted and automatic client transactions, invoice payment and AR tracking, the commission and fee rate structure, net and gross remit, the statement run, and the canned statement. Cost advances are not part of the core: they belong to the legal module, which introduces the cost-advance and cost-payment transaction types and the held balance they move, so an agency that does not litigate never carries them. The servicing fee models and tiered rate rules are v2, arriving with the servicing contract type. The export of journal entries to the agency's accounting system, generic in v1 and named-format in v2, is specified in [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) and is not restated here. A configurable statement designer and a generic client credit for client overpayments are possible later additions, not v1 scope.

## Implementation Phasing

**HiveAR v1 (MVP):** The client as a two-sided posting-driven aggregate reusing the funds-held-and-owed model. The four operator-posted client transaction types and the automatic debtor-driven postings, with extensible transaction types. Invoice payment and client AR tracking with aging. The flat per-contract contingency rate with per-bucket commissionability. Net and gross remit. The statement run with manual initiation, user-defined frequency-code selection, through date, the washed-reversal option, and the due date, with the through date and the due date as civil dates and one currency stated on each invoice, remittance, and statement. The canned statement that lists its transactions.

**HiveAR v2:** Tiered and graduated rate rules by age, balance, or cumulative recovery. The servicing fee models, including per-account and per-seat billing, with the servicing contract type. Named-format accounting exports per [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md). A configurable statement designer.

**HiveAR v3+:** Further billing models and rate-rule sophistication as agencies request them, all additive to the structure defined here.

**Breaking change risk: LOW. The client aggregate reuses the existing event-sourcing and the funds-held-and-owed model, and the transaction types, rate rules, remit models, and statement options are additive. The two-sided trust-versus-operating split and commission-on-debt-paydown are correctness-critical to settle now, but they follow directly from HiveAR Design Decisions 5 and 6 and are stable.**

## Implications For Contributors

The client is an aggregate, posted against like the debtor. Client balances are projections of immutable client transactions, never directly edited numbers, and the payable and receivable sides stay distinct because one is trust and the other is operating.

Variation lives in transaction types, not in a fixed balance set. New client-money behavior is added as a client transaction type, the way debtor variation is added as a bucket, and cost advances in particular belong to the legal module.

Adjustments and write-offs carry reason codes. Any manual correction or write-off to a client balance records a reason code from the [Wax Design Decision 20](../wax/WAX-0020-reason-code-registry.md) registry.

Remittance and invoicing flow from the statement run. Contributors must not post remittances ad hoc outside a run; an off-cycle need is met by initiating a run for the chosen selection and through date.

A statement run compares civil dates and states one currency on each document. Contributors must not compare a through date with a recorded instant, and must not total across currencies.
