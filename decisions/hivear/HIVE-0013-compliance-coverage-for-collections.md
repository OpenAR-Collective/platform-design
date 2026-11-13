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

HiveAR will hold a debt from collection unless every jurisdiction in which its debtor may be located is covered by the installed packs under the coverage check of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). A debt whose debtor may be in a jurisdiction that is not covered is closed as unsupported before any collector activity begins, or sent to review where the agency's policy chooses review, and an agency can override coverage for a jurisdiction and release a debt from review one at a time. When a debtor's location cannot be resolved from a current address, the debt goes to review, unless an agency setting allows a jurisdiction to be presumed from a previous address, a phone number, or the debt's origin. This decision also reads Wax Design Decision 8's content tests for collections: a rule on how a collector must treat a debtor or another party is compliance and ships in a Compliance Pack, while a court's procedure and the starting content of a collections operation ship in Boilerplate Packs. It gives the starting configuration for the United States as the worked example.

## Where This Decision Sits

Wax Design Decision 8 defines the constructs, the content tests, the jurisdiction tree with its three marks for each child jurisdiction, the coverage check, overrides, and the packs that an organization writes and designates, all for any domain. This decision says what they mean for debts and collectors. Licensing, which decides whether the agency may collect a debt in a jurisdiction that is covered, is a separate question.

## The Content Tests for Collections

The compliance test of Wax Design Decision 8 sends to a Compliance Pack every rule that governs how a collector must treat a debtor or another party, such as what a collector must disclose in a notice, when and how often it may contact a debtor, or what it must stop doing when a debtor asks. A court's procedure is not compliance. The format of a complaint, the margins of a filing, and the number of days that must pass before a motion for summary judgment may be filed govern how the court runs its process, so they ship in the legal module's Boilerplate Pack for that court's state, which configures the case flow that the legal module builds once.

## Coverage of a Debt

A debt is covered when every jurisdiction in which its debtor may be located is covered under Wax Design Decision 8. Those jurisdictions are the ones that the debtor's current addresses point to, as the Locale Module structures them, such as the state of a United States address. When the addresses point to more than one jurisdiction, each one counts, which is the cautious reading. When a debtor has no current address, or any of the debtor's current addresses resolves to no jurisdiction, such as an address that names no state or province or an armed forces post office address, the debtor may be in a jurisdiction that the check cannot see. By default nothing is presumed and the debt goes to review, unless the agency allows a presumed jurisdiction, as the next section describes.

The check runs when a debt is created, before any collector activity begins and before entity matching runs, as [HiveAR Design Decision 2](HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md) describes. A debt that is not covered is closed as unsupported, or sent to a review queue where the agency's policy chooses review, so that a specialist can take it or a compliance reviewer can look at it before anyone works it. The check runs again whenever coverage changes, because a pack is installed or removed or an override is set or lifted, and whenever a debtor's addresses change. A debt that was closed as unsupported can be reopened once its jurisdictions are covered. A debt already in collection whose debtor may now be in a jurisdiction that is not covered goes to review rather than closing, so that work in progress is not dropped without a person looking at it.

## A Presumed Jurisdiction

An agency setting can allow a presumed jurisdiction for a debtor who has no current address, or a current address that resolves to no jurisdiction. By default the setting is off, so the delivered workflow presumes nothing and sends the debt to review. Where the setting is on, the presumption comes from the first of these sources, in the order that the agency sets, that yields a jurisdiction.

> **SOURCES OF A PRESUMED JURISDICTION**
>
> **A previous address**: the jurisdiction of the debtor's most recent previous address that resolves to one.
>
> **A phone number**: the jurisdiction to which the area code of a current phone number of the debtor belongs, as the Locale Module resolves it. When the debtor's phone numbers point to more than one jurisdiction, each one counts.
>
> **The debt's origin**: the jurisdiction in which the debt originated, where the client reports one with the debt.

The debtor is then treated as located in the presumed jurisdiction, alongside any jurisdiction that a current address points to, wherever HiveAR reads where the debtor may be: for the coverage of the debt, for the Compliance Packs that govern it, and for every other check that reads the debtor's location. When no source yields a jurisdiction, the debt goes to review as before. The debt records each presumption with its source and when it was made, so that a reviewer can see why the debt was worked where it was. A presumption is made again whenever its sources change, it ends once every current address of the debtor resolves to a jurisdiction, and the coverage check runs again whenever a presumption is made, changes, or ends. A presumption is an operating choice of the agency and not a finding of law, and which law reaches a debtor at an armed forces post office address needs verification.

