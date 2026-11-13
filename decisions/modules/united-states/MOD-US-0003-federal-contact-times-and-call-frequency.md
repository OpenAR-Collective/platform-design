---
id: MOD-US-0003
title: "Federal Contact Times and Call Frequency"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-11-12
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 3: Federal Contact Times and Call Frequency

## Decision

The federal Compliance Pack, compliance.us, will supply the United States federal values for the contact window and the contact frequency counter of [HiveAR Design Decision 10](../../hivear/HIVE-0010-contact-windows-frequency-and-permission.md): the hours that are presumed convenient for communicating with a consumer, and the limits on telephone calls to a person about a debt. It also supplies the federal values for the contact permission of that decision, read on 2026-11-12 from Regulation F and from the Telephone Consumer Protection Act and the Federal Communications Commission's rules under it. The values for the window and the call limits come from Regulation F, 12 CFR part 1006, sections 1006.6 and 1006.14, and their official interpretation. HiveAR will treat the call limits, which the rule states as presumptions, as limits that the check enforces, and an agency may set stricter values. The way past a block under these values is the agency override setting of HiveAR Design Decision 10, which is off unless the agency turns it on. The values from Regulation F govern consumer debts only, meaning debts whose debt type declares the consumer regulatory nature under [HiveAR Design Decision 9](../../hivear/HIVE-0009-debt-type-structure-extension.md), while the values from the Telephone Consumer Protection Act turn on the telephone line called and reach every debt (needs verification). The other rules for commercial debt need separate research and decisions of their own. Every statement of law in this decision is a research finding that needs verification by someone with compliance standing, is educational reference material, and is not legal advice.

## Where This Decision Sits

HiveAR Design Decision 10 builds the contact window, the frequency counter, and the contact permission and holds no values. This decision supplies the federal values as Compliance Pack content under [Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md), the same way [United States Module Design Decision 1](MOD-US-0001-itemization-date-and-validation-itemization.md) supplies the federal values for the validation notice. A state's Compliance Pack adds its own values on the same mechanisms, and under HiveAR Design Decision 10 a contact must satisfy both. The consumer's candidate zones come from the US Locale Module of [United States Module Design Decision 2](MOD-US-0002-country-layer.md).

## Which Debts These Values Govern

The Fair Debt Collection Practices Act and Regulation F govern the collection of consumer debts (needs verification). The pack therefore applies the window and the call limits only to a debt whose debt type declares the consumer regulatory nature, a standardized property under HiveAR Design Decision 9, as [Unsecured Consumer Debt Module Design Decision 1](../unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md) does for unsecured consumer debt. A debt whose type declares the commercial regulatory nature is outside these values. The rules that govern collecting commercial debt in the United States differ, need research of their own, which is recorded as an open question, and will be stated in their own decisions.

## Convenient Times

Absent knowledge of circumstances to the contrary, a time before 8:00 a.m. or after 9:00 p.m., local time at the consumer's location, is presumed inconvenient for communicating with the consumer (needs verification). The source is section 1006.6(b)(1)(i). The pack therefore sets a window from 8:00 a.m. through 9:00 p.m. on every day, for every channel through which the agency communicates with a consumer.

- An electronic communication, such as an email or a text message, occurs when the debt collector sends it, not when the consumer receives or reads it, so the check runs at the moment of sending (needs verification). The source is comment 6(b)(1)(i)-1.
- When the collector's information about the consumer's location conflicts or is ambiguous, such as a phone number whose area code is in one zone and an address in another, the collector communicates at a time that is convenient in all of the locations where the consumer might be (needs verification). The source is comment 6(b)(1)(i)-2. The pack therefore requires the moment to fall inside the window in every candidate zone that the Locale Module returns.
- The prior consent of the consumer, given directly to the debt collector, permits communication outside the window, and consent given to the creditor or to a previous debt collector does not (needs verification). The sources are section 1006.6(b)(4)(i) and its comments. The pack declares this as the window's exception, which the check honors only when the consent is on record as a grant under HiveAR Design Decision 10.

A time that the collector knows is inconvenient for a particular consumer, such as hours the consumer has said are inconvenient, narrows the window further. Under HiveAR Design Decision 10 that knowledge is recorded as a refusal with a window of its own, and how the collector may respond when the consumer starts contact at such a time still needs research.

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

## Contact Permission

