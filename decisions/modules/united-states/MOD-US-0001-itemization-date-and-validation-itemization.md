---
id: MOD-US-0001
title: "Itemization Date and Validation Itemization"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-10-10
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 1: Itemization Date and Validation Itemization

## Decision

The United States layer will state the federal rules for the amounts that a validation notice discloses as Compliance Pack content for the jurisdiction identified as compliance.us, and the HiveAR core will not state them. The core supplies the data and the mechanisms that the notice draws on: the candidate reference dates and the agency's rank order, the itemization with its line classifications, the pre-placement informational totals, and the debt's postings, all from [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md). This decision says how the United States notice uses them. Every statement of law in it is a research finding that needs verification by someone with compliance standing, is educational reference material, and is not legal advice.

## Where This Decision Sits

This is the first decision of the United States layer, which holds the content of HiveAR that depends on United States law or on United States conventions. [Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md) defines the constructs that carry such content: a Compliance Pack for each jurisdiction at federal and state granularity, a Locale Module for addresses and identity numbers, a Reference Pack, and a Bundle that installs them together. The decisions of this family are numbered MOD-US, and each says which construct it describes. This one describes the federal Compliance Pack, which it proposes to identify as compliance.us, with state packs such as compliance.us.tx layered on it. A Compliance Pack reflects the Collective's understanding of the law at the time of publication and is labeled prominently as educational reference material. The core, the debt-type modules, and the packs of other jurisdictions refer to this decision by its ID where a United States rule is meant, and a pack for another jurisdiction defines its own notice and reads the same data.

## The Itemization Date

For the United States, the itemization date is a reference date on which the debt collector can ascertain the amount of the debt, and it is one of five dates: the last statement date, the charge-off date, the last payment date, the transaction date, and the judgment date. The last statement date is the date of the last statement that a creditor provided to the consumer, and the transaction date is the date of the transaction that gave rise to the debt. A collector may select any of the five (needs verification). Once it has used a reference date for a debt in a communication with a consumer, it must use that date for that debt consistently, and a later collector may use a different date from the one a prior collector used (needs verification). The sources are section 1006.34(b)(3) of Regulation F, 12 CFR part 1006, and its official interpretation.

The core stores the candidate dates that the client provides and lets the agency configure the rank order that selects among them, as [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md) describes. This pack contributes the five names and its rule that the selected date must be one of them. After a communication has stated the itemization date, HiveAR will keep that date as the debt's itemization date and will not move it when the candidate dates or the rank order later change.

## The Amount on the Itemization Date

The notice states the amount of the debt on the itemization date. That amount includes any interest, fees, or other charges owed on that date, less any payments or credits applied by that date, so it is one net figure, and the rule does not call for an itemization of what came before the itemization date (needs verification). The sources are section 1006.34(c)(2)(vii), its official interpretation, and the compliance aid that the Consumer Financial Protection Bureau issued on the itemization table. The figure is the itemization-date figure that the client provides under [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md). The lines of the debt's itemization dated on or before the itemization date support it, and HiveAR does not require them to produce it.

## The Validation Itemization

The notice also states an itemization of the current amount of the debt that reflects interest, fees, payments, and credits since the itemization date, which HiveAR calls the validation itemization (needs verification). It covers the period from the itemization date to the date the notice is provided, it includes an item from any source, and a third-party payment or an insurance adjustment may appear as a payment or a credit. It has a field for each of the four categories, and a field is never left blank: when nothing was assessed or applied, the field states zero or none. An item that was applied and then returned or reversed within the same period may be left out when the other amounts are disclosed accurately. The rule names no interest accrual method, and the interest disclosed must be accurate (needs verification). The sources are section 1006.34(c)(2)(viii), its official interpretation, and the compliance aid.

The four itemized amounts and the amount on the itemization date need not add up to the current amount. An amount from the period that cannot be accurately categorized as interest, a fee, a payment, or a credit stays in the current amount without being forced into a category, and the collector may add a field that describes it accurately and does not combine it with the four (needs verification). HiveAR therefore does not force a charge or an adjustment dated after the itemization date into one of the four categories.

## The Current Amount

