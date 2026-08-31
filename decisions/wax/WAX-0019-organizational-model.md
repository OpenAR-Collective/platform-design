---
id: WAX-0019
title: "Organizational Model"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 19: Organizational Model

## Decision

Every HiveAR installation contains at least one organization, created during the installation wizard. An organization is a UUID surrogate key with an i18n-defined name. There is no installation state without an organization. All platform subsystems operate in an organization context at all times. A single installation may contain multiple organizations for multi-entity deployments. Open multi-tenancy across unrelated agencies is explicitly out of scope.

## Always-Present Organization

The first organization is created before any other configuration is possible. Single-entity agencies interact with their one organization without ever needing to engage with the concept. No code path in Wax or in any module branches on whether an organization exists, because one always does. RBAC roles, workflow definitions, module configuration, reference value definitions, UDT definitions, and all account data are scoped to an organization.

## Multi-Organization Deployments

A single installation may contain multiple organizations, each representing a distinct legal entity, business unit, or operational division. Module activation, module configuration, reference value definitions, workflow definitions, RBAC role definitions, and all account data are isolated per organization. Users may be granted access to one or more organizations and can switch between them within an authenticated session. This model addresses two documented use cases: a company operating multiple distinct legal entities on shared infrastructure, and a client requiring complete data and workflow isolation.

## Multi-Tenancy Boundary

Open multi-tenancy, meaning one installation serving unrelated agencies with no organizational relationship to each other, is explicitly out of scope. Certified hosting vendors achieve isolation between unrelated agency clients by running one HiveAR installation per client.

## Implementation Phasing

**Wax v1 (MVP):** Single organization per installation, created during setup. organization_pk column on relevant tables from day one (accounts, users, configuration). No multi-org UI or configuration.

**Wax v2:** Multi-organization support within a single instance. Per-organization module configuration.

**Wax v3+:** Organization hierarchies (parent and child relationships).

**Breaking change risk: MEDIUM if organization_pk is omitted in v1.** Adding an organization foreign key to every table in production is the kind of migration that breaks a weekend.

## Implications For Contributors

All configuration items must carry an organization scope. A workflow definition, UDT definition, or role definition with no organization association is a schema violation.

Module authors must ensure all account-related tables include an organization_fk column. Cross-organization data access through module queries is not permitted.