HiveAR Design Decision 10 checks permission to use a channel, and it expects the federal pack to state, for every outbound channel, whether permission is needed and how it is obtained, revoked, tracked, and inherited. The values below were read on 2026-11-12 from Regulation F and its official interpretation, from the Telephone Consumer Protection Act, 47 U.S.C. 227, and the Federal Communications Commission's rules at 47 CFR 64.1200, and from the decisions that bear on them. Each is a research finding that needs verification by someone with compliance standing. Where a source leaves a point open, the pack takes the cautious reading. Regulation F's procedures for email and text messages protect a collector from liability for a disclosure to a third party rather than forbid other email or texts (needs verification), and the pack treats them as permission, the cautious reading.

> **FEDERAL PERMISSION SETTINGS BY CHANNEL**
>
> **Calls dialed by hand**: no federal rule was found that requires permission before a collector calls by hand, to a landline or a cell phone (needs verification). The window, the call limits, a place that the consumer has made inconvenient, a workplace where the collector knows the employer prohibits such calls, and a request not to be called still apply, under sections 1006.6(b)(1) and (b)(3) and 1006.14(h).
>
> **Automated or recorded calls to a cell phone**: a call made with an automatic telephone dialing system, or in an artificial or prerecorded voice, to a cell phone needs the called party's prior express consent unless it is made for an emergency purpose, under 47 U.S.C. 227(b)(1)(A)(iii) and 47 CFR 64.1200(a)(1)(iii) (needs verification). After Facebook, Inc. v. Duguid (2021), equipment is an automatic telephone dialing system only if it can store or produce numbers using a random or sequential number generator, so whether a dialer needs consent turns on its design, while a call in an artificial or prerecorded voice needs consent whatever dials it (needs verification). The exception for collecting a debt owed to or guaranteed by the United States was severed in Barr v. American Association of Political Consultants (2020) (needs verification). The pack requires permission for every automated or recorded call to a cell phone, the cautious reading.
>
> **Recorded calls to a residential landline**: a call in an artificial or prerecorded voice to a residential line needs prior express consent unless a rule of the Commission exempts it. The rule exempts a commercial call that neither advertises nor is telemarketing, which the research reads to include a collection call, for up to three calls within any 30 consecutive days, if each call offers a way to opt out and the opt-out is honored, under 47 U.S.C. 227(b)(1)(B) and 47 CFR 64.1200(a)(3)(iii) (needs verification). The pack states this as a limit of three such calls within 30 consecutive days, which a grant on record lifts.
>
> **Text messages**: the Commission and the courts treat a text message to a cell phone as a call under the Telephone Consumer Protection Act, so an automated text needs prior express consent as an automated call does (needs verification). Regulation F's procedures cover a text to a number that the consumer used to text the collector about the debt, or for which the consumer gave consent directly to the collector, in either case within the last 60 days or after a check that the number has not been reassigned, against the Commission's reassigned numbers database or one as complete and accurate (section 1006.6(d)(5), needs verification). The pack requires permission for text messages, from the consumer's own text or consent given directly to the collector, kept good by the 60 days or the check, the cautious reading of both sources.
>
> **Email**: Regulation F's procedures cover an address that the consumer used to email the collector about the debt, or for which the consumer gave consent directly to the collector, which the interpretation says can be given in writing, electronically, or orally. They also cover an address that the creditor obtained from the consumer and used for the account, once the creditor has sent a notice naming the collector and the address, warning that others with access may see the messages, and offering a reasonable and simple way to opt out within a period of at least 35 days, the period has passed without an opt-out, the address's domain is open to the public, and the collector does not know that the consumer's employer provided it. They cover an address that the immediately prior collector used under these procedures without an opt-out as well (section 1006.6(d)(4) and comment 6(d)(4)(i)(B)-1, needs verification). A collector may not email an address that it knows the consumer's employer provided, unless the consumer used it or consented to it, or a prior collector used it under these procedures (section 1006.22(f)(3), needs verification). The pack requires permission for email from one of these sources.
>
> **Letters**: no federal rule was found that requires permission before a letter is mailed (needs verification). A postcard is prohibited (section 1006.22(f)(1)), and a refusal to pay or a request to cease communication, a request not to receive mail, and a request not to be contacted at home still apply.
>
> **Visits**: no federal rule was found that requires permission before a visit (needs verification), and a place that the consumer has made inconvenient still applies.
>
> **Social media**: a communication that the general public or the person's social media contacts can see is prohibited (section 1006.22(f)(4), needs verification). The pack requires permission for any social media channel until its rules are researched further, the cautious reading.

