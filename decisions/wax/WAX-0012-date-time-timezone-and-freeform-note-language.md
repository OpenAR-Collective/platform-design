---
id: WAX-0012
title: "Date, Time, Timezone, and Freeform Note Language"
status: Accepted
version: 2.0
area: wax
date: 2026-10-05
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 12: Date, Time, Timezone, and Freeform Note Language

## Decision

All instants, meaning values that name a moment in time, will be stored in UTC, and display to users will be rendered in each user's configured timezone. Calendar dates that name a day rather than a moment, such as a due date, a date of birth, a date of death, or a filing date, will be stored as civil dates with no zone and will not be converted for display. Deriving a civil date from an instant, or comparing the two, will always name a zone of reference supplied by the organization, the party, or the rule concerned, never by the viewer. Freeform notes will carry a language code indicating the language in which they were written, preserving the original text as the authoritative record. A translation module architecture will support just-in-time rendering of notes in a reader's preferred language. AI-only translation as a substitute for the i18n architecture is explicitly rejected.

## Date and Time Storage: UTC Throughout

Every timestamp in the system, in core.event, in authoritative state tables, in read models, and in module-owned tables, will be stored in UTC. No timezone-local values will be stored in the database. Timezone conversion is a display concern, not a storage concern.

When a timestamp is displayed to a user, the application will convert it from UTC to the user's configured timezone at render time. A collector in Manila and a supervisor in Dallas looking at the same account record will each see timestamps in their local time. The database record is unambiguous regardless of where the reader is located.

This eliminates a category of operational error that affects multi-location agencies: ambiguous timestamps where it is unclear which timezone a value represents, incorrect ordering of events when records from different timezones are compared, and daylight saving time boundary errors when local times are stored directly.

> **TIMEZONE HANDLING RULES**
>
> All timestamp columns in all tables are stored in UTC. Columns must use a timezone-aware data type (PostgreSQL timestamptz). No application code may write a timezone-local value to the database. All writes convert to UTC before persistence. User timezone is stored as a named IANA timezone string (e.g., America/Chicago, Asia/Manila) in the user profile, not as a UTC offset. Named timezones handle daylight saving transitions correctly; static offsets do not. The frontend is responsible for timezone display conversion. The API delivers UTC timestamps. The frontend converts to the user's local timezone for rendering. The event payload fields occurred_at and recorded_at are UTC timestamps and must never be converted before storage.

## Civil Dates

Many facts in collections are calendar dates, not moments: the day a payment was due, the day of the last payment, a date of birth, a date of death, the day a petition was filed, the day a judgment was entered, the day a notice was received. A calendar date names a day as people in a particular place understand it. It has no time of day and no zone. Storing it as a UTC instant invents a time of day and a zone that nobody asserted, and the invented value reads as the wrong day for some viewers: a date of birth stored as midnight UTC displays as the previous day to every viewer west of Greenwich. Civil dates are therefore stored as plain dates, are never converted for display, and read as the same day to every viewer. The timezone handling rules above govern instants. A civil date has no time of day to localize, so those rules do not apply to it.

An instant and a civil date are different kinds of value, and neither stands in for the other. When a rule needs to move between them, for example to decide whether a payment received at a given moment arrived by the end of a due date, it names the zone of reference explicitly. The zone belongs to the thing being evaluated, not to the person looking at it: the organization's business zone for statement cut-offs and scheduled processing, the debtor's zone for permitted contact times, the court's zone for a filing deadline. Zones are named IANA zones, never offsets. Which zone governs a given rule is rule content and belongs in packs.

When an event carries a civil date that the command did not supply, such as the day a payment is considered received, the platform derives the date from occurred_at in the organization's business zone and stores the derived date. The zone is applied once, at write time, and every later comparison is a comparison between dates. A statement run that takes a through date compares dates and never has to ask which midnight was meant.

## The Organization's Business Zone

Every organization carries a business zone, a named IANA zone set during installation. The platform uses it wherever it computes a day boundary on the organization's behalf, including the date derived for an event whose command supplied none and the day on which a scheduled job counts as running. An organization whose staff and debtors span several zones still has one business zone, because its books and statements close on one clock.

## Counting Between Dates

Deadlines and waiting periods are counted, and rules count differently: in calendar days or business days, with or without deemed-receipt days, with different weekend days, and against holiday sets that vary by place and change over time. Wax will provide a calendar, a named set of weekend days and non-working dates versioned by effective date, and a date arithmetic service that takes a start date, an interval, a unit, a calendar, and a zone of reference and returns a due date or a due instant. Rules name the calendar and the counting basis they use, and the framework does not choose them. Calendars themselves, such as a country's holidays, are pack content. The framework defines only their shape and the arithmetic.

