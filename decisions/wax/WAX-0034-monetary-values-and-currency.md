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

Wax will represent every monetary value as a typed quantity: an exact decimal amount together with an ISO 4217 currency code, carried together everywhere the value appears, in event payloads, authoritative state tables, read models, and user-defined fields. A stored monetary value will never be a bare number: it always names its currency, so it stays complete if the installation's configuration later changes. The installation's default currency is the single currency named by the installed Region Packs when they name exactly one, and the framework applies it automatically wherever a monetary value is created without a currency, so that an installation working in one currency never has to specify a currency in code, on a screen, or in an import layout. When the installed Region Packs name more than one currency there is no default, and a value created without a currency is rejected rather than guessed. OpenAR code and certified modules will always specify the currency in code, taking it from the account, contract, client, or payment concerned, and will never rely on the default, so that adding a currency to an installation cannot break them. Arithmetic on amounts will be exact decimal arithmetic, never binary floating point. An amount in one currency is never added to, compared with, or allocated against an amount in another currency without an explicit conversion, and a conversion is a recorded act that names the rate, the source of the rate, and the date the rate applies to. The list of currencies, each currency's minor-unit scale, and its rounding conventions are reference data supplied by the region and locale layer once per currency. When more than one currency is in play, which currency an account, a ledger, or a client uses, and when conversion happens, are decisions for the layers built on Wax.

## Why This Is a Framework Decision

Money appears in nearly every layer: event payloads, authoritative state tables, read models, user-defined fields, and the general ledger. If each layer chooses its own shape, the platform ends up with bare numbers in some places, a currency column in others, and an installation-wide assumption holding the rest together. That assumption holds only until an installation holds its first account in a second currency, which a cross-border agency, a debt buyer with purchased portfolios, a forwarding network, or an organization outside the United States will do from the first day. One typed shape, defined once, removes the choice.

The timing matters because events are immutable. An event written with a bare amount can be repaired later only by an upcaster under [Wax Design Decision 26](WAX-0026-event-schema-versioning.md) that supplies the installation's currency, and that repair is valid only for installations that were single-currency throughout. Stamping the default currency on every stored value at write time costs a few dozen bytes per amount and no effort from developers or users, and it means that the day an installation adds a second currency, or changes its Region Packs, no stored value changes meaning. Shipping the typed shape in v1 costs nothing while no events exist.

## The Typed Quantity

In an event payload a monetary value is a keyed object with two keys: amount, an exact decimal written as a string in canonical form, and currency, an ISO 4217 alphabetic code. Strings avoid the ambiguity of JSON numbers, and the canonical form is pinned in the hash specification of [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) so that a hash computed in one place verifies in another.

```
{ "current_balance": { "amount": "1500.00", "currency": "USD" } }
```

The currency code is a standardized technical string of the same class as the locale codes that [Wax Design Decision 11](WAX-0011-internationalization-architecture-and-reference-value-system.md) already permits in technical identifiers, and its display name is resolved through i18n. ISO 4217 also assigns funds codes to several indexed units of account that some countries use for debts, such as CLF in Chile and MXV in Mexico, so one code space covers them (needs verification).

In a table, every monetary column is accompanied by the currency that denominates it, either as a paired column that shares the same root and ends in _currency_code, or as the table's single currency_code column where every amount in a row shares one currency by definition. Amount columns use an exact numeric type with the precision the arithmetic requires. In a user-defined table, money is a field type of its own beside the decimal type, and a money field carries its currency.

## The Default Currency

Most installations work in one currency, and for them currency is invisible. When the installed Region Packs name exactly one currency, that currency is the installation's default. A field, import layout, or condition that an agency defines without naming a currency takes the default, and so does an amount that an agency's own code creates without one. The framework resolves the default and stamps the resolved currency onto the value when it is stored. Administrators and users in a single-currency installation never specify a currency, and screens and layouts show no currency selector or column.