## Overrides and Releases

Until the Collective publishes packs for the states and other child jurisdictions that an agency works, which their parent packs mark as not yet researched, the agency is expected either to write its own packs for them and designate them under Wax Design Decision 8, which satisfies the hold, or to override the research requirement for those jurisdictions itself. An agency can override coverage for a jurisdiction under Wax Design Decision 8, such as treating Texas as covered without the Texas pack because the agency has written its own Texas rules, and every debt whose jurisdictions are then all covered is released. An agency can also release a single debt from review without overriding its jurisdiction, one debt at a time. Every override and every release is recorded with who made it, when, and why.

## The United States Starting Configuration

For the United States the content tests produce three layers, installed together as the US Bundle. The US Locale Module carries the address structure with its state codes, the SSN and EIN formats and their validation, and the name components. The Region Pack region.us carries the currency and the date and number formats, and a Language Pack such as US English carries the translations. None of these carries compliance. The federal Compliance Pack, compliance.us, carries the federal rules and lists the states and territories as its children, and a Compliance Pack for each state, such as compliance.us.tx, carries that state's additions. The US Boilerplate Pack carries the starting content that a typical agency wants. An agency that litigates adds the legal module's Boilerplate Pack for each state in which it files, which carries that state's court case flow. A state has no Locale Module or Region Pack of its own, because its differences are legal and procedural and not structural: a Louisiana parish is stored in the county field.

The US Bundle is the natural starting configuration for a US-based agency: the US Locale Module, the Region Pack region.us, a US English Language Pack, the appropriate Business Class Module for the agency's vertical, the federal Compliance Pack compliance.us with a Compliance Pack for each state in which the agency collects, and the US Boilerplate Pack. Installing the US Bundle gives an agency a working configured deployment with a single operation.

## The Collections Boilerplate

The US Boilerplate Pack, boilerplate.us.collections, carries the statuses of a typical collections workflow, such as promise to pay, broken promise, and NSF for a returned check, default roles, departments, and rules, workflow definitions, letter templates, report definitions, reason code sets, and industry-standard action and result codes. Further Boilerplate Packs serve other lines of collections work, such as healthcare, auto lending, and first-party collection. The legal module's Boilerplate Pack for a state, such as boilerplate.us.tx.legal_case_flow, carries that state's court case flow. Each is installed as an instance that the agency owns and is encouraged to customize, as Wax Design Decision 8 and [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md) describe.

## Implementation Phasing

**HiveAR v1 (MVP):** The US Boilerplate Pack applied at setup, already installed as an instance that the agency owns, with the delivered version it came from recorded so that its first update can be merged. No coverage check: an agency handles debts from jurisdictions it does not serve by hand.

**HiveAR v2:** The coverage check at debt creation and whenever coverage or a debtor's addresses change, closing as unsupported or sending to review by the agency's policy, overrides by jurisdiction, release from review one debt at a time, and reopening when coverage arrives. The agency setting that allows a presumed jurisdiction, with its sources in the agency's order. Guidance for writing a jurisdiction's pack, published with the pack pipeline of Wax Design Decision 8, so that an agency can write its own packs for the states and other child jurisdictions it works. The US Bundle and further Boilerplate Packs.

**HiveAR v3+:** Coverage of jurisdictions below the state level as their packs are published.

**Breaking change risk: LOW. The check reads the coverage that Wax Design Decision 8 computes and acts only on debts, and its default holds debts rather than releasing them.**

**Confidence: MEDIUM. The coverage rule is a cautious default that will hold many debts until an agency installs or writes its state packs or records overrides, and the right review experience for held debts will need practitioner input.**

## Implications For Contributors

Every path that creates a debt runs the coverage check before any collector activity, and no path works a debt that the check holds.

A rule on how a collector must treat a debtor goes to a Compliance Pack, and a court's procedure goes to the legal module's Boilerplate Pack for that court's state.

Nothing presumes a jurisdiction unless the agency's setting allows it, and a presumption is recorded on the debt with its source and when it was made.

The core never names a jurisdiction. The trees, the marks, and the packs come from what the agency installs, writes, or designates, and an override or a release is always recorded with who made it, when, and why.