## Freeform Note Language Indicators

Account notes, contact notes, and other freeform text fields entered by users will carry a language code indicating the language in which the note was written. The language code is an IETF BCP 47 tag (e.g., en-US, es-MX, tl-PH) and is determined at the time of note creation based on the writing user's active locale.

The original text of a note is the authoritative record. A Spanish-speaking collector's note written in Spanish is stored in Spanish. It is not translated to English for storage, normalized to a common language, or altered in any way. The language code is metadata that enables downstream rendering and translation; it does not change what was written.

A translation module may be developed as an optional Module that provides just-in-time rendering of notes in a reader's preferred language. When a supervisor who reads English opens an account with Spanish notes, the translation module can render an English version inline. The original Spanish record remains unchanged and is always accessible. The translated rendering is clearly marked as a translation and does not replace the source record.

## Why Not AI Translation as the Primary Strategy

There is a tempting architectural shortcut: abandon the i18n table system, store all user-entered text in English by translating at write time, and use AI translation to present a cohesive multilingual experience. This approach is simpler to implement in the short term and has become more viable as large language model quality has improved.

The platform explicitly rejects this approach for the following reasons.

**Authenticity and legal integrity**: In a regulated industry, the authoritative record is what was actually said or recorded, not an AI's interpretation of it. A note written in Spanish by a collector during a consumer call is a contemporaneous record. Storing an AI translation of that note as the primary record introduces a layer of interpretation that does not belong in a compliance-sensitive system. If that record is ever produced in response to a dispute, an audit, or a legal proceeding, the question of whether the stored text accurately represents what was originally communicated becomes a material concern.

**Translation error risk**: AI translation is imperfect. Medical terminology, legal terms, industry-specific jargon, and colloquial expressions translate poorly out of context. A mistranslated note in a collection context could misrepresent a consumer's stated position, a payment arrangement, or a dispute. The risk of a silent mistranslation being treated as an accurate record is not acceptable for a compliance-first platform.

**Availability dependency**: A system that depends on an AI translation service being available at write time introduces a failure mode. If the translation service is unavailable, slow, or returns an error, the write operation either fails or stores unprocessed text. This creates operational fragility that the i18n architecture does not.

**User experience quality**: AI translation of short, context-light notes produces inconsistent results. A well-designed i18n system where UI strings are translated by human translators who understand the application context produces a materially more professional and coherent experience than real-time AI translation of arbitrary user input.

The translation module described above uses AI translation at read time for optional rendering assistance, not at write time as the primary storage strategy. That distinction is deliberate. The original record is always preserved, the translation is always marked as such, and the system never depends on translation availability for a write to succeed.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. Store every instant as UTC and convert to the user's timezone at the presentation layer. Store every civil date as a date, derive a missing civil date once from occurred_at in the organization's business zone, and set the organization's business zone during installation. This is a coding discipline, not a feature.

**Wax v2:** The calendar and the date arithmetic service, which the Pending Event Register and the Job Scheduler depend on.

**Breaking change risk: CATASTROPHIC if deferred.** Timezone bugs in financial data are unfixable retroactively, and a civil date stored as an instant has lost the zone that would let it be repaired.

## Implications For Contributors

All timestamp columns must use PostgreSQL timestamptz. Timestamp columns without timezone awareness are a schema violation.

No module may write timezone-local values to the database. UTC conversion before write is mandatory.

All freeform text fields that accept user input must include a language_code column storing the IETF BCP 47 locale tag of the writing user's active session.

No module may translate user-entered text before storing it. The source text is always the authoritative record.

Translation modules must clearly distinguish translated renderings from original records in the UI. A translated note must never be presented as if it were the original.

A column that holds a day, such as a due date or a date of birth, must be typed date and named with the _date suffix. A column that holds a moment must be typed timestamptz and named with the _at suffix. A civil date stored as a timestamp is a schema violation.

Module authors declare the kind of every date-bearing payload field, instant or civil date, in the field registry, as they already do for PII and reference value fields under [Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md). The serializer rejects a civil date that carries a time part and an instant that carries no zone.

No code converts a civil date for display, or converts between a civil date and an instant, without naming a zone of reference. Code that needs a day boundary on the organization's behalf reads the organization's business zone, not the server's zone and not the current user's.

In C#, a civil date is a DateOnly and an instant is a DateTimeOffset in UTC.
