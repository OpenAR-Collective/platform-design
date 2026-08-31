---
id: SHARED-0008
title: "Reference Deployment Architecture"
status: Accepted
version: 1.0
area: shared
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 8: Reference Deployment Architecture

## Decision

The Foundation provides Docker Compose reference architectures for deploying HiveAR and other applications built on Wax, for use by agencies hosting the platform themselves or by vendors hosting it on their behalf. The references are the concrete realization of the deployment model adopted in [Wax Design Decision 6](../wax/WAX-0006-deployment-model.md) and the high-availability and disaster recovery topology described in [Wax Design Decision 24](../wax/WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md). They are phased from a single getting-started configuration to a documented suite covering multiple deployment topologies with demonstration materials.

## Rationale

A working reference deployment lowers the barrier to adoption more than any amount of prose documentation. An operator clones the repository, runs a single command, and has a functioning system to evaluate within minutes. The Compose file itself serves as executable documentation of the supported topology: the services, their relationships, the network boundaries, and the persistent storage are all expressed in one readable file.

This decision is placed among the Shared decisions because a deployment reference is a cross-cutting operational concern rather than framework internals or accounts receivable business logic. Wax is never deployed in isolation; what an operator runs is an application built on Wax, with HiveAR serving as the reference instance. The closest companions to this decision are the repository architecture in [Shared Design Decision 1](SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md) and the development lifecycle in [Shared Design Decision 7](SHARED-0007-devops-and-contribution-lifecycle.md).

## Scope and Non-Goals

The reference architectures are starting points, not turnkey production systems. The Foundation does not operate, host, or manage any deployment on behalf of an operator. Each operating agency owns its own production hardening, including security configuration, secret management, backup verification, capacity planning, and monitoring integration. The references demonstrate a sound topology and provide a tested baseline; the operator adapts that baseline to its own environment, infrastructure, and compliance obligations.

## Reference Topology

The reference deployment expresses the component architecture as a set of composed services: the HiveAR application tier, the workflow service that processes asynchronous jobs, a PostgreSQL database tier, a pgBouncer connection pooler in front of the database, and a reverse proxy for TLS termination and request routing. At the high-availability tier, the database expands to a primary with one or more streaming replicas, with optional Patroni and a distributed consensus store providing automatic failover. The application and workflow tiers are stateless and horizontally scalable, consistent with [Wax Design Decision 24](../wax/WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md).

## Implementation Phasing

**Wax v1 (MVP):** A single reference Compose file for the simplest working deployment: the HiveAR application, a single-node PostgreSQL database, pgBouncer, and a reverse proxy for TLS. Each service carries inline comments, with pointers to upstream PostgreSQL and pgBouncer documentation. The goal is evaluation and first run. This tier deliberately omits replication and automatic failover; a single-node database is appropriate for pilot agencies, consistent with the v1 deployment scope in [Wax Design Decision 6](../wax/WAX-0006-deployment-model.md).

**Wax v2 and HiveAR v2:** A high-availability and disaster recovery reference configuration: a PostgreSQL primary with a streaming replica, pgBouncer, and optional Patroni with a distributed consensus store for automatic failover. Each reference ships with a written guide explaining every service, the rationale for its presence, and the specific changes an operator should make before production use. Reference Patroni configuration is provided alongside pointers to upstream Patroni, pgBouncer, and PostgreSQL streaming replication documentation.

**Wax v3+ and HiveAR v3+:** A documented suite of reference configurations covering distinct deployment scenarios, including single-node evaluation, high-availability and disaster recovery, deployment against an external managed PostgreSQL service, and a horizontally scaled multi-instance application tier. The suite is accompanied by written configuration guides and demonstration videos that walk an operator through standing up and configuring each topology.

**Breaking change risk: LOW. The reference architectures are example artifacts that operators copy and adapt; they impose no compile-time or runtime dependency on the platform. Topologies can be added, refined, or reorganized across versions without breaking any deployed system, since each operator runs its own adapted copy rather than consuming the references as a live dependency.**
