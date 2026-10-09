---
id: SHARED-0006
title: "File Interface Engine"
status: Accepted
version: 1.1
area: shared
date: 2026-10-08
supersedes: none
license: CC-BY-4.0
---

# Shared Design Decision 6: File Interface Engine

## Decision

Wax will include a file interface engine that supports bidirectional data exchange between the platform and external systems. The engine defines a layout definition model for file grammar, a two-phase import pipeline with staging review and approval, an exceptions queue for change import conflicts, an export engine driven by the event store and read models, and a mapping and conditional logic layer shared with the workflow engine. The engine targets any registered aggregate root; it is not restricted to account records. HiveAR registers AR-specific aggregate types, import category rules, and a mandatory balancing gate as domain contributions to this engine.

## Wax Layer: File Interface Infrastructure

The Wax layer provides the file interface engine's structural foundations: the layout definition model, import and export pipelines, mapping and conditional logic, post-record trigger mechanism, pre-approval gate hook interface, auto-approve configuration, and custom parser extension point.

Layout Definition Model

A layout definition describes the grammar of a file independent of direction. The same definition governs both inbound parsing and outbound writing. A layout definition is a tree of record type definitions. Each record type carries a discriminator rule, a role (header, detail, subtotal, or trailer), and an ordered list of field definitions. Field definitions specify position and length for fixed-width formats, or delimiter position for delimited formats, plus format masks for dates, numbers, and typed values. A field that holds money maps to a typed monetary value, so a layout supplies an amount and either a currency field or a fixed currency, and a layout used in an installation whose Region Packs name one currency supplies neither, because the default currency applies, as defined in [Wax Design Decision 34](../wax/WAX-0034-monetary-values-and-currency.md). Hardcoded values, calculated subtotals, record counters, and run-date stamps are declared as synthetic fields and resolved during the write pass. The layout engine is implemented natively in C# with no external ETL library dependency.

Agencies whose file formats cannot be expressed in the standard layout model may implement a published C# interface as a custom parser and register it through the module registry. Custom parsers bypass Collective review and are the installing agency's responsibility.

Import Pipeline: Two Phases

The import pipeline operates in two phases. In the load phase, the layout engine parses the source file and the mapping layer evaluates each parsed record against mapping rules and conditional logic, producing a queue of pending commands rather than raw source rows. For change imports, each command records the observed field value at evaluation time as a precondition. The staging area holds this command queue. Reviewers see commands expressed in domain terms: old and new values for field mutations, plain-language descriptions for domain operations.

In the approval phase, the command handler processes each pending command. For change imports, the precondition is re-evaluated immediately before execution. Commands whose preconditions are no longer satisfied route to an exceptions queue rather than executing silently on stale data. The precondition check is optimistic concurrency applied at the file interface layer: it detects that another process modified the same record while the import sat in staging, and routes the conflict for human resolution rather than applying a potentially incorrect mutation.

Exceptions Queue

The exceptions queue holds commands from change imports whose preconditions were no longer satisfied at execution time. The reviewer can drill into exceptions by aggregate, command type, or field. Three resolution options are available: apply anyway (override the precondition check and execute the command), skip (cancel the pending command without applying it), and re-evaluate (run the mapping rules against the current state of the record to produce a new pending command if the rules still fire). Demographic field conflicts on change imports are resolved by the golden record engine rather than the exceptions queue; see the HiveAR Layer section below.

Export Engine

Two export types are defined. Delta exports are driven by the event store: the export definition specifies a target aggregate type, qualifying event types, and a date range. The engine queries the event store for events matching the criteria and produces a file of records where qualifying activity occurred within the window. Inventory exports are driven by a read model query: the export definition specifies a target aggregate type and a scope filter using the same field picker and query builder used by batch workflows, producing a full population file constrained to the declared scope.

Both export types support optional write-back events. After the output file is produced, the export engine fires configurable actions against included records through normal command handlers.

An export definition is also exposed as a workflow action type. Workflows may initiate an export run as part of their action graph, with the export definition selected as a parameter.

Mapping and Conditional Logic Engine

The mapping layer handles three constructs: field assignments, value translation tables, and conditional rules. Field assignments map source field positions or delimiter columns to target aggregate fields or command parameters. Value translation tables provide explicit input-to-output substitutions, such as client status codes to internal reason codes or external disposition values to internal closure types. Conditional rules evaluate one or more field conditions and, when met, execute actions: set a staging variable, override a field assignment, skip the record, or select an alternate command type.

The condition evaluator and action dispatch for the mapping layer are shared with the workflow engine ([Wax Design Decision 23](../wax/WAX-0023-workflow-automation-engine.md)). Contributors familiar with the workflow designer will recognize the condition and action model.

Post-Record Trigger Mechanism

Each import definition declares an optional post-record trigger. The trigger is scoped to the import definition and is distinct from triggers on any other definition for the same aggregate type. The trigger fires after a record's full command set is applied during the approval phase. Workflows attach using the standard workflow engine subscription model. Agencies with multiple import definitions for the same aggregate type configure independent triggers per definition, so downstream workflows are isolated by source.

Pre-Approval Gate hook

Wax provides a pre-approval gate hook mechanism for import definitions. A gate registered against an import definition is evaluated before the approval action becomes available to reviewers. If the gate condition is not satisfied, approval is blocked. A supervisor with appropriate RBAC privilege may override a blocked gate, but doing so requires a mandatory comment that is written to the audit record. Gate implementations are provided by domain layers and modules; Wax defines the interface and the enforcement mechanism.

Auto-Approve Configuration

