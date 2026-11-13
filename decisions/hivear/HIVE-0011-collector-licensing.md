---
id: HIVE-0011
title: "Collector Licensing"
status: Proposed
version: 0.2
area: hivear
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 11: Collector Licensing

## Decision

HiveAR will check that an organization holds every authorization to collect that an applicable jurisdiction requires for a debt before the organization works the debt, contacts anyone about it, or sues on it. An authorization record states, for an organization and a jurisdiction, that the organization is licensed, registered, or bonded there, that it is exempt on a recorded basis, or that it has determined on a recorded basis that no requirement there reaches its debts, together with the record's number, issuer, scope, and dates. The core supplies the records and the check and holds no requirements: which jurisdictions require an authorization, for which debts and activities, what brings a collector within the requirement, which exemptions it allows, and what follows from collecting without it all come from the Compliance Packs. A debt that an applicable requirement reaches, and for which the organization holds no authorization, is held from collection as the cautious default, and so is a debt that a jurisdiction's requirements could reach while they are not yet researched or are unclear, until the agency clears the jurisdiction. No one overrides a hold in the moment: the way past it is a record, with its basis, of an authorization, an exemption, or the agency's determination. Each check records its answer with its inputs.

## A Mechanism, Not a List of States

Where a jurisdiction licenses, registers, or bonds collectors, its requirement has a few common parts, while the values differ from one jurisdiction to the next and change over time: the debts and activities it reaches, the facts that bring a collector within it, the exemptions it allows, and the consequence of collecting without it. This is the mechanism test of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md): HiveAR builds the parts once, and a Compliance Pack supplies its jurisdiction's values. The United States values are stated in [United States Module Design Decision 6](../modules/united-states/MOD-US-0006-state-collection-licensing.md). Nothing in the core names a jurisdiction, a kind of license, or a bond amount.

Licensing is separate from compliance coverage, which Wax Design Decision 8 computes and [HiveAR Design Decision 13](HIVE-0013-compliance-coverage-for-collections.md) applies to debts. A covered jurisdiction is one whose rules the installed packs supply, so that the platform knows them. An authorization record says whether this organization may collect a given debt there. A covered jurisdiction can still hold debts that its requirement reaches and that the organization is not authorized for, and an organization needs no authorization where no requirement reaches its debts. The two checks share one default: what no one has researched holds the debt until the agency clears it, for coverage by writing or designating a pack or overriding the research requirement, and for licensing by recording an authorization, an exemption, or its own determination.

## Authorization Records

> **AUTHORIZATION RECORD**
>
> **Holder**: the organization of [Wax Design Decision 19](../wax/WAX-0019-organizational-model.md), the legal entity that collects. In later versions a holder can also be an office of the organization or an individual collector, because some jurisdictions license each location or each person (needs verification).
>
> **Jurisdiction**: named by the ISO 3166 codes that Compliance Pack identifiers use, such as us.wa for Washington.
>
> **Kind**: a license, a registration, a bond filing, a notification, an exemption, or a determination. An exemption names the exemption of the requirement that it relies on and records who claimed it and on what evidence. A determination records the agency's own finding that no requirement of the jurisdiction reaches the debts in its scope, with its basis, such as counsel's opinion or the agency's reading of named sources, who made it, and when, and it can carry a review date that is warned of like an expiry. A determination counts only where the governing packs leave the jurisdiction's requirements not yet researched or mark them unclear, and it stops counting once a pack states a requirement that reaches the debts in its scope.
>
> **Scope**: the debts and activities that the authorization covers as the issuing jurisdiction grants it, described with the same properties that a requirement reads, such as a regulatory nature or a contract type.
>
> **Identifiers and dates**: the number, the issuing authority, the effective date, the expiry or renewal date, and the status, such as pending, active, lapsed, suspended, or surrendered.
>
> **Conditions and evidence**: the conditions that the authorization carries, such as a bond or a trust account, recorded as information, and the license or the filing receipt, held in document storage under [Wax Design Decision 30](../wax/WAX-0030-document-storage.md).

