---
id: WAX-0034
title: "Monetary Values and Currency"
status: Proposed
version: 0.1
area: wax
date: 2026-10-05
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 34: Monetary Values and Currency

## Decision

Wax will represent every monetary value as a typed quantity: an exact decimal amount together with an ISO 4217 currency code, carried together everywhere the value appears, in event payloads, authoritative state tables, read models, and user-defined fields. In an event payload the amount is a string in a canonical form that follows the currency's standard representation: it carries the fewest fraction digits that represent the value exactly and never fewer than the currency's standard number of fraction digits, so that each value has exactly one string. A stored monetary value will never be a bare number: it always names its currency, so it stays complete if the installation's configuration later changes. The installation's default currency is the single currency named by the installed Region Packs when they name exactly one, and the framework applies it automatically wherever a monetary value is created without a currency, so that an installation working in one currency never has to specify a currency in code, on a screen, or in an import layout. When the installed Region Packs name more than one currency there is no default, and a value created without a currency is rejected rather than guessed. OpenAR code and certified modules will always specify the currency in code, taking it from the account, contract, client, or payment concerned, and will never rely on the default, so that adding a currency to an installation cannot break them. Arithmetic on amounts will be exact decimal arithmetic, never binary floating point. An amount in one currency is never added to, compared with, or allocated against an amount in another currency without an explicit conversion, and a conversion is a recorded act that names the rate, the source of the rate, and the date the rate applies to. A currency can be used for money only when an installed Region Pack supplies it, so an installation that has not loaded the Region Pack for a currency cannot hold money in that currency. The Region Pack supplies the currency's code, its minor-unit scale, and its rounding conventions once per currency. Deactivating a Region Pack stops new money in its currencies, and removing a pack keeps the definition of any currency that a stored value names, so every stored value stays readable and verifiable. When more than one currency is in play, which currency an account, a ledger, or a client uses, and when conversion happens, are decisions for the layers built on Wax.

## Why This Is a Framework Decision

Money appears in nearly every layer: event payloads, authoritative state tables, read models, user-defined fields, and the general ledger. If each layer chooses its own shape, the platform ends up with bare numbers in some places, a currency column in others, and an installation-wide assumption holding the rest together. That assumption holds only until an installation holds its first account in a second currency, which a cross-border agency, a debt buyer with purchased portfolios, a forwarding network, or an organization outside the United States will do from the first day. One typed shape, defined once, removes the choice.

The timing matters because events are immutable. An event written with a bare amount can be repaired later only by an upcaster under [Wax Design Decision 26](WAX-0026-event-schema-versioning.md) that supplies the installation's currency, and that repair is valid only for installations that were single-currency throughout. Stamping the default currency on every stored value at write time costs a few dozen bytes per amount and no effort from developers or users, and it means that the day an installation adds a second currency, or changes its Region Packs, no stored value changes meaning. Shipping the typed shape in v1 costs nothing while no events exist.

## The Typed Quantity

In an event payload a monetary value is a keyed object with two keys: amount, an exact decimal written as a string in canonical form, and currency, an ISO 4217 alphabetic code. Strings avoid the ambiguity of JSON numbers, and the canonical form, described below, is pinned in the hash specification of [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) so that a hash computed in one place verifies in another.

```
{ "current_balance": { "amount": "1500.00", "currency": "USD" } }
```

The canonical form of an amount follows the currency's standard representation. The string uses a period as the decimal mark, has no grouping, no plus sign, and no exponent, and begins with a minus sign when the value is negative. It carries the fewest fraction digits that represent the value exactly, and never fewer than the currency's standard number of fraction digits, which is the minor-unit exponent that ISO 4217 lists for the currency and that the installed Region Packs supply. That number is the floor. A value with no more digits than the floor is padded up to it, so 1500 US dollars is "1500.00", 1500 Japanese yen is "1500", and 1.2 Kuwaiti dinars is "1.200". A value that genuinely has more digits than the floor keeps them and loses only the trailing zeros beyond the floor, so 0.0123 US dollars is "0.0123" and 0.0120 US dollars is "0.012". Zero is written with the floor's digits, as "0.00" for US dollars, and is never written with a minus sign. Every value in a currency therefore has exactly one string.

The framework's money type writes the canonical string, because it knows the currency's digits, and the hash covers the string exactly as written. A later change to a currency's standard digits therefore cannot alter an event already stored, and verifying a hash never requires deriving the form again. A database cast of a numeric amount to text is not the canonical form, because the text follows the stored scale of the column.

