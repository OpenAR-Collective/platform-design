---
id: SHARED-0003
title: "API Surface"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 3: API Surface

## Decision

The HiveAR will expose a REST API as its published interface between the backend and all frontends. The API will be designed around use cases and read models rather than raw entity representations. Each endpoint serves a specific command or a specific query backed by a purpose-built read model. The API contract will be versioned. Breaking changes require a new version, not silent modification of existing endpoints.

## Rationale

REST is the dominant API style for enterprise backend systems. Every developer who has built a web application in the last fifteen years knows it. HTTP verbs express intent clearly. OpenAPI provides automatic documentation and client code generation. Tooling for testing, debugging, and integration is mature, widely available, and well understood by the contributor community Wax is targeting.

GraphQL's primary advantage is allowing clients to specify exactly which fields they need, avoiding overfetching. For Wax this problem is largely solved by the read model architecture. A collector queue read model is already a pre-built table containing exactly the right fields for that view. A REST endpoint backed by that model returns the right shape of data without any overfetching. The motivation for GraphQL's flexibility disappears when the read side is already purpose-built per use case.

GraphQL also introduces meaningful complexity: schema definition language, resolvers per field, query complexity attack surface, and a steeper learning curve for module contributors. For a compliance-first platform where the API surface is the single point of authentication, authorization, and input validation, simplicity and predictability in the API design are features, not limitations.

## Use-Case-Oriented Endpoint Design

REST endpoints are organized around commands and use-case-specific queries rather than generic entity CRUD. This means the API reflects what the system does rather than what data it stores. Illustrative examples:

| **Type** | **Endpoint** | **Backed By** |
| --- | --- | --- |
| Command | POST /account/{id}/post-payment | PostPaymentCommandHandler |
| Command | POST /account/{id}/update-address | UpdateAddressCommandHandler |
| Command | POST /account/{id}/close | CloseAccountCommandHandler |
| Query | GET /account/{id}/collector-view | workflow.collector_queue_read_model |
| Query | GET /account/{id}/audit-history | core.event (compliance use case) |
| Query | GET /account/{id}/supervisor-summary | workflow.supervisor_read_model |
| Query | GET /collector/{id}/queue | workflow.collector_queue_read_model |
| Query | GET /reporting/aging | reporting.aging_read_model |

Commands never return data beyond a success or failure acknowledgment. Queries never change state. This separation is enforced by convention and reinforced by the CQRS architecture described in [Wax Design Decision 2](../wax/WAX-0002-cqrs-model.md).

## Versioning

The API version is included in the URL path: /api/v1/account/{id}/collector-view. When a breaking change is required, a new version path is introduced. The prior version remains available for a documented deprecation period. Non-breaking additions (new optional fields in responses, new optional query parameters) do not require a version increment.

## Openapi Documentation

All endpoints will be documented using OpenAPI 3.x. The OpenAPI specification file will be published as part of the repository and kept current with the codebase. Endpoint documentation will include command and query descriptions, request and response schemas, error codes, and authentication requirements. Accurate and current API documentation is a contributor requirement, not an afterthought.

## Implementation Phasing

**HiveAR v1 (MVP):** Core endpoints only: account CRUD, entity and contact CRUD, payment posting, account search and filtering, assignment operations, event and audit history queries, authentication endpoints. API endpoints can be more CRUD-like in v1; use-case-oriented endpoint optimization is a v2 refinement.

**HiveAR v2:** Use-case-oriented endpoints based on real usage data. OpenAPI 3.x documentation published with the repository. Module-contributed endpoints through the module contract.

**HiveAR v3+:** GraphQL option for complex query patterns. Webhook and callback registration for integrations.

**Breaking change risk: LOW.** API versioning handles the transition. v1 endpoints remain supported.

## Implications For Contributors

Every module that exposes new queries must provide a corresponding read model and a documented REST endpoint. Undocumented endpoints will not be accepted into the repository.

Command endpoints must validate all inputs at the API layer before passing to command handlers. Validation rules belong to the API contract, not just to application logic.

The API contract is the stable surface third-party developers build against. Any change to an existing endpoint's request or response shape is a breaking change and requires a version increment.

Modules may not expose direct database access through their API endpoints. All responses must come from read models or the event store through defined query handlers.
