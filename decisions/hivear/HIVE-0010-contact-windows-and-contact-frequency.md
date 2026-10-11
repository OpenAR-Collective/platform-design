---
id: HIVE-0010
title: "Contact Windows and Contact Frequency"
status: Proposed
version: 0.1
area: hivear
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 10: Contact Windows and Contact Frequency

## Decision

HiveAR will check every outbound contact against two mechanisms before it is made. A contact window says whether the present moment is a permitted time to reach a party through a channel, evaluated in the party's own time zone. A contact frequency counter says whether another contact would exceed a limit on contacts within a period. The core supplies the mechanisms and holds no values: every window, limit, period, and exception comes from the Compliance Packs that govern the debt and from the agency's own stricter rules, and a contact is permitted only when every applicable rule permits it. Each check records its answer with its inputs, so that an agency can show afterward why a contact was or was not made.

## A Mechanism, Not a Rule

Contact timing is the clearest case of the mechanism test in [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). Jurisdictions that limit contact tend to do it with a few common shapes, a window of permitted hours and a cap on contacts within a period, while the hours, the caps, the periods, and the exceptions differ from one jurisdiction to the next and change over time. HiveAR builds the shapes once, and a Compliance Pack supplies the values for its jurisdiction. The United States values will be stated in a decision of the United States layer. Nothing in the core names an hour, a count, or a number of days.

## The Contact Window

> **CONTACT WINDOW**
>
> **What a window rule says**: the hours during which a party may be contacted through a channel, for each kind of day. Channels are the communication channel types of [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md), such as calls, text messages, email, visits, and letters, and a rule names the channels it covers. Kinds of day are weekdays, weekend days, and non-working dates, taken from a calendar in the shape that [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md) defines and that the rule names. A rule can differ by the party's role on the debt under [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), so that a debtor and a third party contacted to locate the debtor can have different windows.
>
> **Whose time**: the window is evaluated in the party's own zone, as Wax Design Decision 12 requires for permitted contact times. The Locale Module for the party's country returns the zones the party can be in, from an address or a phone number, as [United States Module Design Decision 2](../modules/united-states/MOD-US-0002-country-layer.md) does for the United States. When it returns more than one zone, the Compliance Pack decides how to treat the candidates, for example by permitting contact only when the moment falls inside the window in every candidate zone.
>
> **Exceptions**: a rule can name the exceptions its jurisdiction allows, such as a party's recorded consent to be contacted at another time, and the check honors an exception only when its evidence is on record.

## The Contact Frequency Counter

> **CONTACT FREQUENCY**
>
> **What a limit rule says**: how many contacts of a given unit are allowed within a period, over a given scope. The unit is an attempt, a conversation with the party, or a message sent. The period is a rolling number of days, a calendar day, or a calendar week. The scope is one debt, a debt group at any level of [HiveAR Design Decision 4](HIVE-0004-debt-groups.md), the party across the debts of one client, or the party across the agency.
>
> **Quiet periods**: a rule can also require a pause after an event, such as no further call for a number of days after a conversation with the party.
>
> **Exclusions**: a rule can leave kinds of contact out of a count, such as an attempt that never connected or a contact the party started.
>
> **Counts**: counts are kept from the communication events of [Wax Design Decision 1](../wax/WAX-0001-enriched-event-sourcing.md) and maintained as contacts happen by the event-driven path, not computed at the moment of the check, in the same way that entity aggregate fields are maintained under HiveAR Design Decision 1.

## Which Rules Apply

The rules that apply to a contact are those of every Compliance Pack that governs the debt, such as the federal pack and the pack for the state in which the debtor lives, together with the agency's own rules. A contact is permitted only when all of them permit it, so the strictest window and the lowest limit govern, and no pack has to know about another. Which packs govern a debt, and how a federal pack and a state pack combine when they define the same thing differently, remain open questions, but windows and limits need no further choice under this rule.

An agency can add its own rules in the same shapes, for a client's contract or for its own policy, and they can only narrow what is permitted. A Compliance Pack's values are the agency's to edit once installed, as Wax Design Decision 11 describes, so the platform will show wherever an agency's value is looser than the value its pack published, and every change to a value is versioned under [Wax Design Decision 21](../wax/WAX-0021-configuration-management-and-environment-lifecycle.md).

## The Answer and Its Evidence

The check answers permitted or not permitted. When the answer is not permitted, it names the rule that blocked the contact and the next moment at which the contact would be permitted, so that a dialer, a queue, or a collector's screen can move on, and the Pending Event Register of [Wax Design Decision 27](../wax/WAX-0027-pending-event-register.md) can schedule a retry. The check that precedes a contact is recorded with the contact's communication event: the zones considered, the rules and their versions, the counts at the time, and the answer. A contact the check refused is recorded as refused. An agency can then show, for any contact, which rules applied and what they said.

## Where the Check Runs

Every path that makes an outbound contact runs the check first: a collector's screen before a manual call or message, the work queues and dialer campaigns of [HiveAR Design Decision 3](HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md) when they choose whom to contact, and the dialer, texting, and email integrations when they send. A Vendor Integration Module that makes contact calls the check and keeps no copy of the rules. A contact the party starts, such as an inbound call, is not checked, although a rule can count it. When the check blocks a contact, no one overrides it in the moment, and the only way past a rule is an exception that the rule itself allows, with its evidence on record.

## Scope and What Branches Off

This decision defines the mechanisms and states no jurisdiction's values. It does not define the restrictions that a party can place on contact, such as a request to stop, to use only one channel, or not to be contacted at work, which are a separate mechanism that can only narrow what this one permits and are recorded as an open question. It does not define the communications module, whose channels and integrations remain on the module roadmap.

## Implementation Phasing

**HiveAR v1 (MVP):** The window check and the frequency counter, with quiet periods and exclusions, for calls, text messages, and email, the evidence recorded with each contact, and the next permitted moment returned. The collector's screens and the work queues use the check. The United States values come from the federal Compliance Pack.

**HiveAR v2:** The dialer, texting, and email integrations call the check as the communications module arrives. Visits, exceptions backed by recorded consent, and the warning where an agency's value is looser than its pack's.

**HiveAR v3+:** Further units, periods, and scopes as jurisdictions require them.

**Breaking change risk: LOW. The check reads events that already exist and adds a projection of counts and a recorded answer. The part to get right from the start is the evidence recorded with each contact, because an agency's proof depends on it and it cannot be added to past contacts later.**

## Implications For Contributors

No code names an hour, a count, or a period for contact. Values come only from Compliance Packs and the agency's own rules.

Every outbound contact path calls the check, vendor integrations included, and none keeps its own copy of the rules.

A rule never works out a party's zone on its own. It asks the Locale Module for the candidate zones and applies the choice its Compliance Pack makes.

A blocked contact is never overridden in the moment. The way past a rule is an exception that the rule allows, with its evidence on record.

The evidence of each check is recorded with the contact, or with the refusal, so that the answer can be shown later.
