---
id: MOD-US-0002
title: "Country Layer: Locale Module, Region Pack, and Language Packs"
status: Proposed
version: 0.1
area: module:united-states
date: 2026-10-11
supersedes: none
license: CC-BY-4.0
---

# United States Module Design Decision 2: Country Layer

## Decision

The United States layer will ship one country layer that carries the country's structure, formats, and translations and no compliance content: the US Locale Module, the Region Pack region.us, and the US Language Packs. The Locale Module will own the US tables for names, identity numbers, and addresses with their validation, will validate and format US phone numbers, and will resolve a party's time zones from an address or a phone number. The Region Pack will supply the dollar, the US display formats, the US time zones, and the federal holiday calendar. The Language Packs will supply US English and, later, US Spanish. Every state uses this one layer, because states differ in law and procedure and not in structure, so what a state requires goes to its Compliance Pack or to a module's Boilerplate Pack for that state.

## Where This Decision Sits

[Wax Design Decision 8](../../wax/WAX-0008-extensibility-construct-nomenclature.md) defines the constructs and the tests that place content, and it sketches the US Locale Module. Several decisions already assign US structure to that module: [HiveAR Design Decision 1](../../hivear/HIVE-0001-entity-data-model-person-business-and-entity-relationships.md) names its name and identity tables, [HiveAR Design Decision 2](../../hivear/HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md) has it declare the fields used for matching, and [HiveAR Design Decision 3](../../hivear/HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md) gives the US address fields and the US completeness rules. This decision gathers them in one place and adds what was missing, such as phone numbers, time zone resolution, and the contents of region.us. An agency installs the country layer through the US Bundle, together with the federal Compliance Pack compliance.us, a Compliance Pack for each state in which it collects, and the US Boilerplate Pack.

## The US Locale Module

The module is identified as oar.core.us_locale, has the module type locale, and owns the us_locale schema under [Wax Design Decision 4](../../wax/WAX-0004-schema-architecture-and-module-extension-pattern.md).

> **US LOCALE MODULE CONTENTS**
>
> **Names**: the us_name_components table with given_name, middle_name, family_name, and suffix. A US name is complete with a given name and a family name, and a middle name and suffix are optional. The module's read model projection builds display_name from the given name, middle name, family name, and suffix, in that order.
>
> **Identity numbers**: the us_identity table with a person's Social Security number, a business's employer identification number, and, as proposed here, an individual taxpayer identification number for a person who has one in place of a Social Security number. Each has a format check. The Social Security number and the individual taxpayer identification number are designated for column-level encryption under [Wax Design Decision 14](../../wax/WAX-0014-encryption-and-data-protection.md).
>
> **Addresses**: the us_address table with addr1, addr2, city, state_code, postal_code, and county. The state_code takes the USPS two-letter codes for the fifty states, the District of Columbia, the territories, and the armed forces post offices, AA, AE, and AP. The postal_code takes a five-digit ZIP Code or a ZIP+4 code. The county holds a county or its equivalent, such as a Louisiana parish or an Alaska borough. A US address is complete with addr1, city, state_code, and postal_code. The module validates the state code and the postal code and registers the USPS CASS address standardization action type for the workflow engine.
>
> **Phone numbers**: US numbers in the North American Numbering Plan. They are stored in the core phone history in E.164 form, as +1 followed by ten digits, and displayed in the familiar form (312) 555-0100. The module checks that the area code and the exchange are well formed.
>
> **Matching fields**: the entity matching field registry that HiveAR Design Decision 2 asks of each Locale Module, which offers the taxpayer numbers, the name components, and the address, alongside core fields such as the date of birth, with starting weights that the agency tunes.
>
> **Time zone resolution**: given a US address or a US phone number, the module returns the IANA zone or zones it can lie in. It resolves an address by its state, and by its ZIP Code where the state spans more than one zone or keeps different rules within it, as in Arizona, where most of the state keeps standard time all year. It resolves a phone number by its area code, and an area code that covers more than one zone returns each of them. This is how a rule finds the debtor's zone, which [Wax Design Decision 12](../../wax/WAX-0012-date-time-timezone-and-freeform-note-language.md) says governs permitted contact times. Which candidate a rule must honor, when the address and the phone point to different zones, is compliance and belongs to compliance.us.

