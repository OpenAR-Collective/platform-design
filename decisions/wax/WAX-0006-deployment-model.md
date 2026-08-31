---
id: WAX-0006
title: "Deployment Model"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 6: Deployment Model

## Decision

HiveAR will be designed for agency-controlled deployment: installed on the agency's own infrastructure, or hosted by a vendor of the agency's choosing. The Collective will not operate a hosted SaaS instance. Organizations deploying the platform may install it on Windows Server, Linux, or cloud infrastructure of their choice (AWS EC2, Azure VM, GCP Compute, and equivalent). The platform will be distributed as a deployable package, not as a service.

## Rationale

The Collective's mission is to provide open infrastructure, not to operate it on behalf of others. SaaS operation would introduce ongoing operational costs, data liability, service level obligations, and regulatory exposure that are inconsistent with the Collective's nonprofit model and resource profile.

Agency-controlled deployment also aligns with the data security requirements of the collection industry. Agencies handling consumer financial data are subject to strict data security obligations. Maintaining direct control of their deployment environment, data storage, and network topology is a meaningful security and compliance benefit for agency operators.

## Platform Support Targets

Windows Server 2019 and later

Ubuntu LTS (20.04 and later) and other major Linux distributions

AWS EC2, Azure Virtual Machines, GCP Compute Engine (via standard Linux deployment)

Containerized deployment via Docker and Docker Compose (Wax v2 goal)

## Out Of Scope

The Collective will not provide hosted instances, managed updates, or operational support. Organizations requiring managed hosting or support services will be directed to vendors certified under the Collective's vendor certification program.

## Implementation Phasing

**Wax v1 (MVP):** Support Linux deployment (Ubuntu LTS) as the primary target. Docker Compose reference file for single-node deployment. Basic installation documentation. Windows Server support is a v2 goal; .NET runs on both, but testing and documentation can wait. No HA/DR reference architecture; single-node PostgreSQL is appropriate for pilot agencies. The reference deployment artifacts and their phasing across versions are specified in [Shared Design Decision 8](../shared/SHARED-0008-reference-deployment-architecture.md).

**Wax v2:** Windows Server deployment documentation and testing. Docker Compose HA reference (primary + replica). Upgrade and migration tooling.

**Wax v3+:** Kubernetes Helm chart. Managed deployment guidance for certified vendors.

**Breaking change risk: NONE.** Deployment model is operational, not architectural.
