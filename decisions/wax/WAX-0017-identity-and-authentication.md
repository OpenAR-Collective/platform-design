---
id: WAX-0017
title: "Identity and Authentication"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 17: Identity and Authentication

## Decision

Every human user and every API service account is a row in core.user. Neither is a PostgreSQL database user. Authentication may be handled by HiveAR's own credential store or delegated to an external identity provider. Multiple authentication providers may be active simultaneously. Active Directory group membership may be mapped to Wax roles as a synchronization mechanism. Automated user provisioning via SCIM is supported but not required.

## Users as Application Rows

The application connects to PostgreSQL using a small number of service credentials covering normal operations, migrations, and optionally read-only reporting. Those are the only database-level credentials. All human users and all service accounts are rows in core.user identified by UUID surrogate keys. PostgreSQL roles are infrastructure-level concerns applying to these service credentials only, never to application-level principals.

## Authentication Modes

Wax supports multiple authentication modes simultaneously. Human users may authenticate against Wax's own credential store or against an external identity provider. Multiple identity providers may be configured on a single installation. Supported external authentication protocols will include LDAP bind authentication and SAML 2.0 and OpenID Connect for single sign-on. The identity provider handles authentication only. Authorization is always determined by HiveAR's own RBAC model.

## Active Directory Group to Role Mapping

Agencies using Active Directory or a compatible directory service may configure group-to-role mappings. When a user authenticates, Wax syncs Wax roles based on the configured mapping. The authoritative record of a user's roles is always the Wax database, not the directory. Wax operates correctly when the directory is unavailable. Group-to-role mapping is a synchronization mechanism, not a live dependency.

## Automated User Provisioning via SCIM

Wax will support SCIM as an optional integration for automated user lifecycle management. Identity providers that support SCIM can push user creation, deactivation, and group membership changes to Wax automatically. Combined with group-to-role mapping, this enables a fully automated identity lifecycle. SCIM is supported but not required. Agencies without directory infrastructure provision users manually through the Wax administration UI.

## Implementation Phasing

**Wax v1 (MVP):** Users as application rows in core.user. Local username and password authentication. No Active Directory integration, no SCIM provisioning.

**Wax v2:** Active Directory and LDAP authentication. AD group to role mapping.

**Wax v3+:** SCIM automated user provisioning. SSO integration patterns.

**Breaking change risk: LOW.** The user table schema should accommodate external identity provider fields (nullable) from v1.

## Implications For Contributors

No module may store user credentials, session tokens, or authentication material. These are managed exclusively by Wax's authentication subsystem.

Authentication provider configuration is installation-scoped, not organization-scoped. All organizations on an installation share the same configured identity providers.