The currency code is a standardized technical string of the same class as the locale codes that [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) already permits in technical identifiers, and its display name is resolved through i18n. ISO 4217 also assigns funds codes to several indexed units of account that some countries use for debts, such as CLF in Chile and MXV in Mexico, so one code space covers them (needs verification).

A monetary value may name only a currency that an installed Region Pack supplies. The framework rejects a value that names any other currency, so an installation that has not loaded the Region Pack for a currency cannot hold money in it, whatever ISO 4217 lists. ISO 4217 gives the codes their standard form, and the Region Packs decide which of them exist in an installation. No module, and no Pack other than a Region Pack, supplies a currency.

In a table, every monetary column is accompanied by the currency that denominates it, either as a paired column that shares the same root and ends in _currency_code, or as the table's single currency_code column where every amount in a row shares one currency by definition. Amount columns use an exact numeric type with the precision the arithmetic requires. In a user-defined table, money is a field type of its own beside the decimal type, and a money field carries its currency.

## The Default Currency

Most installations work in one currency, and for them currency is invisible. When the installed Region Packs name exactly one currency, that currency is the installation's default. A field, import layout, or condition that an agency defines without naming a currency takes the default, and so does an amount that an agency's own code creates without one. The framework resolves the default and stamps the resolved currency onto the value when it is stored. Administrators and users in a single-currency installation never specify a currency, and screens and layouts show no currency selector or column.

The default is applied once, at creation, and is recorded on the value, so a later change to the installed Region Packs cannot change what any stored value means. The rule is stated in terms of currencies and not of packs: an installation with several Region Packs that all use the euro still has a default.

The default exists for agency-authored configuration and for code that an agency writes for itself. It does not exist for OpenAR code or certified modules, which always specify the currency in code, taking it from the account, contract, client, or payment concerned, and never from a literal or from the default. The framework offers one creation path that takes a currency and a separate, plainly named path that applies the default, so reliance on the default is visible in review. The build rules of OpenAR repositories and the certification review of modules reject use of the default path in OpenAR and certified code. The continuous integration described in [Shared Design Decision 7](../shared/SHARED-0007-devops-and-contribution-lifecycle.md), and the certification testing of modules, also run the test suite in a configuration with more than one currency, where no default exists, so any reliance on the default fails. Code outside those programs that relies on the default does so at its author's own risk.

If the installed Region Packs come to name more than one currency, the default no longer exists. A value created without a currency is rejected, and the account, contract, or client that the value belongs to supplies the currency. Adding a second currency is therefore a deliberate administrative step: the administrator is shown every money field and import layout that relied on the default and fixes a currency for each, so nothing begins failing unnoticed.

## Deactivating and Removing a Region Pack

An administrator can deactivate a Region Pack. Deactivation is the soft deletion that [Wax Design Decision 10](WAX-0010-module-registry.md) and [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) define, applied to the pack: its currencies are set inactive, the framework rejects any new value that names one, and the features that depend on the pack stop working. Nothing is dropped and nothing stored changes. Every stored value keeps its meaning, because each one names its currency and the pack's currency data stays readable for display, for the canonical string, and for verification. A deactivated pack no longer counts toward the currencies that the installed Region Packs name, so deactivating one of two packs can restore a default for values created from then on, and reactivating a pack is the same deliberate administrative step as loading one. Deactivation stops all new money in the currency, including payments against balances already held, so it is the way to retire a currency and not a way to pause one.

Removing a Region Pack whose currency a stored value names cannot be a full uninstall. It works the way uninstalling a program does when settings and drivers are left behind: the framework removes what nothing stored depends on, and it keeps the definition of every currency that a stored value still names, inactive and read-only, so that each stored value stays readable and verifiable. Events are never deleted, so a currency that any event names is kept for as long as the installation exists. A retained currency cannot be used for new money, and loading its Region Pack again makes it usable again. This is the one case in which a pack leaves part of itself behind, where Wax Design Decision 10 and Wax Design Decision 11 otherwise treat a partial uninstall as invalid, and those decisions will carry the mechanics when this decision is adopted.

## Precision, Rounding, and Display

Amounts are carried at the precision the calculation needs and are rounded to a currency's minor unit only where a rule says to, using the rounding convention that rule names. The framework fixes no rounding convention. A settled amount, such as one posted to a ledger or applied as a payment, is a whole number of the currency's minor units and so has exactly the floor's digits. The layers built on Wax say where a computed amount becomes a settled one, and the rule that rounds it names its convention. Formatting for display, including symbol, grouping, and decimal mark, is a presentation concern resolved from the viewer's locale and is never stored.