An authorization record is an aggregate with its own event history, so the platform can show which authorization stood at the moment of any action. The Pending Event Register of [Wax Design Decision 27](../wax/WAX-0027-pending-event-register.md) schedules a warning ahead of each expiry or renewal date, and a lapse takes effect on its date without anyone having to notice it. Alongside the warnings, a list of the authorizations nearing their expiry or renewal dates is calculated whenever it is read.

## Requirements From the Packs

A Compliance Pack states each requirement of its jurisdiction in the same parts.

> **REQUIREMENT**
>
> **Kind and level**: the authorization that the jurisdiction requires, such as a license, a registration, or a bond filing, and whether it attaches to the organization, an office, or an individual.
>
> **Debts and activities**: which debts the requirement reaches, by their standardized properties under [HiveAR Design Decision 9](HIVE-0009-debt-type-structure-extension.md), such as the regulatory nature flag that each debt carries, consumer or commercial, and which activities, such as collecting for a client under a contingency or servicing contract, buying debt that is in default, or collecting under a name other than the creditor's.
>
> **Triggers**: the facts that bring a collector within the requirement, alone or in combination: the debtor located in the jurisdiction, the client or creditor located there, the organization's office there, or business conducted there.
>
> **Exemptions**: the exemptions that the requirement allows, each with the evidence it needs, such as collecting only by interstate mail and telephone for clients outside the jurisdiction, or holding a license in a jurisdiction that grants the same privilege in return.
>
> **Consequence**: what the jurisdiction says follows from collecting without the authorization, recorded so that the check can apply it, such as a bar on suing on a client's claim.

Every value records its source, its legal force, its effective dates, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values. A Compliance Pack states its jurisdiction's requirements, or states that the jurisdiction has none. A jurisdiction whose pack does neither, or for which no pack is installed, has requirements not yet researched, unless its parent's pack marks it as checked, with nothing to add, in which case it has none of its own. A pack that cannot yet say whether a requirement reaches a kind of debt marks it unclear. The check treats an unclear requirement as reaching the debt, and requirements not yet researched as reaching every debt tied to the jurisdiction by a fact that a requirement can read, every jurisdiction in the debtor's scope included, the cautious reading, until a pack settles them or the agency clears the jurisdiction. Until a jurisdiction's license and bond requirements have been researched and its pack states them, the agency is expected to clear each jurisdiction it works by recording an authorization, an exemption, or its own determination, with its basis, which satisfies the hold. An agency can add requirements of its own in the same shape, such as a client's demand for a license where the law asks for none, and they can only add to what is required.

## Which Requirements Apply

The requirements that apply to a debt are those of every installed Compliance Pack whose triggers the debt's facts meet: every jurisdiction in the debtor's scope under HiveAR Design Decision 13, which until the debtor's location is verified takes in every address on file and every presumption, such as a phone's area code, the client's location, the organization's offices, and the jurisdiction from which the organization acts. Every jurisdiction in the debtor's scope counts, as the candidate time zones do in [HiveAR Design Decision 10](HIVE-0010-contact-windows-frequency-and-permission.md), so that collecting from a debtor who may be in a jurisdiction is treated as collecting there. For a debt with more than one responsible party, such as a co-maker or a guarantor, the scope is the union of every responsible party's scope, as HiveAR Design Decision 13 provides. When a jurisdiction tied to the debt by any of these facts has requirements not yet researched, that jurisdiction applies too. The debt is authorized only when every applicable requirement is met by an active authorization record whose scope covers the debt, or by an exemption on record, and every requirement that is not yet researched or is unclear is cleared by an authorization, an exemption, or a determination whose scope covers the debt.

## The Answer and Its Evidence

The check answers authorized or held. When the answer is held, it names each requirement that is not met and what would meet it, such as a license of a given kind in a given jurisdiction, or, for a jurisdiction whose requirements are not yet researched or are unclear, that the agency must clear it. A held debt is skipped by the work queues and refused by the contact check, and a suit or a referral to counsel is refused for it. A pack can say what else an organization without the authorization may still do, such as accept a payment that the debtor starts, because that answer differs among jurisdictions (needs verification). The check is recorded with the action it precedes, or with the hold, together with the requirements and their versions, the authorization records, the facts it read, and the answer.