## The Region Pack region.us

The pack is identified as region.us and is data only.

> **REGION.US CONTENTS**
>
> **Currency**: the US dollar, USD, with two minor digits, as [Wax Design Decision 34](../../wax/WAX-0034-monetary-values-and-currency.md) has a Region Pack supply. The pack supplies half away from zero, the usual commercial rounding, as the dollar's rounding convention, which the pro-rata shares of [HiveAR Design Decision 7](../../hivear/HIVE-0007-payment-application-and-waterfall.md) use, and it also names half to even for a rule that asks for it.
>
> **Display formats**: dates as month, day, and year, as in 03/30/2026, numbers with a comma between thousands and a period before decimals, and the dollar sign before an amount. These are display forms only, and stored forms follow Wax Design Decisions 12 and 34.
>
> **Time zones**: the IANA zones of the states and territories, such as America/New_York, America/Chicago, America/Denver, America/Phoenix, America/Los_Angeles, America/Anchorage, Pacific/Honolulu, and America/Puerto_Rico.
>
> **Federal holiday calendar**: a calendar in the shape that Wax Design Decision 12 defines, with Saturday and Sunday as weekend days and the federal holidays as non-working dates, versioned by effective date, for rules that count business days to name. A court's own holidays belong to the legal module's Boilerplate Pack for that state.
>
> **Locale defaults**: US English as the default language. The organization's business zone is set at installation under Wax Design Decision 12 and does not come from the pack.

## The Language Packs

US English, language.en_us, is the Language Pack that a US installation starts with. US Spanish, language.es_us, is the first additional Language Pack that [Wax Design Decision 11](../../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md) plans. Both translate labels only and carry no compliance content.

## What the Country Layer Leaves to Other Packs

The country layer stops where compliance and procedure begin. A rule about when a Social Security number may be shown, which zone a contact rule honors, when and how often a debtor may be contacted, or what a notice must say belongs to compliance.us or to a state's Compliance Pack. A state's court case flow belongs to the legal module's Boilerplate Pack for that state. Starting statuses, roles, workflows, and letters belong to the US Boilerplate Pack. External data services, such as a national change of address service or skip tracing, are Vendor Integration Modules.

## Implementation Phasing

**HiveAR v1 (MVP):** The Locale Module's name, identity number, and address tables with their validation and completeness rules, US phone validation and display, the matching field registry, and time zone resolution. The Region Pack with the dollar, the display formats, the zones, and the federal holiday calendar. US English.

**HiveAR v2:** The USPS CASS address standardization action type and US Spanish.

**HiveAR v3+:** Further identity number types or address forms if practice shows a need for them.

**Breaking change risk: LOW. The layer adds tables in its own schema and data in its own packs and changes nothing in the core.**

**Confidence: HIGH. The structures described here are long settled. Three proposals are less settled and are flagged for review: the individual taxpayer identification number, half away from zero as the dollar's rounding convention, and resolving a zone from an area code.**

## Implications For Contributors

Nothing in the country layer encodes a compliance rule. A rule about when a Social Security number may be shown, which zone a contact rule honors, or what a notice says belongs to compliance.us or to a state's Compliance Pack.

US fields live only in the us_locale schema. No US column is ever added to a core table, as Wax Design Decision 8 requires.

A state never gets its own Locale Module or Region Pack. Its differences go to its Compliance Pack or to a module's Boilerplate Pack for that state.

A rule never infers a debtor's zone on its own. It asks the Locale Module for the candidate zones and applies the choice that its Compliance Pack makes.