> **REVOKING PERMISSION AND REFUSING CONTACT**
>
> **A medium refused**: a person can ask a collector not to use a medium, such as calls, or one address or number within it, and the collector may then not use it to communicate about any debt, except to confirm an electronic opt-out, to respond once when the person starts contact through that medium, or where other law requires the communication (section 1006.14(h) and comments 14(h)(1)-1 through 14(h)(1)-3, needs verification). Neither the rule nor its comments say that the request must be in writing, so the pack accepts a request in any form, the cautious reading.
>
> **A place or a time made inconvenient**: a consumer can make a time or a place inconvenient by saying so, and a request not to be contacted at home is read to cover mail to the home and calls to the home landline, which makes it a refusal by the home kind of contact point (comments 6(b)(1)-1 and 6(b)(1)-1.iii, needs verification). A workplace is refused when the collector knows or has reason to know that the employer prohibits such communications (section 1006.6(b)(3), needs verification). Consent to be contacted at such a time or place counts only when the consumer gives it directly to the collector (section 1006.6(b)(4)(i), needs verification).
>
> **Cease communication**: a written or electronic notice that the consumer refuses to pay or wants communication to cease stops communication about that debt once the collector receives it, except for a few notices that the rule allows (section 1006.6(c) and comment 6(c)(1)-1, needs verification). It is a refusal of every channel for that debt.
>
> **The opt-out notice**: every electronic communication to an email address, a text number, or another electronic address states a reasonable and simple way to opt out, at no charge (section 1006.6(e), needs verification). The statement belongs in the pack's message templates, and an opt-out received is a refusal of that address or number for every debt (comment 14(h)(1)-3.ii, needs verification).
>
> **Consent to automated or recorded calls and texts withdrawn**: consent can be revoked by any reasonable means, a reply text with the word stop, quit, end, revoke, opt out, cancel, or unsubscribe revokes it, and a revocation must be honored within a reasonable time of no more than ten business days, under 47 CFR 64.1200(a)(10) and (a)(11) (needs verification). The ten business days remain the outer limit, and a period of seven is only proposed. The pack's cautious values accept a revocation in any reasonable form, as if the agency had designated no exclusive method, do not limit a revocation to a category of messages, and treat a revocation as effective when it is recorded, sooner than the rule's outer limit.
>
> **The order effective on 2026-11-25**: FCC 26-67, a Report and Order and Further Notice of Proposed Rulemaking in CG Docket No. 02-278, published at 91 FR 67214 to 67219 on 2026-10-26 and effective on 2026-11-25, changes revocation in these ways (needs verification). A caller may make one or more of three methods its only accepted means of revocation, an automated voice or key-press opt-out on the call, a reply text with any of the seven words, or a website or telephone number that it names, if it discloses the method clearly and conspicuously on every call or text, and a text that names one of the words must still honor all seven. A caller that designates none must accept any reasonable means under 64.1200(a)(11), and no caller may designate another agency's method, such as a written notice under debt collection rules. A caller may treat a revocation made in response to an informational message, one with no advertising or telemarketing, as reaching only that category of messages, the order's example of a category being payment reminders, and the order sets no test for what a category is. A text sent by a protocol that allows no reply must say so in each message and give other ways to revoke. One confirming text stays allowed, presumed within the consent when it is sent within five minutes, without the earlier clauses that it be the only further message and that it may ask which category the person meant. The Commission delegated a plain-language reorganization of 64.1200, so these paragraph citations may change.

> **INHERITING PERMISSION FROM THE CLIENT**
>
> **Consent given to the creditor**: the Commission's 2008 ruling treats a cell phone number given to a creditor in connection with a debt, such as on a credit application, as prior express consent to be called about that debt by the creditor and by a third-party collector acting for it, but not by or for another creditor, and it puts the burden of proving consent on the creditor (needs verification). Courts were divided on the ruling, and after McLaughlin Chiropractic Associates v. McKesson Corp. (2025) a district court is not bound by the Commission's interpretation and decides the statute's meaning itself (needs verification). The pack lets such an inherited grant count for automated or recorded calls and texts when the client's records show that the consumer gave the number to the creditor for the account, and an agency that wants consent given directly to it can narrow the pack by its own rule.
>
> **An email address from the creditor**: an address that the creditor obtained and used becomes usable through the creditor's notice and the expired opt-out period described above, which are the evidence that an inherited grant for email needs.
>
> **What does not carry over**: consent to be contacted at an inconvenient time or place counts only when given directly to the collector, and consent given to a creditor or a previous collector does not count for it (comment 6(b)(4)(i)-2, needs verification). The text message procedures of section 1006.6(d)(5) likewise rest only on the consumer's own texts or consent given directly to the collector.

