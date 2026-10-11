---
id: MOD-US-0003
title: "Federal Contact Times and Call Frequency"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 3: Federal Contact Times and Call Frequency

## Decision

The federal Compliance Pack, compliance.us, will supply the United States federal values for the contact window and the contact frequency counter of [HiveAR Design Decision 10](../../hivear/HIVE-0010-contact-windows-and-contact-frequency.md): the hours that are presumed convenient for communicating with a consumer, and the limits on telephone calls to a person about a debt. The values come from Regulation F, 12 CFR part 1006, sections 1006.6 and 1006.14, and their official interpretation. HiveAR will treat the call limits, which the rule states as presumptions, as limits that the check enforces, and an agency may set stricter values. The values govern consumer debts only, meaning debts whose debt type declares the consumer regulatory nature under [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-structure-extension.md), and the rules for commercial debt need separate research and decisions of their own. Every statement of law in this decision is a research finding that needs verification by someone with compliance standing, is educational reference material, and is not legal advice.

## Where This Decision Sits

HiveAR Design Decision 10 builds the contact window and the frequency counter and holds no values. This decision supplies the federal values as Compliance Pack content under [Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md), the same way [United States Module Design Decision 1](MOD-US-0001-itemization-date-and-validation-itemization.md) supplies the federal values for the validation notice. A state's Compliance Pack adds its own values on the same mechanisms, and under HiveAR Design Decision 10 a contact must satisfy both. The consumer's candidate zones come from the US Locale Module of [United States Module Design Decision 2](MOD-US-0002-country-layer.md).

## Which Debts These Values Govern

The Fair Debt Collection Practices Act and Regulation F govern the collection of consumer debts (needs verification). The pack therefore applies the window and the call limits only to a debt whose debt type declares the consumer regulatory nature, a standardized property under HiveAR Design Decision 9, as [Unsecured Consumer Debt Module Design Decision 1](../unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md) does for unsecured consumer debt. A debt whose type declares the commercial regulatory nature is outside these values. The rules that govern collecting commercial debt in the United States differ, need research of their own, which is recorded as an open question, and will be stated in their own decisions.

## Convenient Times

Absent knowledge of circumstances to the contrary, a time before 8:00 a.m. or after 9:00 p.m., local time at the consumer's location, is presumed inconvenient for communicating with the consumer (needs verification). The source is section 1006.6(b)(1)(i). The pack therefore sets a window from 8:00 a.m. through 9:00 p.m. on every day, for every channel through which the agency communicates with a consumer.

- An electronic communication, such as an email or a text message, occurs when the debt collector sends it, not when the consumer receives or reads it, so the check runs at the moment of sending (needs verification). The source is comment 6(b)(1)(i)-1.
- When the collector's information about the consumer's location conflicts or is ambiguous, such as a phone number whose area code is in one zone and an address in another, the collector communicates at a time that is convenient in all of the locations where the consumer might be (needs verification). The source is comment 6(b)(1)(i)-2. The pack therefore requires the moment to fall inside the window in every candidate zone that the Locale Module returns.
- The prior consent of the consumer, given directly to the debt collector, permits communication outside the window, and consent given to the creditor or to a previous debt collector does not (needs verification). The sources are section 1006.6(b)(4)(i) and its comments. The pack declares this as the window's exception, which the check honors only when the consent is on record.

A time that the collector knows is inconvenient for a particular consumer, such as hours the consumer has said are inconvenient, narrows the window further. That knowledge is a restriction the consumer places on contact, which belongs to the separate mechanism recorded as an open question, together with how the collector may respond when the consumer initiates contact at such a time.

## Call Frequency

A debt collector is presumed to comply with the rule against repeated calls if it places a telephone call to a particular person in connection with the collection of a particular debt neither more than seven times within seven consecutive days nor within a period of seven consecutive days after having had a telephone conversation with the person about that debt, with the date of the conversation as the first day (needs verification). A collector that exceeds either frequency is presumed to violate the rule. The source is section 1006.14(b)(2).

