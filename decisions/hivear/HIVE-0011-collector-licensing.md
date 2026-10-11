---
id: HIVE-0011
title: "Collector Licensing"
status: Proposed
version: 0.1
area: hivear
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 11: Collector Licensing

## Decision

HiveAR will check that an organization holds every authorization to collect that an applicable jurisdiction requires for a debt before the organization works the debt, contacts anyone about it, or sues on it. An authorization record states, for an organization and a jurisdiction, that the organization is licensed, registered, or bonded there, or that it is exempt on a recorded basis, together with the record's number, issuer, scope, and dates. The core supplies the records and the check and holds no requirements: which jurisdictions require an authorization, for which debts and activities, what brings a collector within the requirement, which exemptions it allows, and what follows from collecting without it all come from the Compliance Packs. A debt that an applicable requirement reaches, and for which the organization holds no authorization, is held from collection as the cautious default, and each check records its answer with its inputs.

## A Mechanism, Not a List of States

Where a jurisdiction licenses, registers, or bonds collectors, its requirement has a few common parts, while the values differ from one jurisdiction to the next and change over time: the debts and activities it reaches, the facts that bring a collector within it, the exemptions it allows, and the consequence of collecting without it. This is the mechanism test of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md): HiveAR builds the parts once, and a Compliance Pack supplies its jurisdiction's values. The United States values are stated in [United States Module Design Decision 6](../modules/united-states/MOD-US-0006-state-collection-licensing.md). Nothing in the core names a jurisdiction, a kind of license, or a bond amount.

Licensing is separate from the auto-close mechanism of Wax Design Decision 8. Installing a jurisdiction's Compliance Pack configures that jurisdiction, so that the platform knows its rules. An authorization record says whether this organization may collect a given debt there. A configured jurisdiction can still hold debts that its requirement reaches and that the organization is not authorized for, and an organization needs no authorization where no requirement reaches its debts.

## Authorization Records

> **AUTHORIZATION RECORD**
>
> **Holder**: the organization of [Wax Design Decision 19](../wax/WAX-0019-organizational-model.md), the legal entity that collects. In later versions a holder can also be an office of the organization or an individual collector, because some jurisdictions license each location or each person (needs verification).
>
> **Jurisdiction**: named by the ISO 3166 codes that Compliance Pack identifiers use, such as us.wa for Washington.
>
> **Kind**: a license, a registration, a bond filing, a notification, or an exemption. An exemption names the exemption of the requirement that it relies on and records who claimed it and on what evidence.
>
> **Scope**: the debts and activities that the authorization covers as the issuing jurisdiction grants it, described with the same properties that a requirement reads, such as a regulatory nature or a contract type.
>
> **Identifiers and dates**: the number, the issuing authority, the effective date, the expiry or renewal date, and the status, such as pending, active, lapsed, suspended, or surrendered.
>
> **Conditions and evidence**: the conditions that the authorization carries, such as a bond or a trust account, recorded as information, and the license or the filing receipt, held in document storage under [Wax Design Decision 30](../wax/WAX-0030-document-storage.md).

An authorization record is an aggregate with its own event history, so the platform can show which authorization stood at the moment of any action. The Pending Event Register of [Wax Design Decision 27](../wax/WAX-0027-pending-event-register.md) schedules a warning ahead of each expiry or renewal date, and a lapse takes effect on its date without anyone having to notice it.

## Requirements From the Packs

A Compliance Pack states each requirement of its jurisdiction in the same parts.

> **REQUIREMENT**
>
> **Kind and level**: the authorization that the jurisdiction requires, such as a license, a registration, or a bond filing, and whether it attaches to the organization, an office, or an individual.
>
> **Debts and activities**: which debts the requirement reaches, by the standardized properties that the debt's type declares under [HiveAR Design Decision 9](HIVE-0009-debt-type-structure-extension.md), such as a consumer or commercial regulatory nature, and which activities, such as collecting for a client under a contingency or servicing contract, buying debt that is in default, or collecting under a name other than the creditor's.
>
> **Triggers**: the facts that bring a collector within the requirement, alone or in combination: the debtor located in the jurisdiction, the client or creditor located there, the organization's office there, or business conducted there.
>
> **Exemptions**: the exemptions that the requirement allows, each with the evidence it needs, such as collecting only by interstate mail and telephone for clients outside the jurisdiction, or holding a license in a jurisdiction that grants the same privilege in return.
>
> **Consequence**: what the jurisdiction says follows from collecting without the authorization, recorded so that the check can apply it, such as a bar on suing on a client's claim.