An auto-approve flag is configurable per import definition. When set, the import bypasses manual staging review and applies the command queue immediately on completion of the load phase. Auto-approve is appropriate for trusted sources with consistent track records where manual review adds no practical value.

Aggregate Scope

The file interface engine is not restricted to accounts. Any aggregate root registered with the module registry is a valid import and export target. Module authors register their aggregate types to make them available for file interface operations.

Pipeline mechanics including chunked processing, parallel workers, fault isolation, and retry are provided by the Wax batch execution engine.

## HiveAR Layer: AR-Specific Registrations and Rules

HiveAR registers AR-specific content with the file interface engine: import category definitions, a mandatory balancing gate for new business and payment imports, aggregate registrations, value translation table content, and post-record trigger defaults.

Import Categories and Class Hierarchy

HiveAR defines four import categories organized in a class hierarchy. The base class is the net-new import, which produces creation commands for records that do not yet exist. Net-new imports carry no precondition checking and no balancing requirement. Three types extend or derive from the base:

Record Addition Import: a pure instance of the net-new base class. Covers any aggregate type that is neither account nor payment, including users, clients, and legal cases. No balancing requirement.

New Business Import: produces account creation commands. Inherits net-new pipeline behavior. Adds the mandatory balancing gate as a pre-approval control.

Payment Import: produces payment posting commands. Inherits net-new pipeline behavior. Adds the mandatory balancing gate. Control totals typically represent net payment amounts balanced to a bank deposit register or client remittance total.

Change Import is a distinct class, not a subclass of net-new. It produces field mutation and domain action commands against existing records of any aggregate type. Precondition checking applies to all commands. Staging review presents the full pending command set as a diff before approval. The exceptions queue and three-option resolution are specific to this class. Domain operations such as removing an account from a set or marking a user inactive are expressed as pending commands alongside field mutations, not as a separate mechanism.

Mandatory Balancing Gate

The mandatory balancing gate on New Business and Payment imports is implemented as a Wax pre-approval gate hook with HiveAR-provided balancing logic. The gate calculates the actual record count and the net amount total, per currency, from the loaded records and compares them to declared control totals, and each declared amount total states its currency. In a single-currency installation a declared total states none, and the default currency applies. Totals in different currencies are never added together, so a file that holds more than one currency balances in each. The control total source is declared on the import definition with three options: a trailer record in the file, a manually entered value at review time, or a companion control file delivered alongside the import file. The approve action is unavailable until the calculated totals match the declared totals. A supervisor with appropriate RBAC privilege may override the gate with a mandatory comment.

This design reflects the industry convention that collection agencies balance new business and payment batches to client-provided control totals. The balancing gate enforces this as a structural control rather than a manual checklist item.

Demographic Field Conflict Resolution

Demographic field conflicts on change imports are resolved by the golden record engine ([HiveAR Design Decision 2](../hivear/HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md) and [HiveAR Design Decision 3](../hivear/HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md)) rather than the standard exceptions queue. The import definition declares a source type and optional recency date, enabling the golden record engine to evaluate incoming values against existing demographic history using source reliability, recency, and corroboration scoring. Conflicts route through the scoring engine rather than surfacing as manual exceptions.

Aggregate Registrations

HiveAR registers accounts, entities, and payments as import and export targets with the file interface engine's aggregate registry. Additional aggregate types introduced by HiveAR modules are registered by those modules.

Value Translation Content

HiveAR contributes industry-specific value translation table content for the mapping engine, including standard mappings for debt type codes, account status transitions, and common client-reported disposition values. Agencies extend these defaults with their own client-specific mappings using the same mapping designer tool.

AR-Specific Workflow Triggers

HiveAR provides default post-record trigger registrations for new business and payment import definitions, aligned with standard AR collection workflow patterns. Agencies configure additional triggers per import definition using the standard workflow engine subscription model.

## Implementation Phasing

**Wax v1 (MVP)**: Layout engine and native C# parser. Two-phase import pipeline with staging area, exceptions queue, and three-option resolution. Export engine (delta and inventory). Mapping and conditional logic layer. Post-record trigger interface. Pre-approval gate hook interface. Auto-approve configuration. Custom parser registration interface. Schema for import and export definitions. Not included in v1: layout designer UI, mapping designer UI, value translation table management UI.

**HiveAR v1 (MVP)**: Import category registrations (net-new base class and four subtypes). Mandatory balancing gate for New Business and Payment imports. Aggregate registrations for accounts, entities, and payments.

**HiveAR v2**: Layout designer UI. Mapping designer UI. Value translation table management UI. Inventory file reconciliation and exception reporting. AR-specific post-record trigger defaults.

Breaking change risk: LOW. The pipeline architecture and import and export definition schema are stable. UI tooling additions in v2 do not require schema migration or interface changes in v1 code.

## Implications For Contributors

The file interface engine is a Wax component. Module authors extend it by registering aggregate types through the module registry, contributing import category subclasses, and providing value translation table content. Modules may not bypass the two-phase pipeline or the pre-approval gate mechanism.

Custom parsers registered through the module registry bypass Collective code review. Module authors shipping custom parsers accept full responsibility for parser correctness, including input validation and resource limits.

Post-record triggers must use the standard workflow engine subscription model. Direct execution of side effects from within the import pipeline is not permitted.

HiveAR domain authors adding new aggregate types to the AR platform must register those types with the aggregate registry to make them available for file interface import and export operations.

The mapping and conditional logic layer is shared with the workflow engine. Changes to the shared condition evaluator or action dispatch subsystem require review under the Wax contribution threshold, not the HiveAR threshold.

Control totals are declared and compared per currency, and no layout or gate adds amounts of different currencies.