The default is applied once, at creation, and is recorded on the value, so a later change to the installed Region Packs cannot change what any stored value means. The rule is stated in terms of currencies and not of packs: an installation with several Region Packs that all use the euro still has a default.

The default exists for agency-authored configuration and for code that an agency writes for itself. It does not exist for OpenAR code or certified modules, which always specify the currency in code, taking it from the account, contract, client, or payment concerned, and never from a literal or from the default. The framework offers one creation path that takes a currency and a separate, plainly named path that applies the default, so reliance on the default is visible in review. The build rules of OpenAR repositories and the certification review of modules reject use of the default path in OpenAR and certified code. The continuous integration described in [Shared Design Decision 7](../shared/SHARED-0007-devops-and-contribution-lifecycle.md), and the certification testing of modules, also run the test suite in a configuration with more than one currency, where no default exists, so any reliance on the default fails. Code outside those programs that relies on the default does so at its author's own risk.

If the installed Region Packs come to name more than one currency, the default no longer exists. A value created without a currency is rejected, and the account, contract, or client that the value belongs to supplies the currency. Adding a second currency is therefore a deliberate administrative step: the administrator is shown every money field and import layout that relied on the default and fixes a currency for each, so nothing begins failing unnoticed.

## Precision, Rounding, and Display

Amounts are carried at the precision the calculation needs and are rounded to a currency's minor unit only where a rule says to, using the rounding convention that rule names. The framework fixes no rounding convention. Formatting for display, including symbol, grouping, and decimal mark, is a presentation concern resolved from the viewer's locale and is never stored.

## Conversion

Converting between currencies is an explicit act, recorded as an event or as part of the posting that needs it. The record names the source amount, the target amount, the rate, the source of the rate, and the date the rate applies to. No component converts implicitly, and no total silently mixes currencies: a sum, comparison, or allocation across currencies fails unless a conversion is supplied. Statutory thresholds in rule content are stated as typed quantities with their own effective dates, so a limit expressed in one currency is never applied to an amount in another without conversion.

## What This Decision Does Not Specify

Which currency an account is denominated in, how a payment in another currency is applied, the functional currency of the ledger and the treatment of exchange gains and losses, the currency of client remittances and statements, and how purchase price is held are HiveAR decisions that build on this one. Currency lists, minor-unit scales, and rounding conventions are content of region and locale packs. Thresholds stated in units other than a currency, such as multiples of a statutory base amount, are rule content that packs resolve to a currency amount as of a date.

## Implementation Phasing

**Wax v1 (MVP):** The typed quantity in event payloads and authoritative tables, the money kind in the field registry, exact decimal arithmetic that rejects mixed currencies, ISO 4217 reference data, and the default currency rule with its two creation paths. Single-currency installations specify no currency anywhere, and the framework stamps the default on every stored value. The multi-currency test configuration is part of the continuous integration baseline from the first release.

**Wax v2:** The conversion record.

**Wax v3+:** Effective-dated rate tables and revaluation support if demand warrants.

**Breaking change risk: MEDIUM if deferred, NONE if shipped in v1.** Events written as bare numbers can be repaired only by an upcaster that assumes a single currency.

## Implications For Contributors

No payload schema, column, or user-defined field may hold a monetary value as a bare number. The module contract validator rejects a monetary field that is not declared with the money kind in the field registry, in the same way it rejects an unclassified PII field.

OpenAR code and certified modules always specify the currency in code. They take it from the account, contract, client, or payment concerned, never from a literal and never from the installation's default, so adding a currency to an installation cannot break them. The creation path that applies the default is named so that its use is visible, and the build rules of OpenAR repositories and the certification review of modules reject its use in OpenAR and certified code.

Continuous integration for OpenAR repositories, and certification testing for modules, runs the test suite in a configuration with more than one currency. No default exists in that configuration, so any reliance on the default fails.

No code adds, compares, or allocates amounts of different currencies without an explicit conversion. A sum over a set of amounts checks that the set is single-currency or fails.

Examples in documentation name the currency instead of using an unlabeled symbol.

Floating-point types are never used for amounts.
