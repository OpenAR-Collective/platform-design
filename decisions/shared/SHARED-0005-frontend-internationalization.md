---
id: SHARED-0005
title: "Frontend Internationalization"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 5: Frontend Internationalization

## Decision

The HiveAR frontend will implement internationalization at two distinct layers: the data layer, where all user-visible reference values and domain labels are resolved by the backend and delivered locale-aware through the API, and the UI chrome layer, where button labels, field labels, navigation items, error messages, and all other interface strings are sourced from locale-specific resource bundles. Layout directionality will be managed through CSS logical properties and the HTML dir attribute, supporting right-to-left language rendering without a separate codebase. Additional locale-sensitive conventions (text expansion, CJK font fallbacks, number and date formatting) will be addressed through contributor coding standards rather than architectural mechanisms.

## Data Layer: Reference Values and Domain Labels

The frontend never stores or resolves reference value labels. All status codes, reason codes, debt types, and other domain lookup values are stored in the database as UUID surrogate keys ([Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md)). When the API returns an account record, it includes resolved, translated labels for all reference values, already rendered in the session locale through the three-level locale resolution chain. The frontend renders what the API delivers.

This means adding a new language to the platform requires no frontend code changes. Installing a new Language Pack updates the backend translation tables. The existing API endpoints and frontend components automatically serve the new language the next time a user with that locale preference makes a request.

## UI Chrome Layer: Resource Bundles

User interface strings that are not domain data, including button labels, navigation items, page titles, field labels, placeholder text, error messages, validation messages, and help text, will be stored in .NET resource files (.resx) organized by locale. The active locale is resolved at session start using the same three-level fallback chain defined in Wax Design Decision 11: session preference first, system default second, installation default third.

No UI string will be hardcoded in a Blazor component. Every visible string will reference a resource key. This is enforced as a contributor convention and will be validated through code review. A component that contains a hardcoded English string is a localization defect, not a style preference.

## Layout Directionality: RTL Support

Right-to-left languages, including Arabic, Hebrew, Urdu, and Persian, require not only reversed text alignment but a full mirror of the page layout. Navigation that appears on the left in English appears on the right in Arabic. Icons that convey direction (forward arrows, back chevrons, progress indicators) are mirrored. Visual hierarchy flows from right to left.

The correct approach, and the one HiveAR will use from the start, is CSS logical properties throughout the frontend codebase. Logical properties express layout in terms of flow direction rather than physical direction: margin-inline-start instead of margin-left, padding-inline-end instead of padding-right, text-align: start instead of text-align: left. When the HTML dir attribute is set to rtl at the document level, logical properties automatically mirror the layout without any additional CSS rules.

The dir attribute will be set programmatically based on the active locale at session start. Locales with RTL directionality will be flagged in the locale configuration, and the application shell will apply dir="rtl" to the document root when such a locale is active.

> **RTL DESIGN REQUIREMENTS FOR CONTRIBUTORS**
>
> Use CSS logical properties exclusively. Physical directional properties (left, right, margin-left, padding-right) are prohibited in frontend stylesheets. Directional icons must be mirrored in RTL layouts. An icon component that points right in LTR must point left in RTL. Use CSS transforms or separate RTL-aware icon assets. Test layouts in both LTR and RTL before submitting UI contributions. RTL rendering must be verified, not assumed. Flexbox and Grid layouts are preferred over absolute or fixed positioning, as they respect flow direction automatically when combined with logical properties.

## Additional Locale Considerations

The following concerns are addressed through contributor coding standards rather than architectural mechanisms. They are documented here to ensure contributors are aware of them from the start.

Text expansion: German, Dutch, Finnish, and other European languages routinely produce strings 30 to 40 percent longer than their English equivalents. UI containers must use flexible sizing and wrapping text. Fixed-width labels that clip or overflow in non-English locales are localization defects.

CJK font fallbacks: the frontend font stack must include system CJK font fallbacks to ensure Chinese, Japanese, and Korean characters render correctly on systems where the primary web font does not cover those code points.

Number, date, and currency formatting: the frontend will never format these values directly. Formatted values will be received pre-rendered from the API, or the browser Intl API will be used with the active locale. Custom formatting logic in frontend code is prohibited.

Vertical text: traditional vertical text rendering used in some East Asian typographic contexts is not a consideration for HiveAR. Modern business software in Japanese, Chinese, and Korean markets uses horizontal LTR layout as the standard. Vertical text layout support is out of scope.

## Implementation Phasing

**HiveAR v1 (MVP):** Framework in place, English only. All UI chrome strings sourced from resource bundles, never hardcoded. All reference value labels rendered from API responses (which pull from i18n tables per [Wax Design Decision 11](../wax/WAX-0011-internationalization-architecture-and-reference-value-system.md)). No locale selection UI. No RTL CSS. The critical discipline: no hardcoded strings in components, enforced through code review.

**HiveAR v2:** User locale preference. Spanish resource bundle. RTL CSS logical properties (structural preparation).

**HiveAR v3+:** Full RTL Language Packs. CJK support. Text expansion accommodation.

**Breaking change risk: HIGH if strings are hardcoded in v1. NONE if resource bundles are used from day one.**

## Implications For Contributors

No UI string may be hardcoded in a component. All visible text must reference a resource key in the appropriate .resx file.

All CSS must use logical properties. Physical directional properties are not permitted in the frontend stylesheet.

Contributors adding new reference value types must ensure the API returns resolved, locale-aware labels for those values. The frontend must not perform reference value label resolution.

New Language Pack modules must provide resource bundle files covering all UI chrome keys defined in the core resource file. A Language Pack that omits keys will cause missing string errors in the UI and will be flagged as i18n non-compliant per [Wax Design Decision 10](../wax/WAX-0010-module-registry.md).
