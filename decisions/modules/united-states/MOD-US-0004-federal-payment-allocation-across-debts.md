---
id: MOD-US-0004
title: "Federal Payment Allocation Across Debts"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 4: Federal Payment Allocation Across Debts

## Decision

The federal Compliance Pack, compliance.us, will supply the United States federal values for the two rules of [HiveAR Design Decision 7](../../hivear/HIVE-0007-payment-application-and-waterfall.md) that govern a payment toward a consumer's debts: the consumer's allocation directions are honored, and money the consumer did not direct never applies to an amount in dispute. The values come from section 810 of the Fair Debt Collection Practices Act, 15 U.S.C. 1692h, and they carry the premises that HiveAR Design Decision 7 stated as federal law until this decision moved them out of the core. Where the federal text leaves a question open, the pack takes the cautious reading and flags it. The values govern consumer debts only, meaning debts whose debt type declares the consumer regulatory nature under [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-structure-extension.md), and the core rules hold for every debt whatever this pack says. Every statement of law in this decision is a research finding that needs verification by someone with compliance standing, is educational reference material, and is not legal advice.

## Where This Decision Sits

HiveAR Design Decision 7 builds the two rules as core mechanisms and names no statute, under the default test of [Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md). This decision supplies the federal values as Compliance Pack content, the same way [United States Module Design Decision 1](MOD-US-0001-itemization-date-and-validation-itemization.md) supplies the values for the validation notice and [United States Module Design Decision 3](MOD-US-0003-federal-contact-times-and-call-frequency.md) supplies the values for contact times and call frequency. A state's Compliance Pack adds its own values on the same mechanisms.

## The Federal Rule

If a consumer owes multiple debts and makes any single payment to a debt collector with respect to them, the collector may not apply the payment to any debt that the consumer disputes and, where applicable, must apply the payment in accordance with the consumer's directions (needs verification). The source is 15 U.S.C. 1692h, read on 2026-10-11. Regulation F, 12 CFR part 1006, has no section that implements it (needs verification).

HiveAR Design Decision 7 stated four premises before this decision moved them here. The federal text bears on each as follows.

> **FEDERAL PREMISES FOR PAYMENT ALLOCATION**
>
> **Scope**: federal law governs how a single payment is allocated across a consumer's debts. The text reaches a debt collector that receives a single payment toward multiple debts of one consumer (needs verification).
>
> **Disputed debts**: no part of the payment may be applied to a disputed debt. The text bars applying the payment "to any debt which is disputed by the consumer" (needs verification).
>
> **Consumer directions**: the payment is applied as the consumer directs. The text requires it "where applicable" (needs verification).
>
> **Oral disputes**: a dispute raised orally still excludes the debt. The text does not say how a consumer disputes a debt, and no source for this premise was found, so it remains a premise until someone with compliance standing confirms or corrects it (needs verification).

## The Values This Pack Sets

The pack sets the following values on the mechanisms of HiveAR Design Decision 7. Each is flagged, and each takes the cautious reading where the federal text is silent.

- A dispute counts whatever its form, so a dispute that an agent records from a call excludes the disputed amount from money the consumer did not direct, as it would if the consumer wrote. This is the cautious reading of the oral-disputes premise (needs verification).
- The federal text speaks of a "debt which is disputed", and HiveAR's core rule speaks of amounts in dispute. Whether a debt of which the consumer disputes only part is a disputed debt under the text, so that the whole debt is excluded, is not settled by the text (needs verification). Until it is settled, the pack treats a consumer debt with any disputed part as disputed in whole for money the consumer did not direct, a setting that the core's disputed-amount rule must offer.
- The federal text speaks of a consumer who owes multiple debts. HiveAR's core rule also covers a single debt, so a payment that a consumer does not direct to a wholly disputed debt becomes the consumer credit balance. Whether federal law requires that for a single debt needs verification, and the pack keeps the core rule as the cautious reading.
- Apart from the reading for partial disputes above, the pack adds nothing to the core's handling of money the consumer did not direct: it goes to the consumer's amounts that are not in dispute, and what cannot be applied becomes the consumer credit balance of [HiveAR Design Decision 6](../../hivear/HIVE-0006-gaap-journal-and-general-ledger.md) (needs verification).
- Money that a consumer directs to a debt beyond what the debt owes is not spread to the consumer's other debts as undirected money under this pack, so the core's treatment of such an excess stands. Whether federal law would allow spreading it needs verification, and a pack may allow it only once that is confirmed.
- The pack sets no deadline for holding a consumer credit balance. What the agency does with a balance it holds, such as a refund, is the agency's decision. Whether a state's unclaimed property law reaches a credit balance held for a consumer needs research of its own (needs verification).

## Which Debts These Values Govern

The Fair Debt Collection Practices Act governs the collection of consumer debts (needs verification). The pack therefore applies these values only to a debt whose debt type declares the consumer regulatory nature, a standardized property under HiveAR Design Decision 9. A debt whose type declares the commercial regulatory nature is outside these values, and the core rules of HiveAR Design Decision 7 still apply to it, because they are core mechanisms that no pack is needed to turn on. A state's rules for commercial debt belong to that state's Compliance Pack.

## Status of the Content

> **Legal force**: 15 U.S.C. 1692h is a section of a federal statute, and Regulation F does not implement it. The cautious readings above are design choices of this draft and not readings of law. All of this needs verification.
>
> **Effective date**: not recorded.
>
> **Verification status**: the statute text was read on 2026-10-11 by the drafter and not reviewed by counsel. No source was found for the oral-disputes premise.
>
> **Coverage**: consumer debts, which the pack identifies by the regulatory nature that their debt type declares.

## Implementation Phasing

**HiveAR v1 (MVP):** The values for consumer directions and disputed amounts on consumer debts, including the cautious readings for oral disputes, partial disputes, and a single disputed debt.

**HiveAR v2:** Revisions as counsel verifies or corrects the premises and the cautious readings, each recorded with its effective date and verification status.

**HiveAR v3+:** State Compliance Pack values on the same mechanisms.

**Breaking change risk: LOW. The decision is pack content that configures core mechanisms, and a corrected value changes at the pack's own cadence.**

**Confidence: MEDIUM. The federal text is short and was read directly. The oral-disputes premise has no source, and the readings for partial disputes and a single debt are cautious choices of this draft that need verification.**

## Implications For Contributors

These values live only in compliance.us. HiveAR Design Decision 7 names no statute and never reads these values by name.

A change to a value records its source, its legal force, its effective date, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values.

The core's disputed-amount rule must let a pack treat a debt with any disputed part as disputed in whole, because this pack does so until the question is settled.
