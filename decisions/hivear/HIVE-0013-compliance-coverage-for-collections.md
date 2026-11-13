---
id: HIVE-0013
title: "Compliance Coverage for Collections"
status: Proposed
version: 0.1
area: hivear
date: 2026-11-12
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 13: Compliance Coverage for Collections

## Decision

HiveAR will hold a debt from collection unless every jurisdiction in which its debtor may be located is covered by the installed packs under the coverage check of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). A debt whose debtor may be in a jurisdiction that is not covered is closed as unsupported before any collector activity begins, or sent to review where the agency's policy chooses review, and an agency can override coverage for a jurisdiction and release a debt from review one at a time. The jurisdictions in which a debtor may be located are the debtor's scope: until the debtor's location is verified, every jurisdiction that an address on file or a presumption points to, such as the state of a phone's area code, and once an address is verified, the jurisdictions of the verified addresses alone. A debt whose debtor has no usable address goes to review, unless an agency setting lets presumptions stand in. This decision also reads Wax Design Decision 8's content tests for collections: a rule on how a collector must treat a debtor or another party is compliance and ships in a Compliance Pack, while a court's procedure and the starting content of a collections operation ship in Boilerplate Packs. It gives the starting configuration for the United States as the worked example.

## Where This Decision Sits

Wax Design Decision 8 defines the constructs, the content tests, the jurisdiction tree with its three marks for each child jurisdiction, the coverage check, overrides, and the packs that an organization writes and designates, all for any domain. This decision says what they mean for debts and collectors. Licensing, which decides whether the agency may collect a debt in a jurisdiction that is covered, is a separate question, which [HiveAR Design Decision 11](HIVE-0011-collector-licensing.md) answers from the agency's authorization records with the same default as coverage: a jurisdiction whose requirements no one has researched holds the debts it could reach until the agency clears it.

## The Content Tests for Collections

The compliance test of Wax Design Decision 8 sends to a Compliance Pack every rule that governs how a collector must treat a debtor or another party, such as what a collector must disclose in a notice, when and how often it may contact a debtor, or what it must stop doing when a debtor asks. A court's procedure is not compliance. The format of a complaint, the margins of a filing, and the number of days that must pass before a motion for summary judgment may be filed govern how the court runs its process, so they ship in the legal module's Boilerplate Pack for that court's state, which configures the case flow that the legal module builds once.

## Coverage of a Debt

A debt is covered when every jurisdiction in its debtor's scope, which the next section describes, is covered under Wax Design Decision 8. Each jurisdiction in scope counts, which is the cautious reading, so a debtor who may be in either of two states is covered only when both are.

The check runs when a debt is created, before any collector activity begins and before entity matching runs, as [HiveAR Design Decision 2](HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md) describes. A debt that is not covered is closed as unsupported, or sent to a review queue where the agency's policy chooses review, so that a specialist can take it or a compliance reviewer can look at it before anyone works it. The check runs again whenever coverage changes, because a pack is installed or removed or an override is set or lifted, and whenever the debtor's scope changes. A debt that was closed as unsupported can be reopened once its jurisdictions are covered. A debt already in collection whose debtor may now be in a jurisdiction that is not covered goes to review rather than closing, so that work in progress is not dropped without a person looking at it.

## The Debtor's Scope

Where a debtor may be is known with one of three levels of confidence, and the levels decide which jurisdictions are in the debtor's scope.

> **LOCATION CONFIDENCE**
>
> **Verified**: an address that the debtor has confirmed as where the debtor is, recorded on the address under [HiveAR Design Decision 3](HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md) with who recorded the confirmation, when, and how, for as long as the address stays verified under that decision.
>
> **Safe assumption**: a current address on file that is neither verified nor flagged as bad. An address flagged as bad does not count.
>
> **Presumption**: a jurisdiction drawn from something other than a current address on file: the state of the area code of a current phone number of the debtor, as the Locale Module resolves it, the debtor's most recent previous address that resolves to a jurisdiction, or the jurisdiction in which the debt originated, where the client reports one with the debt.

Until a location is verified, the debtor's scope is every jurisdiction that a safe assumption or a presumption points to, and every one of them governs: the coverage check must find each of them covered, the Compliance Packs of all of them govern the debt, and every other check that reads the debtor's location applies all of them. A debtor with a New York area code and a California address is therefore treated as possibly in either state. Once an address is verified, the scope is the jurisdictions of every verified address and only those, so safe assumptions and presumptions stop counting, even where a phone's area code points elsewhere.

The area codes of the debtor's current phones always count until a location is verified, and no setting governs them, because a wider scope only adds rules and narrows what is permitted. A previous address and the debt's origin count only as stand-ins, when the debtor has no usable address on file, that is, no current address that resolves to a jurisdiction and is not flagged as bad. An address that names no state, or an armed forces post office address, is not usable, and it adds nothing to the scope of a debtor who also has a usable address. Without a usable address the debtor may be in a jurisdiction that the check cannot see, so by default the debt goes to review. An agency setting, off by default, lets the presumptions alone stand in, so that the debt proceeds with every available presumption in its scope instead of going to review. When no presumption is available, the debt goes to review as before.

