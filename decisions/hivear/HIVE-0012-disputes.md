---
id: HIVE-0012
title: "Disputes"
status: Proposed
version: 0.1
area: hivear
date: 2026-11-13
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 12: Disputes

## Decision

HiveAR will record a dispute as a member object of the debt it concerns. A dispute says that the consumer disputes some or all of what the debt shows owed, and it names the amounts. Opening a dispute moves each named amount out of its bucket and into that bucket's disputed counterpart, where payments never reach it, and a dispute that names no amounts moves every balance that payments can reach and holds every amount posted to the debt while it is open. Interest that accrues on a held amount is held with it. An amount leaves a counterpart in only three ways: it moves back to its bare bucket, which needs the consumer's recorded direction, it leaves through the resolution of the dispute, or a balance adjustment reduces it. Every move posts nothing to the ledger. The mechanism is the same in every jurisdiction. What a jurisdiction requires of a collector when a consumer disputes a debt is Compliance Pack content, and this decision states none of it.

## A Dispute Is a Member of the Debt

[Wax Design Decision 1](../wax/WAX-0001-enriched-event-sourcing.md) makes a dispute a member object of the debt aggregate and not an aggregate root. The debt owns the dispute lifecycle, the events that describe a dispute are attributed to the debt, and the dispute's identity travels in the event payload. A consumer who disputes several debts at once produces one independent dispute on each debt, because each follows its own path from there. The disputes may carry the same initiating batch reference for traceability, as Wax Design Decision 1 describes. A debt can have more than one open dispute, for example one about a fee and one about the principal. Each dispute holds the amounts it moved, so the disputed counterpart of a bucket carries the sum of what the debt's open disputes hold, and a dispute never takes an amount from another dispute. Which level of a grouping hierarchy a dispute attaches to when each charge is a debt is an open question in [OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md), and until it is answered a dispute attaches to a debt.

> **WHAT A DISPUTE RECORDS**
>
> **Debt**: the debt the dispute concerns.
>
> **Type**: a reference value from the dispute types of [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md). A type named for a statute comes from that jurisdiction's Compliance Pack.
>
> **Scope**: the amounts the dispute holds, each a bucket on the debt and a typed monetary value in the debt's currency, and optionally references to the itemization lines the consumer named. A reference is evidence only: it changes no line, posts nothing, and is not itself an amount that the dispute holds.
>
> **Opened**: the civil date on which the consumer raised the dispute, as [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md) defines it, who recorded it, and the source, such as a call, a letter, a file, or an API client.
>
> **Reason**: the consumer's stated reason, as a free-text note under Wax Design Decision 12.
>
> **Status and outcome**: open, resolved, or withdrawn and, when resolved, whether the dispute was upheld, partly upheld, or not upheld. A dispute that a balance adjustment ends has no finding, and it is resolved with that adjustment recorded as the way it ended.

## Opening a Dispute

A dispute names its scope as amounts in buckets: all of one bucket, part of a bucket, or several buckets. The person recording the dispute chooses the buckets and amounts that match what the consumer disputes. Opening the dispute moves each named amount from its bucket to that bucket's disputed counterpart by the transfer that [HiveAR Design Decision 5](HIVE-0005-debt-structure-and-balance-composition.md) defines, in one transaction with the dispute.opened event. A dispute that names no scope moves the whole balance of every bare bucket on the debt and holds what is later posted to the debt while it is open, as the section on postings while a dispute is open describes.

The debt's balance is the sum of its buckets, disputed counterparts included, so a dispute never changes what the debt shows owed. It changes what payments can reach. The moves post nothing to the general ledger, because no money moves, as [HiveAR Design Decision 6](HIVE-0006-gaap-journal-and-general-ledger.md) provides. A move changes the balance that interest accrues on, and how interest is posted at a move is part of the open question on interest posting points in OPEN-QUESTIONS.md.

## Narrowing and Withdrawing

While a dispute is open, the consumer can narrow it. Narrowing moves some of the amount the dispute holds back to its bare bucket and is recorded as a dispute.narrowed event. The move back needs the consumer's direction, recorded as [HiveAR Design Decision 7](HIVE-0007-payment-application-and-waterfall.md) defines it, so a narrowing is accepted only when its command states that the consumer directed it, whoever enters the command. A payment never carries a narrowing. A consumer who wants to pay a held amount first narrows the dispute by directing the amount back, and the amount is then paid like any other, as [HiveAR Design Decision 7](HIVE-0007-payment-application-and-waterfall.md) describes. Paying an amount while its dispute stays open, a payment under protest that might be refunded once the dispute is resolved, is not offered in v1 and is an open question in OPEN-QUESTIONS.md. A narrowing that moves the last held amount back is a withdrawal of the dispute and is recorded as one. The consumer can also withdraw the dispute outright, which moves everything it still holds back to the bare buckets, carries the same recorded direction, and is recorded as a dispute.withdrawn event.

## Resolving

A dispute is resolved by a finding, recorded as a dispute.resolved event with who made the finding and the source, that decides each amount the dispute still holds. An amount that the finding upholds is adjusted off by a balance adjustment taken from the disputed counterpart, with a dispute resolution reason code from the registry of [Wax Design Decision 20](../wax/WAX-0020-reason-code-registry.md). The adjustment follows HiveAR Design Decision 6: it posts nothing to the ledger and reverses no revenue, since the adjusted amount was never collected. An amount that the finding does not uphold stays in the counterpart until the consumer directs it back. An agency setting, off by default, moves such an amount back when the dispute is resolved, without a new direction. A Compliance Pack can publish its own value for the setting, which stays flagged until someone with compliance standing verifies it, and the platform shows an agency value that is looser than its pack's.

