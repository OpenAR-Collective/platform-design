---
id: HIVE-0010
title: "Contact Windows, Frequency, and Permission"
status: Proposed
version: 0.1
area: hivear
date: 2026-11-12
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 10: Contact Windows, Frequency, and Permission

## Decision

HiveAR will check every outbound contact against three mechanisms before it is made. A contact window says whether the present moment is a permitted time to reach a party through a channel, evaluated in the party's own time zone. A contact frequency counter says whether another contact would exceed a limit on contacts within a period. A contact permission says whether the party may be reached through that channel at that contact point at all, from the grants and refusals on record for the party, each with its source, its evidence, its own windows, its dates, and any revocation. The core supplies the mechanisms and holds no values: every window, limit, period, permission requirement, and exception comes from the Compliance Packs that govern the debt and from the agency's own stricter rules, and a contact is permitted only when every applicable rule of all three mechanisms permits it. A Compliance Pack states for every channel whether permission is needed, and where a governing pack leaves a channel out, the channel needs permission, which is the cautious default. An agency setting decides whether a blocked contact can be overridden in the moment, by default it cannot, and where an agency allows overrides, settings at the user and group level decide which users may perform them. Each check records its answer with its inputs, and each override records who made it, when, and why, so that an agency can show afterward why a contact was or was not made.

## A Mechanism, Not a Rule

Contact timing is the clearest case of the mechanism test in [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md). Jurisdictions that limit contact tend to do it with a few common shapes, a window of permitted hours and a cap on contacts within a period, while the hours, the caps, the periods, and the exceptions differ from one jurisdiction to the next and change over time. HiveAR builds the shapes once, and a Compliance Pack supplies the values for its jurisdiction. The United States values will be stated in a decision of the United States layer. Nothing in the core names an hour, a count, or a number of days.

Permission follows the same pattern. Jurisdictions differ in which channels need a party's permission before they are used and in how that permission is obtained, revoked, tracked, and inherited, while the shape of a permission is common to all of them: a party, a channel, a contact point, a source, its evidence, and its dates. HiveAR builds the permission and its check once, and each Compliance Pack says what its jurisdiction requires for each channel. The core names no channel's requirement, and where no governing pack states one, it applies the cautious default that the channel needs permission.

## The Contact Window

> **CONTACT WINDOW**
>
> **What a window rule says**: the hours during which a party may be contacted through a channel, for each kind of day. Channels are the communication channel types of [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md), such as calls, text messages, email, visits, and letters, and a rule names the channels it covers, which it can narrow by how a contact is made, such as dialed by hand, dialed by an automated system, or delivered in an artificial or recorded voice, and by the kind of contact point, such as a cell phone or a landline. Kinds of day are weekdays, weekend days, and non-working dates, taken from a calendar in the shape that [Wax Design Decision 12](../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md) defines and that the rule names. A rule can differ by the party's role on the debt under [HiveAR Design Decision 1](HIVE-0001-entity-data-model-person-business-and-entity-relationships.md), so that a debtor and a third party contacted to locate the debtor can have different windows.
>
> **Whose time**: the window is evaluated in the party's own zone, as Wax Design Decision 12 requires for permitted contact times. The Locale Module for the party's country returns the zones the party can be in, from an address or a phone number, as [United States Module Design Decision 2](../modules/united-states/MOD-US-0002-country-layer.md) does for the United States. For a debtor, the candidates are the zones that the Locale Module returns for every location in the debtor's scope under [HiveAR Design Decision 13](HIVE-0013-compliance-coverage-for-collections.md): until a location is verified, every address on file and every presumption, such as a phone's area code, and once a location is verified, that location alone. A contact is permitted only when the moment falls inside the window in every candidate zone, so a debtor who may be in New York or California can be contacted only in the hours that both permit, and every jurisdiction in scope adds its Compliance Packs to those that govern the debt.
>
> **Exceptions**: a rule can name the exceptions its jurisdiction allows, such as a party's recorded consent to be contacted at another time, and the check honors an exception only when its evidence is on record. Consent is on record as a grant under the contact permission below.

## The Contact Frequency Counter

> **CONTACT FREQUENCY**
>
> **What a limit rule says**: how many contacts of a given unit are allowed within a period, over a given scope. The unit is an attempt, a conversation with the party, or a message sent. The period is a rolling number of days, a calendar day, or a calendar week. The scope is one debt, a debt group at any level of [HiveAR Design Decision 4](HIVE-0004-debt-groups.md), the party across the debts of one client, or the party across the agency. Like a window rule, a limit rule can count only contacts made a given way or to a given kind of contact point, such as calls in a recorded voice to a landline.
>
> **Quiet periods**: a rule can also require a pause after an event, such as no further call for a number of days after a conversation with the party.
>
> **Exclusions**: a rule can leave kinds of contact out of a count, such as an attempt that never connected or a contact the party started.
>
> **Counts**: counts are kept from the communication events of [Wax Design Decision 1](../wax/WAX-0001-enriched-event-sourcing.md) and maintained as contacts happen by the event-driven path, not computed at the moment of the check, in the same way that entity aggregate fields are maintained under HiveAR Design Decision 1.