The debt records each presumption and stand-in with its source and when it was made, so that a reviewer can see why the debt was worked where it was. A presumption is made again whenever its sources change, a stand-in ends once the debtor has a usable address, and every presumption ends once an address is verified. An address stays verified only while its confidence under HiveAR Design Decision 3 stays above a threshold that the agency sets, and until that decision's confidence decay exists, a verification ends at the first contradiction: the address flagged as bad, the debtor reporting a move, or a different address arriving from a placement, a skip trace, or a change-of-address notice. A new confirmation restores it. When no verified address remains, the scope widens again to every safe assumption and presumption. The coverage check runs again whenever the debtor's scope changes. A debtor's scope is an operating reading of where the debtor may be and not a finding of law, and which law reaches a debtor at an armed forces post office address needs verification.

## Overrides and Releases

Until the Collective publishes packs for the states and other child jurisdictions that an agency works, which their parent packs mark as not yet researched, the agency is expected either to write its own packs for them and designate them under Wax Design Decision 8, which satisfies the hold, or to override the research requirement for those jurisdictions itself. An agency can override coverage for a jurisdiction under Wax Design Decision 8, such as treating Texas as covered without the Texas pack because the agency has written its own Texas rules, and every debt whose jurisdictions are then all covered is released. An agency can also release a single debt from review without overriding its jurisdiction, one debt at a time. Every override and every release is recorded with who made it, when, and why.

## The United States Starting Configuration

For the United States the content tests produce three layers, installed together as the US Bundle. The US Locale Module carries the address structure with its state codes, the SSN and EIN formats and their validation, and the name components. The Region Pack region.us carries the currency and the date and number formats, and a Language Pack such as US English carries the translations. None of these carries compliance. The federal Compliance Pack, compliance.us, carries the federal rules and lists the states and territories as its children, and a Compliance Pack for each state, such as compliance.us.tx, carries that state's additions. The US Boilerplate Pack carries the starting content that a typical agency wants. An agency that litigates adds the legal module's Boilerplate Pack for each state in which it files, which carries that state's court case flow. A state has no Locale Module or Region Pack of its own, because its differences are legal and procedural and not structural: a Louisiana parish is stored in the county field.

The US Bundle is the natural starting configuration for a US-based agency: the US Locale Module, the Region Pack region.us, a US English Language Pack, the appropriate Business Class Module for the agency's vertical, the federal Compliance Pack compliance.us with a Compliance Pack for each state in which the agency collects, and the US Boilerplate Pack. Installing the US Bundle gives an agency a working configured deployment with a single operation.

## The Collections Boilerplate

The US Boilerplate Pack, boilerplate.us.collections, carries the statuses of a typical collections workflow, such as promise to pay, broken promise, and NSF for a returned check, default roles, departments, and rules, workflow definitions, letter templates, report definitions, reason code sets, and industry-standard action and result codes. Further Boilerplate Packs serve other lines of collections work, such as healthcare, auto lending, and first-party collection. The legal module's Boilerplate Pack for a state, such as boilerplate.us.tx.legal_case_flow, carries that state's court case flow. Each is installed as an instance that the agency owns and is encouraged to customize, as Wax Design Decision 8 and [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md) describe.

## Implementation Phasing

**HiveAR v1 (MVP):** The US Boilerplate Pack applied at setup, already installed as an instance that the agency owns, with the delivered version it came from recorded so that its first update can be merged. No coverage check: an agency handles debts from jurisdictions it does not serve by hand. The debtor's scope from verified locations, addresses on file, and the area codes of current phones, for the checks that read the debtor's location.

**HiveAR v2:** The coverage check at debt creation and whenever coverage or a debtor's scope changes, closing as unsupported or sending to review by the agency's policy, overrides by jurisdiction, release from review one debt at a time, and reopening when coverage arrives. Review of a debt whose debtor has no usable address, and the agency setting that lets presumptions, including a previous address and the debt's origin, stand in. Guidance for writing a jurisdiction's pack, published with the pack pipeline of Wax Design Decision 8, so that an agency can write its own packs for the states and other child jurisdictions it works. The US Bundle and further Boilerplate Packs.

**HiveAR v3+:** Coverage of jurisdictions below the state level as their packs are published.

**Breaking change risk: LOW. The check reads the coverage that Wax Design Decision 8 computes and acts only on debts, and its default holds debts rather than releasing them.**

**Confidence: MEDIUM. The coverage rule is a cautious default that will hold many debts until an agency installs or writes its state packs or records overrides, and the right review experience for held debts will need practitioner input.**

## Implications For Contributors

Every path that creates a debt runs the coverage check before any collector activity, and no path works a debt that the check holds.

A rule on how a collector must treat a debtor goes to a Compliance Pack, and a court's procedure goes to the legal module's Boilerplate Pack for that court's state.

Until an address is verified, every jurisdiction in the debtor's scope governs, and once one is verified, only the jurisdictions of the verified addresses do. Nothing stands in for a missing address unless the agency's setting allows it, and every presumption is recorded on the debt with its source and when it was made.

The core never names a jurisdiction. The trees, the marks, and the packs come from what the agency installs, writes, or designates, and an override or a release is always recorded with who made it, when, and why.
