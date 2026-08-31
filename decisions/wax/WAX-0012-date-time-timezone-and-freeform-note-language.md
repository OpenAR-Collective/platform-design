---
id: WAX-0012
title: "Date, Time, Timezone, and Freeform Note Language"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 12: Date, Time, Timezone, and Freeform Note Language

## Decision

All date and time values will be stored in UTC. Display to users will be rendered in each user's configured timezone. Freeform notes will carry a language code indicating the language in which they were written, preserving the original text as the authoritative record. A translation module architecture will support just-in-time rendering of notes in a reader's preferred language. AI-only translation as a substitute for the i18n architecture is explicitly rejected.

## Date and Time Storage: UTC Throughout

Every timestamp in the system, in core.event, in authoritative state tables, in read models, and in module-owned tables, will be stored in UTC. No timezone-local values will be stored in the database. Timezone conversion is a display concern, not a storage concern.

When a timestamp is displayed to a user, the application will convert it from UTC to the user's configured timezone at render time. A collector in Manila and a supervisor in Dallas looking at the same account record will each see timestamps in their local time. The database record is unambiguous regardless of where the reader is located.

This eliminates a category of operational error that affects multi-location agencies: ambiguous timestamps where it is unclear which timezone a value represents, incorrect ordering of events when records from different timezones are compared, and daylight saving time boundary errors when local times are stored directly.

> **TIMEZONE HANDLING RULES**
>
> All timestamp columns in all tables are stored in UTC. Columns must use a timezone-aware data type (PostgreSQL timestamptz). No application code may write a timezone-local value to the database. All writes convert to UTC before persistence. User timezone is stored as a named IANA timezone string (e.g., America/Chicago, Asia/Manila) in the user profile, not as a UTC offset. Named timezones handle daylight saving transitions correctly; static offsets do not. The frontend is responsible for timezone display conversion. The API delivers UTC timestamps. The frontend converts to the user's local timezone for rendering. The event payload fields occurred_at and recorded_at are UTC timestamps and must never be converted before storage.

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

**Wax v1 (MVP):** Full implementation. Store all timestamps as UTC. Convert to user timezone at the presentation layer. This is a coding discipline, not a feature.

**Breaking change risk: CATASTROPHIC if deferred.** Timezone bugs in financial data are unfixable retroactively.

## Implications For Contributors

All timestamp columns must use PostgreSQL timestamptz. Timestamp columns without timezone awareness are a schema violation.

No module may write timezone-local values to the database. UTC conversion before write is mandatory.

All freeform text fields that accept user input must include a language_code column storing the IETF BCP 47 locale tag of the writing user's active session.

No module may translate user-entered text before storing it. The source text is always the authoritative record.

Translation modules must clearly distinguish translated renderings from original records in the UI. A translated note must never be presented as if it were the original.