## The Contact Permission

The third check answers a different question from the other two: not when or how often a party may be contacted, but whether the party may be contacted through this channel at this contact point at all.

> **CONTACT PERMISSION**
>
> **What a permission says**: whether a party may be contacted through a channel, or through every channel, at a contact point. The contact point is either one value in the party's contact history under [HiveAR Design Decision 3](HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md), such as a phone number or an email address, or a kind of contact point that the history records, such as the party's home phone, work phone, or cell phone, so that a permission by kind also reaches a contact point learned later. A permission is either a grant, which permits the channel, or a refusal, which blocks it, such as a request not to be called at work, to receive everything in writing, or to stop all contact.
>
> **Its own windows**: a permission can carry windows of its own, by day of the week or kind of day and by hours, evaluated in the party's own zone as a window rule is, such as no calls to the home phone on Saturdays or no text messages after 7:00 p.m. A grant permits its channel only inside its windows, and a refusal blocks its channel only inside its windows. A grant never widens a window rule, except where the window rule names the party's consent as its exception.
>
> **Where it comes from**: a permission is obtained directly from the party, such as consent or a refusal given on a call or in writing to the agency, or inherited from the client's agreement with the party, such as the terms under which the party gave the client a cell phone number. Either way it records its source and its evidence: who recorded it, when, how it was given, and the recording or the document that shows it.
>
> **How long it lasts**: a permission can be time-boxed with a start and an end, and it can be revoked, as when a party withdraws consent or lifts a refusal. A revocation is recorded with its evidence in the same way, and every grant, refusal, change, and revocation is an event under [Wax Design Decision 1](../wax/WAX-0001-enriched-event-sourcing.md), so that the permission in force at any past moment can be shown.
>
> **Which debts it reaches**: a grant reaches only the debts it was given for. An inherited grant reaches the debts of the client whose agreement holds it, and a grant obtained directly reaches the debts the party gave it about, unless the party gave it more widely. A refusal reaches every debt of the party at the agency, unless the party limited it. Narrow grants and wide refusals are the cautious defaults, and a Compliance Pack can set a different reach where its jurisdiction's law does.
>
> **What a Compliance Pack says**: for every outbound channel, whether its jurisdiction requires permission before the channel is used, and how permission for that channel is obtained, revoked, tracked, and inherited, such as which sources count, what evidence each needs, how a revocation may be given and how soon it takes effect, and whether a grant inherited from a client's agreement counts. A setting can differ by how the contact is made and by the kind of contact point, as a window rule can, and it can say how long a grant stays good before it must be renewed or checked, such as against a register of reassigned telephone numbers. A Compliance Pack that configures this mechanism states its setting for every outbound channel, and the platform shows a pack that leaves a channel out as incomplete.
>
> **The cautious default**: where a governing pack leaves a channel out, the channel needs permission, so a contact through it proceeds only on a grant on record. The default follows the default test of [Wax Design Decision 8](../wax/WAX-0008-extensibility-construct-nomenclature.md), states no law, and keeps a gap in a pack from turning into permission.

The permission check passes when no refusal on record blocks the contact and, where any governing pack or the agency's own rules require permission for the channel, a grant on record permits it. The agency's own rules can only narrow here too: an agency can require permission for a channel that its packs do not, or record a refusal that a client's contract calls for, but it cannot waive a requirement that a pack states. A rule that turns on the party's consent, such as a window's exception or a counter's exclusion, is satisfied only by a grant on record.

## Which Rules Apply

The rules that apply to a contact are those of every Compliance Pack that governs the debt, such as the federal pack and the pack for the state in which the debtor lives, together with the agency's own rules. A contact is permitted only when all of them permit it, so the strictest window and the lowest limit govern, and no pack has to know about another. Which packs govern a debt, and how a federal pack and a state pack combine when they define the same thing differently, remain open questions, but windows and limits need no further choice under this rule.

An agency can add its own rules in the same shapes, for a client's contract or for its own policy, and they can only narrow what is permitted. A Compliance Pack's values are the agency's to edit once installed, as Wax Design Decision 11 describes, so the platform will show wherever an agency's value is looser than the value its pack published, and every change to a value is versioned under [Wax Design Decision 21](../wax/WAX-0021-configuration-management-and-environment-lifecycle.md).

