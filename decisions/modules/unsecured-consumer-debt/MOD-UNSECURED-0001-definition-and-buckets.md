---
id: MOD-UNSECURED-0001
title: "Definition and Buckets"
status: Accepted
version: 1.0
area: module:unsecured-consumer-debt
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Unsecured Consumer Debt Module Design Decision 1: Definition and Buckets

## Decision

The unsecured consumer debt module is the platform's first debt-type module and its reference example, the canonical bundle of the common consumer-debt primitives. It is a manifest under the module composition model from Wax Design Decision 33: it references shared primitives by key, selects five balance buckets, declares two properties and three account role types, ships with interest accrual off, and supplies a default payment waterfall. It adds no subject-matter structure, since unsecured consumer debt has nothing to itemize beyond its buckets, which makes it the cleanest exercise of the debt-type extension framework from [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-account-structure-extension.md). Its module type is debt_type, and it is compatible with the contingency contract type in v1.

## A Manifest Over Shared Primitives

Almost the whole of this module is a declarative selection from the shared seed package. Its buckets, its role types, and its declared properties are common primitives that other consumer-debt modules will also use, referenced here by key rather than defined here, per [Wax Design Decision 33](../../wax/WAX-0033-module-composition-model.md). The module contributes no satellite tables of its own, because there is no subject matter to record beyond the balance composition the buckets already carry. What remains module-specific is its particular selection and its configured default waterfall. A reader who wants to know what unsecured consumer debt is in HiveAR is therefore reading a short manifest, not a new schema.

## The Buckets

The module selects five balance buckets: client fees, agency fees, client interest, agency interest, and principal. The split is by ownership as well as by kind, because it drives remittance and commission under HiveAR Design Decisions 6 and 8. The three client-side buckets, client fees, client interest, and principal, are commissionable and remitted to the client. The two agency-side buckets, agency fees and agency interest, are the agency's own revenue, the charges it adds where the agreement or law allows. The buckets map to the Reg F itemization categories, so the validation itemization falls out of the balances rather than being assembled separately.

## Interest Off by Default

The module declares the debt interest-bearing-capable but ships interest accrual off. Post-charge-off interest is exactly the charge the FDCPA bars unless the agreement or law authorizes it, so whether interest accrues, and at what rate, is the region pack and the contract speaking, not the module asserting. The client-interest bucket holds interest that arrived in the placed balance, which is remitted; the agency-interest bucket holds interest the agency adds where it is permitted, which is its own revenue. With accrual off, both simply carry whatever interest was placed and nothing more.

## Properties and Roles

The module declares two standardized properties from the Foundation-governed vocabulary, consumer regulatory nature and unsecured, which region packs read to apply the right regime. Its account role types are the primary debtor, a co-borrower or co-signer, and an authorized contact, the realistic set for generic consumer debt. Both the properties and the roles are shared primitives referenced by key, not defined in this module.

## The Default Waterfall

The module ships a default application order of client fees, agency fees, client interest, agency interest, and principal. A payment fills the buckets in that order, subject to the contract, a region-pack mandate, and the per-payment override from [HiveAR Design Decision 7](../../hivear/HIVE-0007-payment-application-and-waterfall.md), and subject to the cross-account Federal floor, which governs allocation across a debtor's accounts and not allocation across buckets within one account.

Confidence on this default order is Medium. It is the conventional fees-then-interest-then-principal sequence with client charges ahead of agency charges, and it is a defensible default, but a client-whole-first alternative, client fees, client interest, principal, then the agency's own add-ons, would pay the client's principal ahead of the agency's most legally exposed charges and is a live candidate for revision on fairness and exposure grounds. The order is an overridable default, so the choice is not load-bearing.

## Itemization

The buckets correspond to the Reg F validation itemization. The itemization-date amount is the principal, the interest and fees buckets carry what accrued since, and payments and credits are the transactions that reduce them, so the itemization a validation notice must present is read from the balances rather than maintained as a separate artifact. The itemization date itself is the account-level date established in [HiveAR Design Decision 5](../../hivear/HIVE-0005-account-structure-and-balance-composition.md).

## No Subject-Matter Structure

This module deliberately attaches no subject-matter fields or sub-entities. Unsecured consumer debt has no collateral, no service lines, and no itemized charge detail beyond its buckets, so there is nothing for the debt-type extension framework to attach. The module stands as proof that the framework imposes nothing: a debt type with no subject matter is fully served by the core account, its buckets, its roles, and its properties.

## Scope

This module covers charged-off, contingency-placed consumer debt, a placed balance, static or carrying placed interest, itemized from the itemization date and worked on a contingency contract. Pre-charge-off and first-party servicing, with payment schedules and a next-due structure, is the servicing contract type in V3 and is out of scope here. Debt purchased rather than placed is the debt-purchase contract type and its module, in V2.

## Implementation Phasing

**Unsecured Consumer Debt Module v1:** The five buckets with their client-and-agency split and commissionability, the consumer and unsecured properties, the debtor, co-signer, and authorized-contact roles, interest accrual off by default, the default waterfall above, and the Reg F itemization mapping. No subject-matter structure. Compatible with the contingency contract type.

**Unsecured Consumer Debt Module v2+:** Interest accrual configuration where a region pack and the contract permit it. Compatibility with the debt-purchase contract type as that module matures. Any refinement the default waterfall warrants after review.

**Breaking change risk: LOW. The module is a manifest selecting shared primitives and adds no structure, so it changes nothing in the core or the framework, and its elements are additive and overridable.**

**Confidence: HIGH. Contingency-collected, charged-off unsecured consumer debt is well-trodden ground, and the buckets, properties, roles, and itemization are settled. The one element held at Medium is the default waterfall order, as noted in that section.**

## Implications For Contributors

This module is a manifest, not a schema. It references shared primitives by key and contributes no satellite tables; a vertical that builds on it adds its subject matter through its own module, not by editing this one.

The bucket split is by ownership and kind. Client-side buckets are commissionable and remitted; agency-side buckets are agency revenue, and the distinction drives remittance and commission, so it must not be collapsed.

Interest is off until compliance turns it on. No code may accrue interest on these accounts unless a region pack and the contract authorize it.

The waterfall is a default, not a rule. The shipped order is overridable by contract, region pack, and per-payment direction, and it is held at Medium confidence pending review.
