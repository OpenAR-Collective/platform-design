---
id: SHARED-0002
title: "Decoupled Frontend and Backend"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 2: Decoupled Frontend and Backend

## Decision

The HiveAR will be built with a strict separation between the backend and the frontend. The backend will expose a published API surface as its only interface. The frontend will consume that API and have no direct access to the database or internal application state. The two layers will be independently deployable, independently versioned, and independently replaceable.

## Rationale

A decoupled architecture means that the user interface can be replaced, rewritten, or supplemented without touching the backend. An agency that wants to build a custom UI for their collectors, a third-party developer who wants to build a mobile supervisor dashboard, or a future community contributor who wants to offer an alternative frontend can do so without forking the core platform. The backend contract, meaning the published API, is the stable surface they build against.

This also means that the Collective's own frontend choices are not permanent decisions. If the community determines that a different frontend framework serves practitioners better, it can be swapped out without re-engineering the system underneath it. The backend investment is preserved regardless of how the UI evolves.

For a compliance-first platform, decoupling also provides a meaningful security benefit. The API surface is the single point at which authentication, authorization, and input validation are enforced. There are no side doors through which a frontend can reach data it has not been explicitly granted access to.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. The decoupled architecture (REST API between frontend and backend) ships in v1. API versioning from day one (v1 endpoints).

**Breaking change risk: NONE if API versioning is in place. HIGH if the frontend makes direct database calls that must be unwound later.**

## Implications

All frontend-to-backend communication will pass through the published API. No direct database access from the frontend layer under any circumstances.

The API contract will be versioned. Breaking changes will require a new version, not silent modification of existing endpoints.

The API surface is implemented as a REST API with use-case-oriented endpoints, as adopted in [Shared Design Decision 3](SHARED-0003-api-surface.md). The decoupling principle established here is what makes the API the sole interface and enables the frontend and backend to be independently versioned and replaced.

Third-party developers and community contributors may build alternative or supplementary frontends against the published API. This is an intentional feature of the architecture, not a risk to be managed.