## The Answer and Its Evidence

The check answers permitted or not permitted. When the answer is not permitted, it names the rule or the permission that blocked the contact and the next moment at which the contact would be permitted, or that no such moment is known, as when a refusal or a missing grant blocks the channel, so that a dialer, a queue, or a collector's screen can move on, and the Pending Event Register of [Wax Design Decision 27](../wax/WAX-0027-pending-event-register.md) can schedule a retry. The check that precedes a contact is recorded with the contact's communication event: the zones considered, the rules and their versions, the counts at the time, the permissions it relied on, and the answer. A contact the check refused is recorded as refused, and a contact made on an override is recorded with the override. An agency can then show, for any contact, which rules and permissions applied and what they said.

## Where the Check Runs

Every path that makes an outbound contact runs the check first: a collector's screen before a manual call or message, the work queues and dialer campaigns of [HiveAR Design Decision 3](HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md) when they choose whom to contact, and the dialer, texting, and email integrations when they send. A Vendor Integration Module that makes contact calls the check and keeps no copy of the rules or the permissions. A contact the party starts, such as an inbound call, is not checked, although a rule can count it. When the check blocks a contact, the ways past it are an exception that the rule itself allows, with its evidence on record, and an override where the agency allows overrides.

## Overrides

Whether a blocked contact can be overridden in the moment is an agency setting, and the core default is that it cannot. In an agency that allows overrides, settings at the user and group level, granted through the access control of [Wax Design Decision 18](../wax/WAX-0018-access-control.md), define which users may perform them, and such a user can make a contact that the check blocked, whether the block came from a window, a limit, or a permission. A rule cannot foresee every instruction a party gives, such as no calls on Saturdays except about a failed payment, and an override leaves such a case to a person's judgment. Each override covers one contact, is made by a person and never by an automated path such as a dialer campaign, and is recorded with the contact together with who made it, when, why, and the block it overrode, so that every override can be reviewed. An override reaches only the checks of this decision and never a hold that another decision places on a debt, such as the hold of [HiveAR Design Decision 13](HIVE-0013-compliance-coverage-for-collections.md) on a debt whose jurisdiction is not covered.

## Scope and What Branches Off

This decision defines the mechanisms and states no jurisdiction's values. The restrictions that a party places on contact, such as a request to stop, to use only one channel, or not to be contacted at work, are refusals under the contact permission. It does not define the communications module, whose channels and integrations remain on the module roadmap.

## Implementation Phasing

**HiveAR v1 (MVP):** The window check, the frequency counter with quiet periods and exclusions, and the permission check, for calls, text messages, and email, with the evidence recorded with each contact and the next permitted moment returned. Grants and refusals by channel and by contact point or kind, with their own windows, start and end dates, revocation, and evidence, whether obtained directly or inherited from the client's agreement when the debt is placed. Each governing pack's permission setting for each channel, with the cautious default where a pack leaves one out. The agency's override setting, off by default, the user and group settings that say who may override, and every override recorded. The collector's screens and the work queues use the check. The United States values come from the federal Compliance Pack.

**HiveAR v2:** The dialer, texting, and email integrations call the check as the communications module arrives. Visits, exceptions backed by recorded consent, the warning where an agency's value is looser than its pack's, the display of a pack that leaves a channel out, and the pack rules for how permission is obtained, revoked, tracked, and inherited beyond each channel's setting.

**HiveAR v3+:** Further units, periods, and scopes as jurisdictions require them.

**Breaking change risk: LOW. The check reads events that already exist and adds a projection of counts, the permissions, and a recorded answer. The part to get right from the start is the evidence recorded with each contact, each permission, and each override, because an agency's proof depends on it and it cannot be added to past contacts later.**

## Implications For Contributors

No code names an hour, a count, a period, or a channel's need for permission. Values come only from Compliance Packs and the agency's own rules, and the core's only default is that a channel that a governing pack leaves out needs permission.

Every outbound contact path calls the check, vendor integrations included, and none keeps its own copy of the rules or the permissions.

A rule never works out a party's zone on its own. It asks the Locale Module for the candidate zones and applies the choice its Compliance Pack makes.

A Compliance Pack that configures this mechanism states its permission setting for every outbound channel.

A permission records its source and its evidence, and a revocation is recorded the same way, so that no permission's history is lost.

A blocked contact is overridden only where the agency's setting allows it, by a user whom the user and group settings allow, one contact at a time, and every override is recorded with who made it, when, and why. Otherwise the way past a rule is an exception that the rule allows, with its evidence on record.

The evidence of each check is recorded with the contact, or with the refusal, so that the answer can be shown later.
