---
id: SHARED-0004
title: "Frontend Framework"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 4: Frontend Framework

## Decision

The HiveAR reference frontend will be built using Blazor WebAssembly. Blazor WebAssembly is Microsoft's web framework for building browser-based applications in C# on the .NET runtime. It runs entirely in the browser using WebAssembly, requiring no persistent server connection. MudBlazor will serve as the primary open-source component library for the reference implementation.

## Rationale

The single most significant factor is contributor stack alignment. The decision to build Wax in C# ([Wax Design Decision 25](../wax/WAX-0025-primary-programming-language.md)) was made in part because the expected contributor community consists of developers who work in or around the accounts receivable industry, and that population skews toward C# and .NET. Blazor WebAssembly extends that alignment to the frontend: a contributor who builds a C# command handler, writes C# event projections, and defines C# domain types can also contribute to the UI without switching languages or maintaining parallel type definitions.

Shared types across the stack are a practical benefit that compounds over time. A C# record defined once is available to the backend command handler, the API response serializer, and the Blazor UI component. There is no translation layer, no risk of frontend and backend types drifting out of sync, and no need for contributors to maintain equivalent type definitions in two languages.

Blazor WebAssembly's stateless model is also a better fit for the agency-controlled deployment target than Blazor Server. Blazor Server requires a persistent SignalR connection between the browser and the server for each active user session. In an agency-controlled deployment, where the agency or its hosting vendor controls the network topology, load balancing, and infrastructure, a stateless WebAssembly client that communicates through the versioned REST API is more robust and imposes no special infrastructure requirements.

Blazor also integrates naturally with ASP.NET Core's authentication and authorization infrastructure. Role-based access control, claims-based identity, and API authentication patterns are shared across the backend and frontend with no framework boundary to bridge. For a compliance-first platform, reducing the surface area where security logic must be duplicated or coordinated across layers is a meaningful benefit.

## Why Not React

React is the closest alternative and a genuinely strong option. Its component ecosystem is larger, its freelance developer pool is deeper, and its maturity in enterprise web applications is well established. For a contributor community that skewed more toward frontend specialists, React would be the natural choice.

For Wax's expected contributor profile, the single-language advantage of Blazor outweighs React's ecosystem depth. However, this assessment is based on an expectation about who will contribute, and that expectation may prove incorrect. If the community that forms around HiveAR in Year 1 and Year 2 demonstrates a meaningful frontend-specialist presence that finds Blazor's ecosystem limiting, the Collective will revisit this decision. The decoupled backend architecture ([Shared Design Decision 2](SHARED-0002-decoupled-frontend-and-backend.md)) means the frontend can be replaced without disrupting the platform's core. React remains the leading alternative and a realistic path if community feedback warrants it.

## Component Library: MudBlazor

MudBlazor is a free, open-source Material Design component library for Blazor. It provides the UI primitives a collections workflow application requires: data grids capable of handling large account lists, form components, date and time pickers, navigation components, dialog and notification systems, and charting capabilities. It is actively maintained, well documented, and widely used in the Blazor community. Adopting MudBlazor as the reference implementation's component library reduces the amount of custom component development required in Year 1 and gives contributors a familiar starting point.

MudBlazor is the default for the Collective's reference implementation. Module authors building their own UI components are not required to use MudBlazor, but components contributed to the core repository will follow MudBlazor conventions for consistency.

## Implementation Phasing

**HiveAR v1 (MVP):** Ship with Blazor WebAssembly and MudBlazor. Core screens: account list and search, account detail, entity detail, payment entry, basic reporting, admin configuration. No custom component development beyond MudBlazor out of the box. Note: Blazor WASM initial download size will be noticeable on slow connections; document it and consider lazy loading.

**HiveAR v2:** Richer UI components (workflow designer, entity merge UI, report builder). Performance optimization (lazy loading, caching).

**HiveAR v3+:** React alternative frontend (if community demand warrants it). Mobile-responsive design improvements.

**Breaking change risk: NONE for the backend.** The decoupled architecture ([Shared Design Decision 2](SHARED-0002-decoupled-frontend-and-backend.md)) makes the frontend replaceable by design.

## Implications For Contributors

All reference frontend code will be written in C# using Blazor WebAssembly. JavaScript will be used only when a specific capability has no Blazor-native implementation, and such usage must be documented and minimized.

Frontend components must not hardcode user-facing strings. All UI chrome text will be sourced from resource bundles per the internationalization architecture ([Shared Design Decision 5](SHARED-0005-frontend-internationalization.md)).

Frontend components must not format dates, times, currencies, or reference value labels directly. Formatted values will be received from the API or rendered using the browser Intl API with the active locale.

Frontend code must not contain business logic. Validation, business rules, and compliance logic belong in command handlers on the backend. The frontend submits commands and renders read model responses.