A finding can also direct an amount to a bucket other than its bare bucket. The legal module is expected to do this for a court's judgment: the amount that the court awards moves by transfer to a judgment bucket, which can bear interest, and any held amount the court does not award is adjusted off. This decision provides the transfer and the adjustment that the module will use, and it does not define the judgment bucket. A dispute is upheld when its finding upholds everything it held, partly upheld when the finding upholds some of it, and not upheld when the finding upholds none of it.

## Adjusting an Amount in Dispute

A balance adjustment posts to a counterpart as it does to any bucket, because the counterpart is part of the debt's balance and a dispute does not block an adjustment. A client's balance-reducing adjustment and the forgiven remainder of a settlement can therefore take an amount out of a counterpart. A payment is the one thing that never posts there. An adjustment that reduces a counterpart names the dispute whose held amount it reduces, so that the counterpart still equals the sum of what the debt's open disputes hold. When the adjustment names none, it reduces the held amounts in the order in which the disputes were opened, the earliest first, each down to zero before the next. An adjustment reduces a held amount by at most what it holds. When an adjustment takes everything a dispute holds to zero, the dispute ends, as the status and outcome entry above describes. A balance adjustment may increase a counterpart, such as a fee assessed on an amount in dispute, only when it names the dispute that holds the increase.

## Postings While a Dispute Is Open

Interest that accrues on an amount in a counterpart posts to the counterpart of the interest bucket, where the same dispute holds it, so that interest produced by a disputed amount never becomes reachable by a payment. A dispute that names no scope holds every amount later posted to the debt while it is open, such as interest or a fee: each posts to the counterpart of its bucket and is held with the rest. When more than one dispute that names no scope is open, the earliest holds the later postings, in the same order in which an adjustment reduces held amounts. When accrued interest is posted, and whether opening, narrowing, or resolving a dispute is a posting point, stay with the open question on interest calculation and posting points in OPEN-QUESTIONS.md.

## Defaults and Where Values Come From

The core ships cautious defaults, as the default test of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md) requires. A payment never applies to a disputed counterpart, and no configuration changes that. A dispute that names no scope moves the whole balance and holds what is posted while it is open. A resolution that does not uphold an amount leaves it held until the consumer directs it back or the agency's setting moves it back. A disputed counterpart takes every attribute of its bare bucket except how payments apply, so opening a dispute decides nothing about interest or the current-due amount. A Boilerplate Pack can set a conservative starting value for any setting that these mechanisms expose, such as the interest setting of a counterpart, and a Compliance Pack replaces a default with the value that a jurisdiction's law sets and keeps it flagged until verified.

## Scope and What Branches Off

This decision defines the dispute object, its scope, and its events. It does not say what a collector must do, stop doing, or provide when a consumer disputes a debt, because those are rules of a jurisdiction and belong in its Compliance Pack. The buckets, their counterparts, and the transfer are defined in HiveAR Design Decision 5. The recorded consumer direction and the way a payment treats an amount in dispute are defined in HiveAR Design Decision 7, and [United States Module Design Decision 4](../modules/united-states/MOD-US-0004-federal-payment-allocation-across-debts.md) describes the United States federal values for them. How a dispute is reported to the credit bureaus belongs to credit reporting, which OPEN-QUESTIONS.md records as an open question.

## Implementation Phasing

**HiveAR v1 (MVP):** The dispute as a member of the debt, with its record and its four events, the disputed counterpart of every bucket, the moves into and out of counterparts, adjustment on upholding, the transfer that a finding can direct, the recorded consumer direction on a narrowing or a withdrawal, interest on a held amount posted to the counterpart of its interest bucket, a dispute with no scope holding what is posted while it is open, and the agency setting, off by default, that moves a not-upheld amount back when the dispute is resolved.

**HiveAR v2:** The attachment of a dispute to a level of a grouping hierarchy once the open question on the compliance unit is answered, and payment of an amount while its dispute stays open, if the open question on paying an amount in dispute decides to allow it.

**Breaking change risk: LOW.** The dispute is a member object of the debt, the counterparts are ordinary buckets, and every move is a posting that the existing balance model already carries, so later settings are additive.

## Implications For Contributors

A dispute is a member of the debt and never an aggregate root. No code creates a dispute aggregate or attributes a dispute event to anything but the debt.

No code applies a payment to a disputed counterpart. An amount leaves a counterpart only through the events this decision defines: a move back with the consumer's recorded direction or under the agency's setting when a finding does not uphold it, an adjustment when a finding upholds it or an ordinary balance adjustment reduces it, or a transfer that a finding directs. A move back is its own command and never part of a payment.

Every move between a bucket and its counterpart is a transfer, and a transfer posts nothing to the ledger.

Interest that accrues on a held amount posts to the counterpart of the interest bucket, and while a dispute that names no scope is open, every posting to the debt lands in the counterpart of its bucket. No code posts either to a bare bucket.

No code or decision states what a jurisdiction requires when a consumer disputes a debt. That belongs in a Compliance Pack, and the core carries only the mechanism and its cautious defaults.
