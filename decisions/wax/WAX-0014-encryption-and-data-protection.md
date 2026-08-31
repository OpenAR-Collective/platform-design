---
id: WAX-0014
title: "Encryption and Data Protection"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 14: Encryption and Data Protection

## Decision

TLS is required and enforced for all API and UI connections. Column-level encryption for defined PII fields is provided through PostgreSQL's pgcrypto extension. Infrastructure-level encryption is left to agency infrastructure choices. The Collective is responsible for building a platform that is securable. Security decisions beyond the platform mechanisms are agency responsibilities.

## Transport Security

TLS is required for all connections to the HiveAR application in every environment tier including development. The default installation configuration enforces TLS and does not permit plaintext connections.

## Column-Level PII Encryption

Defined PII fields in the data model will be encrypted at the column level using PostgreSQL's pgcrypto extension. Fields subject to column-level encryption will include social security number, date of birth, financial account numbers, and other fields designated as high-sensitivity PII in the Wax v2 security specification. The encryption key is never stored alongside the encrypted data. Key management is the deploying agency's responsibility. Because Wax runs under agency-controlled deployment by design, encryption keys never pass through Collective infrastructure.

## Infrastructure Encryption

Disk encryption, database volume encryption, and similar infrastructure-level controls are left to agency infrastructure choices. The platform's responsibility is column-level encryption for the most sensitive fields and TLS for transport.

## What The Foundation Is Not Responsible For

Infrastructure security, network topology and firewall configuration, secrets management practices, backup and recovery procedures, penetration testing, and the specific security controls required by an agency's contracts and certifications are agency responsibilities. The platform provides the mechanisms. Agencies configure and operate them in accordance with their own obligations.

## Implementation Phasing

**Wax v1 (MVP):** Transport security (TLS) required. Infrastructure encryption (disk-level) documented as a deployment recommendation. Column-level PII encryption deferred to v2; PII stored as plaintext in v1. Documented as a known limitation.

**Wax v2:** Column-level PII encryption via Wax Security Module (WSM). pgcrypto integration. Encryption envelope format in event payloads.

**Wax v3+:** Key rotation automation. Retention-triggered key destruction.

**Breaking change risk: LOW.** Encryption is additive to the storage layer. The envelope format in event payloads is a serialization concern that does not affect schema.
