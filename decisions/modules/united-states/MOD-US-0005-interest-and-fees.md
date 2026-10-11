---
id: MOD-US-0005
title: "Interest and Fees"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 5: Interest and Fees

## Decision

The federal Compliance Pack, compliance.us, will state the United States federal rule on amounts added to a consumer debt: a debt collector may collect an amount, including interest, a fee, a charge, or an expense incidental to the principal obligation, only when the agreement creating the debt expressly authorizes it or the law permits it. The rule comes from the Fair Debt Collection Practices Act and Regulation F, and it carries the premise that [Unsecured Consumer Debt Module Design Decision 1](../unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md) stated until this decision moved it out of the module. The pack reads the rule when it decides whether a debt may accrue interest or add a fee, and the rates and caps that state law sets are values of the state Compliance Packs, not statements in any decision. The rule governs consumer debts only, meaning debts whose debt type declares the consumer regulatory nature under [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-structure-extension.md). Every statement of law in this decision is a research finding that needs verification by someone with compliance standing, is educational reference material, and is not legal advice.

## Where This Decision Sits

A debt's balance is composed of the buckets of [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md), and a debt-type module decides whether its debt can bear interest. The unsecured consumer debt module ships interest accrual off, the cautious default under the default test of [Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md), and leaves whether interest accrues, and at what rate, to the contract and the Compliance Pack. This decision supplies the federal rule that the pack applies to that question. The starting values that the US Boilerplate Pack sets for interest, which are sound practice and not law, belong in this decision too and are added when the interest settings that they configure are decided.

## The Federal Rule

A debt collector must not collect any amount unless the agreement creating the debt expressly authorizes it or the law permits it, and "any amount" includes any interest, fee, charge, or expense incidental to the principal obligation (needs verification). The sources are 15 U.S.C. 1692f(1) and 12 CFR 1006.22(b), read on 2026-10-11.

The premise that the unsecured consumer debt module stated, and that this decision moves here, is that interest added after charge-off is an amount the rule bars unless the agreement or the law authorizes it (needs verification). Whether a creditor that stopped adding interest after charge-off can resume it, or a collector can add it for the creditor, depends on the agreement and on state law and needs research of its own (needs verification).

## Which Debts This Rule Governs

The Fair Debt Collection Practices Act and Regulation F govern the collection of consumer debts (needs verification). The pack therefore applies this rule only to a debt whose debt type declares the consumer regulatory nature. Interest and fees on a debt declared commercial follow the contract and state law, and the state rules that limit what a collector of commercial debt may add belong to that state's Compliance Pack.

## Status of the Content

> **Legal force**: 15 U.S.C. 1692f(1) is a section of a federal statute, and 12 CFR 1006.22(b) is a regulation of the Consumer Financial Protection Bureau that implements it. All of this needs verification.
>
> **Effective date**: not recorded.
>
> **Verification status**: read from the statute and the Bureau's published regulation on 2026-10-11 by the drafter and not reviewed by counsel.
>
> **Coverage**: consumer debts, which the pack identifies by the regulatory nature that their debt type declares.

## Implementation Phasing

**HiveAR v1 (MVP):** The federal rule as pack content, read when the pack decides whether a consumer debt may accrue interest or add a fee.

**HiveAR v2:** The US Boilerplate Pack's starting values for interest, added with the interest settings that they configure.

**HiveAR v3+:** State Compliance Pack values, such as the rates and caps that state law sets, on the same mechanisms.

**Breaking change risk: LOW. The decision is pack content that configures existing mechanisms and changes at the pack's own cadence.**

**Confidence: MEDIUM. The federal rule was read directly from the statute and the regulation, and they agree. How it applies to interest after charge-off depends on facts and state law that were not researched.**

## Implications For Contributors

This rule lives only in compliance.us. The debt-type modules and the HiveAR core never name it.

A change to a value records its source, its legal force, its effective date, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values.