The notice states the current amount of the debt as of the date the notice is provided, which may be the total outstanding debt or the amount required to bring the account current, depending on the facts (needs verification). The sources are section 1006.34(c)(2)(ix), its official interpretation, and the compliance aid. [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md) supplies the balance and derives the current-due amount from the contract type.

## How the Notice Draws on HiveAR Data

The federal Compliance Pack contributes a disclosure template for the amounts of the notice, and the template binds each field to HiveAR data as follows. The itemization date is the debt's itemization date, and the amount on that date is the itemization-date figure. The interest, fees, payments, and credits since the itemization date come from three places. The first is the lines of the debt's itemization dated after the itemization date, read by their interest, fee, payment, and credit classifications. The second is the interest and fees that arrived in the placed balance, where the debt-type module says which of its buckets carry them, as the [unsecured consumer debt module](../unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md) does with its client interest and client fees buckets. The third is the postings made since placement, which are payments, adjustments that reduce the debt, interest accruals, and fee assessments. The current amount is the debt's balance or current-due amount on the date of the notice. A line classified as a charge or an adjustment and dated after the itemization date is not placed in a category, and HiveAR reports the difference between the current amount and the sum of the itemization-date amount and the four itemized amounts, so that the agency sees what an added field would have to describe.

## Scope and What Branches Off

This decision covers the reference date and the amounts. It does not cover the rest of the validation information, such as the creditor's name and the account number, if any, on the itemization date, or the timing and the delivery of the notice. Each is for a later decision of this family. The creditor and the account number on the itemization date depend on HiveAR keeping dated history of the creditor and of the debt's identifiers, which a later decision will address. The rules of a state that add to the federal ones belong to the decisions on the state packs. How a federal pack and a state pack combine when both speak to one subject is an open question, as is whether the candidate reference dates can extend beyond these five for another jurisdiction.

## Status of the Content

> **Legal force**: Regulation F, 12 CFR part 1006, is a regulation of the Consumer Financial Protection Bureau, and section 1006.34 has an official interpretation. The Bureau has also issued a compliance aid on the itemization table, whose legal force is for counsel to confirm. All of this needs verification.
>
> **Effective date**: not recorded. It is to be confirmed against the Federal Register publication of the rule.
>
> **Verification status**: read from the Bureau's published text on 2026-10-10 by the drafter and not reviewed by counsel. The model validation notice itself was published as an image and was not read.
>
> **Coverage**: not assessed here. Which debts and which collectors the rule reaches needs verification.

## Implementation Phasing

**HiveAR v1 (MVP):** The five candidate reference dates, which the core already stores under [HiveAR Design Decision 5](../../hivear/HIVE-0005-debt-structure-and-balance-composition.md), named by this pack.

**HiveAR v2:** The disclosure template bindings for the amounts of the notice, the added field for amounts that cannot be categorized, the report of the difference between the current amount and the itemized total, and the rule that a debt keeps the itemization date once a communication has stated it. These arrive with the validation notice itself and with the derived totals of HiveAR Design Decision 5.

**HiveAR v3+:** The remaining validation information and the state packs, as later decisions of this family specify them.

**Breaking change risk: LOW. This decision adds a decision family and moves statements out of the core text. It changes no stored shape, and the rules it states are pack content that changes at the pack's own cadence.**

**Confidence: MEDIUM. The statements of law were read from the text of the rule, its official interpretation, and the Bureau's compliance aid on the Bureau's site, and they agree with one another. The model notice was not read, the effective date was not recorded, and no one with compliance standing has reviewed the content. The mapping to HiveAR data is straightforward.**

## Implications For Contributors

Statements of what United States law requires belong in the decisions of this family. A decision of the core, a debt-type module, or a pack for another jurisdiction that needs to mention a United States rule refers to the decision of this family by its ID and does not restate the rule.

A debt-type module says which of its buckets carry interest and fees and how placed amounts enter the notice. It does not say what the notice must contain.

Every statement of law in this family carries a verification flag, and it changes only after review by someone with compliance standing.

A pack for another jurisdiction reads the same itemization and the same line classifications and defines its own notice in its own family.