> **TRACKING**
>
> **Records**: a collector keeps the records that evidence its compliance from the start of collection activity on a debt until three years after its last collection activity on that debt, and keeps any recorded call for three years from the call (section 1006.100, needs verification). Every grant, refusal, and revocation keeps its evidence for at least that long.
>
> **Reassigned numbers**: a grant to call or text a cell phone by automated means can go stale when the number is reassigned, and the pack holds a text grant good for 60 days from the consumer's last text or consent, or from a check against the reassigned numbers database, as section 1006.6(d)(5) describes (needs verification).

The values from Regulation F govern consumer debts, as the rest of this decision does. The values from the Telephone Consumer Protection Act turn on the telephone line called and the means of calling, not on the nature of the debt, so they govern every debt whose party is called at a cell phone or, for recorded calls, at a residential line, commercial debts included (needs verification).

Still to be researched are state laws on calls, texts, and consent, which belong to the state packs; whether a collection call or text is an informational message for the scope of a revocation, which the order of 2026-11-25 does not settle; the Commission's pending proposals on a shorter period for honoring a revocation, on one-way texting, and on a one-step method to revoke everything; how courts now treat consent inherited from a creditor; and how a collector may respond when a consumer starts contact at a time that the consumer has made inconvenient.

## Status of the Content

> **Legal force**: Regulation F, 12 CFR part 1006, is a regulation of the Consumer Financial Protection Bureau that implements the Fair Debt Collection Practices Act, and sections 1006.6 and 1006.14 have an official interpretation. The call limits are presumptions that can be rebutted, not bright-line rules. The Telephone Consumer Protection Act is a federal statute with rules of the Federal Communications Commission under it, and since McLaughlin Chiropractic Associates v. McKesson Corp. (2025) the Commission's interpretations of the statute do not bind a district court. All of this needs verification.
>
> **Effective date**: not recorded. It is to be confirmed against the Federal Register publication of the rule.
>
> **Verification status**: the window and the call limits were read from the Bureau's published text and official interpretation on 2026-10-11. The contact permission values were read on 2026-11-12 from the Bureau's text and interpretation, from the statute and the Commission's rules as the Legal Information Institute publishes them, from the Federal Register text and the Commission's own text of order 26-67, and from law firm summaries of the Supreme Court decisions named. None of it has been reviewed by counsel.
>
> **Coverage**: consumer debts for the values from Regulation F, which the pack identifies by the regulatory nature that their debt type declares, and every debt for the values from the Telephone Consumer Protection Act. Which collectors the rule reaches, such as whether a creditor collecting its own debts is covered, needs verification.

## Implementation Phasing

**HiveAR v1 (MVP):** The window of 8:00 a.m. through 9:00 p.m. at the consumer's location in every candidate zone, the call limit and the quiet period with their exclusions, and the counting of calls by debt, including student loans serviced under one account number. The federal permission settings for every outbound channel, as the section on contact permission states them, flagged until verified, so that the permission check does not fall back to requiring permission for every channel.

**HiveAR v2:** The prior-consent exception for the window and for call counts, which needs consent recorded as evidence, as HiveAR Design Decision 10 phases exceptions.

**HiveAR v3+:** Revisions when the rule or its interpretation changes, each recorded with its effective date.

**Breaking change risk: LOW. The decision is pack content that configures an existing mechanism and changes at the pack's own cadence.**

**Confidence: MEDIUM. The values were read from the text of the rule and its official interpretation, and they agree with one another. The rule states its call limits as presumptions, and treating them as enforced limits is a design choice of this draft. No one with compliance standing has reviewed the content, and the effective date was not recorded. The permission values rest partly on secondary summaries of recent court decisions, which makes them less certain than the window and the limits.**

## Implications For Contributors

These values live only in compliance.us. HiveAR Design Decision 10 and the core never name them.

A change to a value records its source, its legal force, its effective date, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values.

A call records the debts it concerns, so that the counts follow the rule for more than one debt.

A permission value records whether it comes from Regulation F, which reaches consumer debts, or from the Telephone Consumer Protection Act, which turns on the line called.
