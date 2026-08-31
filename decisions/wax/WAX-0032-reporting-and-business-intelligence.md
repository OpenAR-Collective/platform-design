---
id: WAX-0032
title: "Reporting and Business Intelligence"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 32: Reporting and Business Intelligence

## Decision

Wax will not build a reporting or business intelligence engine. The platform already exposes its data as a complete, secured view layer, and that view layer is the reporting surface. An operator points a mature open-source business intelligence tool at it for custom and ad-hoc reporting, charting, dashboards, and scheduling. Wax provides a light, tool-agnostic setup helper for connecting such a tool to the view layer, and supports a small, fixed set of non-configurable operational dashboards rendered as application screens for the most basic needs. The specific dashboards a product ships, and any domain-specific reference report pack, are concerns of the domain implementation built on Wax rather than of the framework.

## The Data Layer Already Exists

Reporting is usually treated as a feature to build. Here the hard part is already done by decisions made elsewhere. Every entity and every read model is exposed as a SQL view that decrypts personal information and resolves internationalized labels transparently, scoped by the connecting credential's role through row-level security, as established in Wax Design Decisions 2, 14, and 18. A business intelligence tool, a reporting tool, or any direct SQL client with read credentials queries those views and receives clean, correctly permissioned data with no special configuration. The question this decision answers is therefore not how to make the data reportable, which it already is, but what, if anything, the platform should build on top of that surface.

## No Native Reporting Engine

The platform will not grow a query engine, a visualization layer, a dashboard designer, or a report scheduler. Those capabilities are solved, mature, and freely available in open-source business intelligence tools that do them far better than the Foundation could. Building a native engine would reinvent that work less well and would pull the platform into a software category that is not its purpose, the same posture taken toward document management in [Wax Design Decision 30](WAX-0030-document-storage.md). Custom reports, ad-hoc queries, charting, exports, and scheduled delivery are the business intelligence tool's responsibility, reached through the view layer.

## Where Report Shaping Happens, and the No-Code Path

An agency almost never needs to create a platform projection for reporting, and never needs to touch source code. Three layers cover the need. Data the platform already captures is exposed as granular views, so reporting over existing data requires nothing new. Report-specific shaping, aggregations, rollups, and joins across entities such as a total by client by month, is defined in the business intelligence tool's own modeling layer as a dataset or saved query over those views, which is exactly what such a tool is built to do. Data the platform does not yet model is captured by creating a user-defined table, already a no-code administrative operation, for which the view generator automatically produces a decrypting, label-resolving, row-level-security-scoped view that the business intelligence tool queries like any built-in one.

The only need that falls outside those three layers is a heavy pre-computed rollup maintained on the server for performance, which is rare. When it genuinely arises, it is handled as a materialized view refreshed by a recurring Job Scheduler job. A no-code declarative rollup definition is a possible future capability rather than a present requirement, because the business intelligence tool's own caching and aggregation cover the common cases. The governing division is that the platform owns granular, secured exposure of its data, and the business intelligence tool owns report shaping, with no source code written on either side.

## Native Operational Dashboards Are Fixed by Design

Wax supports a small, fixed set of operational dashboards rendered as ordinary application screens over projection views, the same kind of screen as any other in the application. They exist so that a deployment with genuinely basic needs is not forced to stand up a separate business intelligence tool to see its most fundamental operating numbers. Which dashboards a product ships, and what questions they answer, is a concern of the domain implementation rather than the framework; Wax establishes that such dashboards are permitted and how they must behave.

These dashboards are deliberately non-configurable and non-exportable. There is no column picker, no chart builder, and no export to a spreadsheet. That constraint is the boundary that keeps the platform from accreting a reporting tool one feature request at a time, and it is a stated principle rather than a temporary limitation: a native dashboard answers a fixed question at a glance, and the moment a user wants to change, chart, export, or schedule one, that is the business intelligence tool's role. A domain implementation keeps its dashboard set deliberately small, chosen as the few numbers every operator reviews rather than as an attempt to define a basic report, which is a line no two operators would draw the same way.

## Setup Helper and Reference Packs

Pointing a business intelligence tool at the platform is made turnkey by a light setup helper that connects the tool to the view layer, rather than leaving it a manual configuration exercise. The helper is tool-agnostic, since the view layer is standard SQL, and it is a deliverable rather than a maintained software integration the platform must carry. Operators commonly expect a system to arrive with a set of common reports already available, and the platform supports this through domain-specific reference report packs: sets of prebuilt queries and dashboards for a business intelligence tool that a deployment imports and runs on the first day. A pack is report definitions over the existing views, and its content is a concern of the domain implementation rather than the framework, since the reports a domain needs are inherent to that domain.

## Tool Independence and License Discipline

The framework names no specific business intelligence tool. Because integration is through the standard view layer rather than by embedding any tool, a deployment may point any business intelligence or reporting tool that speaks SQL at the platform. The framework states one tool-related principle, license discipline: where a domain implementation publishes a reference report pack, that pack should target a permissively licensed tool, so that bundling, demonstrating, or distributing the pack carries no copyleft entanglement. The specific tool a domain implementation anchors its pack to is a concern of that implementation, made under this principle. An operator sophisticated enough to build a different product on Wax is equally capable of selecting the reporting tool that suits it.

## The Audit Trail Is Not a Reporting Source

The event store and the key audit log remain outside the general reporting surface, consistent with [Wax Design Decision 2](WAX-0002-cqrs-model.md). They are reached only through the restricted compliance audit interface available to roles granted audit access, never through the reporting view layer or a business intelligence tool connection. Reporting draws on the entity and read model views, which present current and historical state for analysis, while the integrity of the event history is preserved by keeping it out of the general query path.

## Implementation Phasing

**Wax v1 (already true):** The view layer exposing entity and read model data for querying, which is established in [Wax Design Decision 2](WAX-0002-cqrs-model.md) and requires nothing additional for reporting to consume.

**Wax v2:** The tool-agnostic setup helper for connecting a business intelligence tool to the view layer, framework support for a small fixed set of non-configurable native operational dashboards as application screens, and the license-discipline principle for reference packs. These accompany the row-level security and view-decryption capabilities that mature in v2. The domain-specific reference report pack, the specific dashboards, and the anchored tool are deliverables of the domain implementation rather than the framework.

**Wax v3+:** A possible no-code declarative rollup definition for server-maintained pre-computed reporting projections, if demand warrants it beyond materialized views refreshed by Job Scheduler jobs.

**Breaking change risk: LOW. Reporting consumes the existing view layer rather than introducing new platform machinery. The reference pack and setup helper are deliverables external to the core, and the native dashboards are read-only screens over projections.**

## Implications For Contributors

Reporting is not a platform feature to build. A contributor must not add a query engine, a visualization layer, a dashboard designer, or a report scheduler to the platform. Custom and ad-hoc reporting is the business intelligence tool's responsibility, reached through the view layer.

Native dashboards stay fixed. The small set of in-application operational dashboards must remain non-configurable and non-exportable. A request to make one customizable, chartable, or exportable is a request to use the business intelligence tool, not to extend the dashboards.

New reporting data flows through views, not bespoke projections. Data the platform already holds is reportable through its existing views. New data is captured through user-defined tables, whose views are generated automatically. Contributors do not hand-write projections to satisfy a reporting need without a clear performance justification.
