---
id: WAX-0018
title: "Access Control"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 18: Access Control

## Decision

Wax ships with a complete, non-bypassable role-based access control model. Roles are assigned to principals. Principals include human users and API service accounts, treated identically by the permission evaluation path. Row-level security is enforced at the PostgreSQL database layer as the primary access boundary. API service accounts may be scoped to a specific subset of endpoints in addition to their role permissions.

## Role-Based Access Control

Permissions are defined at the resource and operation level within a specific organization scope. Roles are defined per organization and are user-configurable items subject to the version control model from [Wax Design Decision 21](WAX-0021-configuration-management-and-environment-lifecycle.md). A collector role might grant the ability to post payments and log contact attempts on assigned accounts. An administrator role grants configuration access. Role definitions are configuration, not code.

## API Service Account Scoping

Service accounts are principals in the RBAC model and hold roles like any other principal. Each service account may additionally be scoped to a specific subset of API endpoints from the published API catalog. A payment processor integration cannot close accounts or modify reference values, even if its assigned role would otherwise permit those operations, if those endpoints are excluded from its endpoint scope. Agency administrators create and manage service accounts through a dedicated administration dashboard. Authentication method is configurable per service account, with supported methods including shared secret and OAuth 2.0 client credentials.

## Row-Level Security

PostgreSQL row-level security is implemented at the database layer for all tables containing account data, contact data, event records, and other sensitive content. Application-layer authorization checks are a second line of defense. RLS is a design-time architectural decision because it affects how every query in the platform is written and how every module author must structure data access.

## Implementation Phasing

**Wax v1 (MVP):** Basic RBAC with a small fixed set of roles: Administrator, Manager, Collector, Read-Only. Simple permission checks in API endpoints. No row-level security. The RBAC schema (user-to-role assignments, permission definitions, role hierarchy table) must support RLS from day one even though enforcement is deferred.

**Wax v2:** Row-level security policies on core and ar tables. API service account scoping. Per-organization role assignments for multi-org deployments.

**Wax v3+:** Field-level security (PII visibility by role). Dynamic permission sets.

**Breaking change risk: MEDIUM.** If v1 uses a simplistic permission model (a single is_admin flag), retrofitting proper RBAC touches every authorization check. Ship the role and permission tables in v1.

## Implications For Contributors

All database queries in Wax and in modules must be written with awareness of the RLS model. A query that does not correctly participate in the session context will fail in production.

Module authors who expose new API endpoints must register those endpoints in the published API catalog so they can be included in or excluded from service account endpoint scopes.