What becomes of a held debt is the agency's decision, set by policy: it can stay held while a license is sought, go to a review queue, or be returned to the client. The platform never makes that choice silently.

## Where the Check Runs

The check runs when a debt is approved for collection, the point at which [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md) requires a balance, a responsible party, and an itemization date, so that an import can route a debt that would be held to the exceptions queue of [Shared Design Decision 6](../shared/SHARED-0006-file-interface-engine.md). It runs again on every path that makes an outbound contact, beside the contact check of HiveAR Design Decision 10, and before a debt is referred for suit or a suit is filed. It reruns for the affected debts whenever an authorization record changes, a requirement changes, or a debtor's scope changes, so that a lapse or a move holds the debts it touches. When the check holds a debt, no one overrides it in the moment, and the only way past a requirement is an authorization record or an exemption that the requirement itself allows, or, where the requirement is not yet researched or is unclear, the agency's determination that it does not reach the debt, each with its basis on record.

## Scope and What Branches Off

This decision defines the records, the requirement shape, and the check, and states no jurisdiction's values. It does not enforce the conditions that an authorization carries, such as keeping a bond in force, depositing collections in a trust account, or remitting to clients within a deadline, which the client billing of [HiveAR Design Decision 8](HIVE-0008-client-billing-invoicing-and-statements.md) and a trust accounting capability would have to honor and which are recorded as an open question. It does not decide which jurisdiction's law governs a debt for any purpose other than authorization. It leaves to a later decision the further facts that a requirement may read, such as the creditor's type or the dates on which a debt was sold, also recorded as an open question.

## Implementation Phasing

**HiveAR v1 (MVP):** Authorization records for the organization, one for each jurisdiction, with lapses that take effect on their dates and a list of the authorizations nearing expiry, calculated when it is read. Requirements at the organization level that read the debt's regulatory nature and contract type and trigger on the debtor's and the client's locations, with exemptions on record. The hold for a jurisdiction whose requirements are not yet researched or are unclear, and the agency's determination that clears one. Where the Collective has researched a country's requirement values, they are applied at setup, flagged until verified, the way the federal Compliance Pack and the Boilerplate Pack are, because the pack installation pipeline arrives in v2, as United States Module Design Decision 6 does for the states. The check at debt approval, before outbound contact, and before a suit, with holds and their evidence.

**HiveAR v2:** Office and individual authorizations, exemptions that depend on another authorization, such as a reciprocal license, and re-evaluation at scale when a requirement changes. Warnings ahead of each expiry or renewal date, scheduled through the Pending Event Register of [Wax Design Decision 27](../wax/WAX-0027-pending-event-register.md), which arrives in Wax v2. The license and bond requirements of further jurisdictions, researched and published as their packs' requirement values, each flagged until verified.

**HiveAR v3+:** Checks that the conditions an authorization carries are kept, as the open question resolves.

**Breaking change risk: MEDIUM. The check sits on the paths that work, contact, and sue, so it must be in place from v1, or the debts worked before it existed would have to be examined again. The records and the requirements themselves are additive.**

**Confidence: MEDIUM. The requirement shape fits the 50 states and the District of Columbia as read for United States Module Design Decision 6, and a jurisdiction that licenses by a different test would extend the shape rather than break it.**

## Implications For Contributors

Every path that works a debt, contacts anyone about it, or sues on it runs the check first. A Vendor Integration Module that collects calls the check and keeps no list of licenses.

The core never names a jurisdiction or a kind of license. A requirement selects the debts it reaches by their properties, such as the regulatory nature flag of each debt, never by a module's identity.

An authorization record is evidence. It changes by events, it keeps its history, and its documents are stored with it.

No path overrides a hold. A jurisdiction whose requirements are not yet researched or are unclear holds the debts it could reach until a record with its basis clears it, and a determination never clears a requirement that a pack states.
