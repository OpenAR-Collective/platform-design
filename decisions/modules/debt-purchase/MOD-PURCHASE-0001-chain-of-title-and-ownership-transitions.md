---
id: MOD-PURCHASE-0001
title: "Chain of Title and Ownership Transitions"
status: Accepted
version: 1.1
area: module:debt-purchase
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# Debt-Purchase Module Design Decision 1: Chain of Title and Ownership Transitions

## Decision

The debt-purchase module will record an account's chain of title, the documented history of who has owned the debt from the original creditor to the current owner, and the ownership transitions that build and close it. Each link in the chain is an assignment record that names the parties and the date and references its proving documents in the document store from [Wax Design Decision 30](../../wax/WAX-0030-document-storage.md), identifying the specific account rather than a bulk file. Purchase appends the agency as the current owner; sale and buyback transfer ownership out. The chain exists only because ownership transfers, which is why it lives in the debt-purchase module and not in the HiveAR core, where the current-owner fact alone is already carried by [HiveAR Design Decision 5](../../hivear/HIVE-0005-account-structure-and-balance-composition.md).

## Why Chain of Title Matters

A purchased debt is only as enforceable as the owner's ability to prove it owns the specific account. To collect or sue, a buyer must show an unbroken chain of title, each assignment from the original creditor through every intermediate holder to the current owner, documented in writing and identifying the particular account rather than a bulk portfolio. A single missing or generic link, an assignment that names only a file number or a bulk schedule without the account, can defeat standing and end a suit. The chain is therefore an evidentiary structure, not merely a provenance note, and the module models it as one: a sequence of assignments, each tied to the bill of sale, the assignment instrument, and the account-level schedule that prove it.

## The Chain Structure

An account carries an ordered chain of ownership links. Each link records the assignor and assignee as entities from [HiveAR Design Decision 1](../../hivear/HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), the date of assignment, a civil date as defined in [Wax Design Decision 12](../../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md), and references to the proving documents held in the [Wax Design Decision 30](../../wax/WAX-0030-document-storage.md) store, the bill of sale and the account-level schedule that places the specific account within the transfer. The original creditor and the current owner are projections of the chain rather than separately maintained fields, so they cannot drift from the underlying assignments. A purchased account whose chain is incomplete is flagged as such, since the gap bears directly on enforceability, and the agency may carry the account while knowing its title is clouded.

## Ownership Transitions

Three transitions move ownership, and each is an event on the account. Purchase brings an account under the agency's ownership and appends the agency to the chain as the current owner, with the bill of sale attached; the seller becomes the prior owner, who may or may not be the original creditor. Sale transfers an account to a party other than the one it was bought from, closing the agency's ownership and extending the chain to the new owner. Buyback returns an account to the creditor it was bought from, reversing the original purchase, and typically carries a refund of the purchase price. Sale and buyback are distinguished because they differ in counterparty and in economic effect, a buyback being a reversal of the acquisition while a sale is an onward disposition.

## The Money Side Is Recorded Here, Posted Later

This decision records the ownership transitions and their amounts as data: the purchase price, already a confidential account field under [HiveAR Design Decision 5](../../hivear/HIVE-0005-account-structure-and-balance-composition.md), the proceeds of a sale, and the refund on a buyback. Each of these is a typed monetary value under [Wax Design Decision 34](../../wax/WAX-0034-monetary-values-and-currency.md) that names its own currency, the one in which it was paid or received, which need not be the account's denomination currency from [HiveAR Design Decision 5](../../hivear/HIVE-0005-account-structure-and-balance-composition.md). It does not post the full general-ledger accounting of cost, proceeds, and refund. That accounting is the debt-purchase module's advanced accounting, deferred consistent with [HiveAR Design Decision 6](../../hivear/HIVE-0006-gaap-journal-and-general-ledger.md), where v1 posts purchased collections as gross recovery revenue and the GAAP cost-recovery treatment, purchase funding, and cost recovery by file arrive with that later module work. The transitions and amounts are captured now so the history is complete; their booking follows when the advanced accounting lands.

## Relationship to the Core and the Locale Layer

The chain of title is distinct from the concerns it sits near. It is not the HiveAR account lifecycle, which is an account's own status over time and needs no decision of its own. It is not account grouping from [HiveAR Design Decision 4](../../hivear/HIVE-0004-account-sets.md), which organizes accounts without changing ownership. It is the history of owners, which only the debt-purchase module produces. Compliance rules read the chain rather than living in it: a region pack that requires disclosure of the original creditor reads the chain to find that creditor, and the rule itself remains in the locale layer per [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-account-structure-extension.md), never in this module.

## Implementation Phasing

**Debt-Purchase Module v1:** The chain-of-title structure as ordered assignment links, each referencing its proving documents in the document store and identifying the specific account. The purchase, sale, and buyback transitions as account events, with original owner and current owner as projections of the chain. Recording of the purchase price, sale proceeds, and buyback refund as typed monetary values. The incomplete-chain flag.

**Debt-Purchase Module v2+:** The advanced purchase accounting, the general-ledger treatment of cost, proceeds, and refund, cost recovery by file, and purchase funding and funding source. Richer chain validation and acquisition due-diligence support as practice and community feedback clarify what buyers need.

**Breaking change risk: LOW. The chain is additive structure on purchased accounts and changes nothing in the HiveAR core, and the money side is deliberately deferred so this decision commits only to recording history.**

**Confidence: LOW. The author's direct purchasing experience is buying from original creditors without resale, so the multi-hop chain, its storage, and the surrounding workflow rest on research rather than practice. This decision is explicitly flagged for community scrutiny on what buyers and courts expect for chain-of-title capture and on the workflow around acquiring, validating, and disposing of purchased portfolios.**

## Implications For Contributors

The chain is evidentiary. Each link must reference proving documents that identify the specific account, not a bulk file, because enforceability depends on it. A link without account-level proof is recorded as incomplete rather than treated as valid.

Original and current owner are projections. They are derived from the chain, never maintained as independent fields, so they cannot disagree with the assignments behind them.

Chain of title is module-only. It must not migrate into the HiveAR core. The core carries the current-owner fact from [HiveAR Design Decision 5](../../hivear/HIVE-0005-account-structure-and-balance-composition.md); the ownership history belongs to this module.

The money side is recorded, not posted. Transition amounts are captured as typed monetary values here; their general-ledger booking is the module's advanced accounting and is not implemented in this decision.