A database shows a stored amount at the scale of its column and not at the currency's digits. A column with a declared scale of four shows 1500 US dollars as 1500.0000, and a column with no declared scale shows whatever scale the writer supplied, which arithmetic can change. Application screens are unaffected, because under [Shared Design Decision 5](../shared/SHARED-0005-frontend-internationalization.md) the frontend never formats money itself and receives formatted values from the API or renders them with the browser's Intl API, which takes a currency's default digits from ISO 4217. The generated SQL views that reporting tools and direct SQL clients read need the same care. The view generator described in [Wax Design Decision 16](WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md) will emit, beside each money pair, a display column that rounds the amount to the currency's standard digits and writes it as text, as in "1500.00", and the exact amount stays in its own column for calculation. The display column rounds for display only and stores nothing. A value finer than the currency's digits, such as an accrued 0.0123 US dollars, appears rounded in the display column, so a screen that must show the extra digits asks for the exact amount. Symbol, grouping, and decimal mark depend on the locale and remain the business of the interface or the reporting tool. The mechanics belong to Wax Design Decision 16, which will carry them when this decision is adopted.

## Conversion

Converting between currencies is an explicit act, recorded as an event or as part of the posting that needs it. The record names the source amount, the target amount, the rate, the source of the rate, and the date the rate applies to. No component converts implicitly, and no total silently mixes currencies: a sum, comparison, or allocation across currencies fails unless a conversion is supplied. Statutory thresholds in rule content are stated as typed quantities with their own effective dates, so a limit expressed in one currency is never applied to an amount in another without conversion.

## What This Decision Does Not Specify

Which currency an account is denominated in, how a payment in another currency is applied, the functional currency of the ledger and the treatment of exchange gains and losses, the currency of client remittances and statements, and how purchase price is held are HiveAR decisions that build on this one. Currency lists, minor-unit scales, and rounding conventions are content of region and locale packs. Thresholds stated in units other than a currency, such as multiples of a statutory base amount, are rule content that packs resolve to a currency amount as of a date.

## Implementation Phasing

**Wax v1 (MVP):** The typed quantity in event payloads and authoritative tables, its canonical string form, the money kind in the field registry, exact decimal arithmetic that rejects mixed currencies, the currency reference data that Region Packs supply, and the default currency rule with its two creation paths. Single-currency installations specify no currency anywhere, and the framework stamps the default on every stored value. The multi-currency test configuration is part of the continuous integration baseline from the first release. The display columns of generated views ship with those views, in the release in which Wax Design Decision 16 phases them.

**Wax v2:** The conversion record, and the deactivation and removal of Region Packs, which arrive with the Pack installation pipeline of [Wax Design Decision 8](WAX-0008-extensibility-construct-nomenclature.md).

**Wax v3+:** Effective-dated rate tables and revaluation support if demand warrants.

**Breaking change risk: MEDIUM if deferred, NONE if shipped in v1.** Events written as bare numbers can be repaired only by an upcaster that assumes a single currency.

## Implications For Contributors

No payload schema, column, or user-defined field may hold a monetary value as a bare number. The module contract validator rejects a monetary field that is not declared with the money kind in the field registry, in the same way it rejects an unclassified PII field.

OpenAR code and certified modules always specify the currency in code. They take it from the account, contract, client, or payment concerned, never from a literal and never from the installation's default, so adding a currency to an installation cannot break them. The creation path that applies the default is named so that its use is visible, and the build rules of OpenAR repositories and the certification review of modules reject its use in OpenAR and certified code.

Continuous integration for OpenAR repositories, and certification testing for modules, runs the test suite in a configuration with more than one currency. No default exists in that configuration, so any reliance on the default fails.

No code adds, compares, or allocates amounts of different currencies without an explicit conversion. A sum over a set of amounts checks that the set is single-currency or fails.

Examples in documentation name the currency instead of using an unlabeled symbol.

Floating-point types are never used for amounts.

A currency is available only when an installed Region Pack supplies it. Code and configuration that name a currency the installation has not loaded are rejected, and no module defines a currency of its own. Code that reads, formats, or verifies an existing value works from the retained currency definition and does not assume that the Region Pack is active, because a pack can be deactivated or removed without changing any stored value.

Event payloads carry amounts in the canonical string form, written by the framework's money type. Code never builds the string by hand or by casting a number to text.

Rounding for display happens in the display column of a generated view or in the interface, and a module does not round a stored amount to make it look right.