Every value records its source, its legal force, its effective dates, and its verification status, as Wax Design Decision 8 requires of Compliance Pack values. A pack that cannot yet say whether a requirement reaches a kind of debt marks it unclear, and the check treats an unclear requirement as reaching the debt, the cautious reading, until someone with compliance standing settles it. An agency can add requirements of its own in the same shape, such as a client's demand for a license where the law asks for none, and they can only add to what is required.

## Which Requirements Apply

The requirements that apply to a debt are those of every installed Compliance Pack whose triggers the debt's facts meet: the debtor's locations from the Locale Module, the client's location, the organization's offices, and the jurisdiction from which the organization acts. When the debtor's addresses point to more than one jurisdiction, each one counts, as the candidate time zones do in [HiveAR Design Decision 10](HIVE-0010-contact-windows-and-contact-frequency.md), so that collecting from a debtor who may be in a jurisdiction is treated as collecting there. The debt is authorized only when every applicable requirement is met by an active authorization record whose scope covers the debt, or by an exemption on record.

## The Answer and Its Evidence

The check answers authorized or held. When the answer is held, it names each requirement that is not met and what would meet it, such as a license of a given kind in a given jurisdiction. A held debt is skipped by the work queues and refused by the contact check, and a suit or a referral to counsel is refused for it. A pack can say what else an organization without the authorization may still do, such as accept a payment that the debtor starts, because that answer differs among jurisdictions (needs verification). The check is recorded with the action it precedes, or with the hold, together with the requirements and their versions, the authorization records, the facts it read, and the answer.

What becomes of a held debt is the agency's decision, set by policy: it can stay held while a license is sought, go to a review queue, or be returned to the client. The platform never makes that choice silently.

## Where the Check Runs

The check runs when a debt is approved for collection, the point at which [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md) requires a balance, a responsible party, and an itemization date, so that an import can route a debt that would be held to the exceptions queue of [Shared Design Decision 6](../shared/SHARED-0006-file-interface-engine.md). It runs again on every path that makes an outbound contact, beside the contact check of HiveAR Design Decision 10, and before a debt is referred for suit or a suit is filed. It reruns for the affected debts whenever an authorization record changes, a requirement changes, or a debtor's location changes, so that a lapse or a move holds the debts it touches. When the check holds a debt, no one overrides it in the moment, and the only way past a requirement is an authorization record or an exemption that the requirement itself allows, with its evidence on record.

## Scope and What Branches Off

This decision defines the records, the requirement shape, and the check, and states no jurisdiction's values. It does not enforce the conditions that an authorization carries, such as keeping a bond in force, depositing collections in a trust account, or remitting to clients within a deadline, which the client billing of [HiveAR Design Decision 8](HIVE-0008-client-billing-invoicing-and-statements.md) and a trust accounting capability would have to honor and which are recorded as an open question. It does not decide which jurisdiction's law governs a debt for any purpose other than authorization. It leaves to a later decision the further facts that a requirement may read, such as the creditor's type or the dates on which a debt was sold, also recorded as an open question.

## Implementation Phasing

**HiveAR v1 (MVP):** Authorization records for the organization, one for each jurisdiction, with expiry warnings and lapses that take effect on their dates. Requirements at the organization level that read the debt's regulatory nature and contract type and trigger on the debtor's and the client's locations, with exemptions on record. The check at debt approval, before outbound contact, and before a suit, with holds and their evidence.

**HiveAR v2:** Office and individual authorizations, exemptions that depend on another authorization, such as a reciprocal license, and re-evaluation at scale when a requirement changes.

**HiveAR v3+:** Checks that the conditions an authorization carries are kept, as the open question resolves.

**Breaking change risk: MEDIUM. The check sits on the paths that work, contact, and sue, so it must be in place from v1, or the debts worked before it existed would have to be examined again. The records and the requirements themselves are additive.**

**Confidence: MEDIUM. The requirement shape fits the 50 states and the District of Columbia as read for United States Module Design Decision 6, and a jurisdiction that licenses by a different test would extend the shape rather than break it.**

## Implications For Contributors

Every path that works a debt, contacts anyone about it, or sues on it runs the check first. A Vendor Integration Module that collects calls the check and keeps no list of licenses.

The core never names a jurisdiction or a kind of license. A requirement selects the debts it reaches by the properties that their types declare, never by a module's identity.

An authorization record is evidence. It changes by events, it keeps its history, and its documents are stored with it.