> **FEDERAL CALL LIMITS**
>
> **Unit and scope**: telephone calls placed to one person in connection with one debt. A call includes a ringless voicemail and a call that reaches voicemail or another recorded message, and it does not include an email or a text message (needs verification). The limits apply to a third party called to learn the consumer's location as well as to the consumer (needs verification). The sources are comments 14(b)-1, 14(b)(3)(ii)-1, and 14(b)(2)(i)-1.
>
> **Limit**: no more than seven calls within seven consecutive days, a rolling count in HiveAR Design Decision 10's terms.
>
> **Quiet period**: no call within the seven consecutive days that begin on the date of a telephone conversation with the person about the debt, whichever party started the conversation (needs verification). The source is comment 14(b)(4)-1.
>
> **Exclusions**: a call does not count if the person gave prior consent directly to the debt collector and the call falls within the seven consecutive days that begin on the date the consent was received, if it does not connect to the dialed number, or if it is placed to one of the persons listed in section 1006.6(d)(1)(ii) through (vi) (needs verification). The source is section 1006.14(b)(3). A call to a number that turns out not to be the person's does not count as a call to that person (needs verification). The source is comment 14(b)(2)(i)-3.
>
> **More than one debt**: each of a consumer's debts in collection is a particular debt, except that student loans serviced under a single account number when the collector obtained them count as one debt (needs verification). A call about several debts counts toward each of them, and a call that names no debt, such as an unanswered call or a voicemail that refers to no debt, counts toward one debt that the collector chooses (needs verification). The sources are section 1006.14(b)(4) and comment 14(b)(4)-1.

The check of HiveAR Design Decision 10 applies these values as follows. Each call records the debts it concerns, through the communication aggregate's covered debts, and counts toward each of them. For a call that names no debt, the check permits the call when at least one of the person's debts has room under both limits, and it records the call against such a debt. The seven consecutive days are counted as calendar days in the zone that the window uses, a choice of this draft.

## What These Values Do Not Cover

The federal rule sets no count for email or text messages, though conduct across channels can still be harassment when taken together (needs verification). The source is comment 14(a)-2. An agency that wants a limit on messages sets it in its own rules. Communications with third parties to learn a consumer's location are governed by section 1006.10, and a state's rules, such as its own limits on calls, belong to that state's Compliance Pack. Both are for later decisions.

## Status of the Content

> **Legal force**: Regulation F, 12 CFR part 1006, is a regulation of the Consumer Financial Protection Bureau that implements the Fair Debt Collection Practices Act, and sections 1006.6 and 1006.14 have an official interpretation. The call limits are presumptions that can be rebutted, not bright-line rules. All of this needs verification.
>
> **Effective date**: not recorded. It is to be confirmed against the Federal Register publication of the rule.
>
> **Verification status**: read from the Bureau's published text and official interpretation on 2026-10-11 by the drafter and not reviewed by counsel.
>
> **Coverage**: consumer debts, which the pack identifies by the regulatory nature that their debt type declares. Which collectors the rule reaches, such as whether a creditor collecting its own debts is covered, needs verification.

## Implementation Phasing

**HiveAR v1 (MVP):** The window of 8:00 a.m. through 9:00 p.m. at the consumer's location in every candidate zone, the call limit and the quiet period with their exclusions, and the counting of calls by debt, including student loans serviced under one account number.

**HiveAR v2:** The prior-consent exception for the window and for call counts, which needs consent recorded as evidence, as HiveAR Design Decision 10 phases exceptions.

**HiveAR v3+:** Revisions when the rule or its interpretation changes, each recorded with its effective date.

**Breaking change risk: LOW. The decision is pack content that configures an existing mechanism and changes at the pack's own cadence.**

**Confidence: MEDIUM. The values were read from the text of the rule and its official interpretation, and they agree with one another. The rule states its call limits as presumptions, and treating them as enforced limits is a design choice of this draft. No one with compliance standing has reviewed the content, and the effective date was not recorded.**

## Implications For Contributors

These values live only in compliance.us. HiveAR Design Decision 10 and the core never name them.

A change to a value records its source, its legal force, its effective date, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values.

A call records the debts it concerns, so that the counts follow the rule for more than one debt.
