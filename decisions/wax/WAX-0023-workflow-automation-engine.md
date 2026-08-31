---
id: WAX-0023
title: "Workflow Automation Engine"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 23: Workflow Automation Engine

## Decision

Wax will include a user-configurable workflow automation engine. The engine supports two workflow types: event-triggered workflows and batch workflows. Event-triggered workflows execute in real time when a system event fires. Batch workflows iterate over a scoped table and execute against each qualifying row. Both types use a directed acyclic graph execution model within a single workflow definition, with event-scope-aware conditions and a pluggable action type architecture.

## Event Scopes

Every event type declares a scope: account, debtor, user, client, payment, legal case, payment arrangement, or other entity types defined by modules. The scope is not metadata. It is the structural boundary that determines which fields are available as conditions and which action categories are applicable. The workflow designer validates scope-action compatibility at definition time. A condition referencing client billing status cannot be added to a user-scope workflow. An action that updates account status is not offered for a user-scope workflow. The scope-action matrix is enforced by the designer UI and by the engine at runtime.

## The Two-Keyring Model

Every event type declares a key ring: a typed list of primary key references to the entities in scope. A payment_posted event declares account_pk, payment_pk, and user_pk. The condition engine loads the current state of those entities and all reachable related entities through declared foreign key relationships at evaluation time. A condition can therefore evaluate any field reachable through the key ring without the event payload needing to carry that data.

Every event carries two key rings. The pre_state_keys ring points to entity state before the triggering change. The post_state_keys ring points to entity state after the triggering change. For post-events, pre_state_keys resolves against the prior_value fields already stored in core.event by the enriched event sourcing architecture, and post_state_keys resolves against the current committed authoritative state tables. For pre-events, pre_state_keys resolves against the current authoritative state tables (which are the pre-change values) and post_state_keys resolves against a provisional state object constructed from the proposed write, held in a temporary evaluation context for the duration of the pre-event workflow execution.

Conditions are always expressed as key ring traversal. For example: post_state.account.current_balance, or pre_state.address.postal_code. The engine resolves these consistently regardless of whether the value comes from committed database state or a provisional context. This means conditions are written identically for pre and post events, which is a significant contributor-friendliness benefit.

The event payload may also carry event-specific properties, for example an address_changed event carries the full before and after address fields directly. These are redundant with what is reachable through the key ring but are provided as a convenience. The payload is the permanent audit record. The key rings are the condition evaluation interface. Both surfaces expose the same values through different access paths.

## Pre-Events and Post-Events

Many system actions have a pre-event and a post-event. The pre-event fires before the write is committed to the database. The post-event fires after the write succeeds. Pre-events are synchronous interceptors: the proposed write is held pending the outcome of all pre-event workflows. Post-events are asynchronous notifications: the write has already succeeded and post-event workflows cannot reverse it.

Event granularity is at the transaction boundary, not the field boundary. When a user saves changes to an address and two phone numbers, the system fires one address-change event and two phone-change events, one per distinct entity changed. The GUI assists with this through visual field grouping: address fields are in a distinct frame from phone fields, and saving is triggered by navigating away from a field group rather than by a single save button. The user experience is that they change what needs changing and receive immediate inline feedback per entity group if a pre-event rejects or modifies the proposed change.

## Pre-Event Workflow Outcomes

A pre-event workflow has three possible outcomes. Accept means proceed with the proposed change as submitted. Reject means block the change entirely, return a configurable error message, and optionally record an audit event of the rejection. Modify means proceed with a transformed version of the proposed change: the workflow modifies the post_state_keys provisional context before the write commits, and the write proceeds with the modified values. Modify is the correct mechanism for use cases like address standardization, where the workflow calls an external API and applies the normalized result before the original proposed change is persisted.

## Rejection Propagation

When a pre-event rejects a write that was initiated by a workflow action (rather than a human), the rejection propagates back to the post-action handler of the calling workflow as a structured error. The parent workflow routes to its configured failure path for that action. Action declarations include an on_failure behavior: continue, halt, or log-and-continue. This is a required configuration field on any action that can trigger pre-events, so administrators must consciously choose failure handling rather than relying on a default.

## DAG Execution Model and Cross-Workflow Chains

Within a single workflow definition, the execution model is a directed acyclic graph. The designer tool enforces acyclicity: backward connections that would create a cycle within the definition are not permitted. The graph supports divergence (branching on conditions), convergence (merging branches), per-action result routing (dedicated success and failure paths from every action node), and AND or OR join semantics at merge points. An AND join requires all upstream branches to arrive before proceeding. An OR join proceeds when any upstream branch arrives.

Across workflow definitions, cycles are possible by nature: a workflow action can issue a command that produces an event that triggers another workflow. The engine cannot prevent this at definition time. An execution chain context travels with each event as it propagates. The chain context records the root event, every event in the chain, and the depth. Before evaluating definitions against an event, the engine checks whether the same event type on the same entity primary key has already appeared in the current chain. If it has, the engine logs a cycle detection warning and terminates that branch. Chain depth is bounded by a configurable maximum as a backstop against non-obvious cycles.

## Downstream Workflow Suppression

A workflow action can instruct the engine to suppress downstream workflow evaluation for the events it produces. The suppression flag is set on the event record and tells the workflow engine not to evaluate definitions against that event. The event is still written to core.event with full enriched payload. Read model projections, reporting, and all other systems process it normally. Only workflow evaluation is suppressed. This is distinct from suppressing the event itself, which is never permitted: the audit record in core.event is always written.

## Pluggable Action Type Architecture

The workflow engine defines an action type interface in C#. Any class implementing the interface is a valid action type. Wax ships with a built-in library. Modules and Packs contribute additional action types. Power users with C# skills may implement and install their own local action types. A LexisNexis address scrubbing action type shipped as a Pack, for example, handles all communication with the LexisNexis endpoint, parses the response, and populates declared output schema fields that are then available as downstream conditions in the workflow designer.

> **ACTION TYPE INTERFACE DECLARATION**
>
> **Input schema**: the typed fields the action accepts from the upstream key ring and payload. The workflow designer presents a field mapping UI for each input.
>
> **Output schema**: the typed fields the action exposes to downstream conditions and actions. Declared as a structured schema so the condition builder can navigate response fields the same way it navigates entity fields.
>
> **Blocking capability flag**: whether synchronous blocking execution is supported. A blocking action holds the workflow pending its completion, within a configurable timeout. Non-blocking actions fire and the workflow continues.
>
> **Retry capability flag**: whether retry with configurable attempt count and inter-attempt delay is supported.
>
> **Pre-event eligibility flag**: whether the action is valid in a pre-event workflow. Reject and modify-provisional-state are pre-event only. Most other actions are post-event only or both.
>
> **GUI-required flag**: whether an active GUI session is required. GUI-required actions are skipped silently when the triggering event was not GUI-initiated.
>
> **External side effects flag**: whether the action triggers state changes in an external system even when HiveAR does not write to its own database. Prominently surfaced in the designer and in test mode.
>
> **Timeout configuration**: for blocking actions, the maximum wait time before routing to the failure path.
>
> **Has_retry_with_wait**: retry handling is internal to the action. Retry count and inter-attempt delay are properties of the action configuration, not graph cycles.

Custom action types installed by power users bypass the Collective's quality and security review. A custom C# action can do anything C# can do: arbitrary database queries, external API calls, file system operations. This is a deliberate extensibility feature and a deliberate risk. The installation UI prominently warns that custom action types are the installing agency's full responsibility. A sandboxed execution mode for custom action types is a named future goal for future consideration.

## Condition Builder: Field Picker and Query Builder

The condition builder offers two modes. The field picker is the default and is appropriate for most administrators. It presents a navigable tree of fields reachable from the event's key rings: pre_state and post_state entities and their related entities through declared foreign key relationships. Selecting a leaf field presents appropriate operators and value inputs based on the field type. A decimal field offers greater than, less than, and equals. A reference value field offers is one of and is not one of with a populated dropdown. A date field offers before, after, and within the last N days.

The query builder is an advanced mode for users with SQL familiarity who need to express conditions the field picker cannot represent. It exposes a governed expression language constrained to the reachable schema: field references, condition logic, and relationship traversal. It does not allow arbitrary SQL. Expressions are validated against the declared schema before saving. Both modes produce the same internal condition representation. A condition built in the field picker is viewable in the query builder as its expression equivalent. Switching from query builder to field picker is offered only when the expression can be fully represented in picker form.

## Workflow State Toggles

Every event-triggered workflow definition has three state toggles that govern its behavior in the live environment.

> **THE THREE TOGGLES**
>
> **Attached (on/off)**: controls whether the workflow fires when its trigger event fires in the live system. A newly created workflow is unattached by default. The designer builds, tests, and validates the workflow in an unattached state. Toggling Attached to on is the deployment action. An unattached workflow never fires regardless of other toggle states.
>
> **Test mode (on/off)**: when on, all actions suppress their side effects. Database write actions are skipped and their would-be output is recorded to the test audit trail. API call actions execute normally unless marked as having external side effects, which are surfaced with a warning. Communication actions are skipped. Schedule future event actions are skipped. Downstream workflow evaluation fires in test mode as well, preserving the full chain in test context. When Test mode is on, Detailed Auditing is forced on regardless of its individual setting.
>
> **Detailed Auditing (on/off, default off)**: writes the full execution narrative alongside normal execution. Records every condition resolved and its evaluated value, every branch taken and why, every action parameter, every API response evaluated. Can be toggled independently of Test mode for production diagnostic purposes, such as validating a newly deployed workflow against live traffic.

The meaningful execution states combine these toggles. Unattached with Test mode on supports ad hoc test execution where the designer picks a specific record by PK, the engine constructs the key ring from real current data, and executes the full workflow in test context with a complete test audit trail. Attached with Test mode on is Attached test mode: the workflow fires on real live events from now on, but all actions are suppressed. The designer observes how the workflow behaves against real traffic without consequences. Attached with Test mode off is live production execution.

## Execution Chain Context and Provenance

When a workflow action issues a command that produces an event, that event carries the execution chain context forward. The chain context is a structured provenance record that accumulates as the chain progresses. Each event in a chain carries a root_event_pk pointing to the originating event, a parent_event_pk pointing to the immediate predecessor, a chain depth counter, and a chain_context JSON field that accumulates contributor labels from each step. The final event in a chain can carry a reason code that reflects all contributors that led to it.

The chain context is read-only within a workflow. Conditions may evaluate chain context fields (is the root event from a portal session? does the chain already include a standardization step?) but actions cannot modify the chain context directly. The engine appends to it automatically.

## Event Type Registry

Every trigger that can be used to initiate a workflow evaluation is registered in the event type registry. The registry is the catalog from which the workflow designer populates its trigger selection interface. A trigger that is not in the registry cannot be selected in the designer. Module authors who want their domain event types available as workflow triggers must register them as part of their module contract.

The trigger unit is the event_type string on a domain event row, or a named non-domain trigger such as a scheduler entry or an API call type. A workflow that fires on contact.phone_corrected evaluates whenever a domain event with that event_type is written to core.event. Payload-level filtering, such as only firing when the corrected number is in a specific area code, belongs in workflow conditions, not in the trigger definition. This keeps the registry clean and puts filtering logic in the workflow graph where it is inspectable and testable.

> **EVENT TYPE REGISTRY FIELDS**
>
> **event_type_code**: The namespaced string identifier (e.g., contact.phone_corrected, account.placed). Unique across the registry. Matches the event_type value written to core.event for domain event triggers. Non-domain triggers use a reserved namespace: scheduler.nightly_run, api.inbound_request.
>
> **owning_module**: The module that defined this event type. Core-defined types carry the module identifier 'core'. Module-defined types carry that module's identifier. The owning module is responsible for maintaining the registry entry when its event type schema changes.
>
> **category and subcategory**: Hierarchical classification for catalog browsing and search. Example categories: Account Lifecycle, Entity Demographics, Payment, Communication, System. Subcategories provide a second level within each category. The category taxonomy is owned by Core and extended by modules through the module contract.
>
> **display_label_fk**: Foreign key to the i18n translation table. The label shown in the designer UI trigger picker. Follows the full i18n architecture: no English strings stored directly in the registry.
>
> **description_fk**: Foreign key to the i18n translation table. A plain-language description of what this trigger fires on, shown in the designer and in catalog search results.
>
> **trigger_source**: domain_event, scheduler, or api_call. Indicates the origin of the trigger signal. Domain event triggers fire when a matching core.event row is written. Scheduler triggers fire on a configured schedule. API call triggers fire when a designated inbound API endpoint is invoked.
>
> **is_pre_event_eligible**: Boolean. Whether this trigger can be used in a pre-event workflow. Pre-event workflows are synchronous interceptors that can abort the triggering command. Not all trigger sources support pre-event evaluation.
>
> **is_system_trigger**: Boolean. Whether this is a Core-internal trigger used by system workflows. System triggers are visible to administrators with the show system workflows privilege and are excluded from the standard designer picker by default.
>
> **property_payload_schema**: The typed schema of fields available to workflow conditions and actions when this trigger fires. Declared as a structured schema so the condition builder can present field navigation for the specific event type without requiring the workflow author to know the raw jsonb structure.

The category taxonomy is the primary navigation structure for the catalog. Categories group related trigger types so a workflow author looking for account lifecycle triggers does not need to scroll through contact, payment, and communication types to find them. Search operates across event_type_code, display label, description, category, and subcategory. A workflow author can search for 'phone' and receive contact.phone_corrected, contact.phone_added, contact.phone_voided, and any module-contributed phone-related event types registered under the same search surface.

The registry also answers provenance questions in the audit trail. When a compliance officer asks 'what workflow fired when this account was placed?' the workflow execution log carries the trigger event_type and the workflow definition version. The registry entry for that event_type identifies the owning module, category, and description, making the audit trail self-describing without requiring the reader to know the platform internals.

## Scheduled Future Events

Workflows execute in real time and complete in fractions of a second. There are no waiting states within a workflow. Any deferred or scheduled action is handled by a schedule future event action type that writes an entry to the Pending Event Register ([Wax Design Decision 27](WAX-0027-pending-event-register.md)): a future-dated entry with a target event type, target entity key ring, and parameter overrides. When the scheduler fires at the designated time, it triggers a new independent event with no chain context inherited from the originating workflow. The new event may invoke its own workflows. Scheduled actions are not continuations of the originating workflow.

## Batch Workflows

A batch workflow is a distinct workflow type with no trigger event. Instead of firing on an event, it iterates over a scoped set of rows in a target table and executes the workflow definition against each row. Each row is a discrete execution unit with its own condition evaluation, branch decisions, and success and failure paths. The batch workflow declaration specifies the target table and the available scope dimensions: the indexed columns and declared foreign keys that are sensible as scope selectors.

The scope selection is provided at runtime rather than baked into the workflow definition. The caller supplies a scope selection expression using the same field picker and query builder interface used for workflow conditions, constrained to the target table and its directly reachable relationships. The engine pushes the scope selection down to a parameterized WHERE clause against the target table so only qualifying rows are loaded. Multi-select is natural: the scope selection can express any combination of conditions. Named scope presets can be saved on the batch workflow definition for common run patterns and referenced by name in job scheduler entries or API calls.

Batch workflows can be triggered in four ways: manually from the designer with record and scope selection, via the Job Scheduler ([Wax Design Decision 28](WAX-0028-job-scheduler.md)) with a configured schedule and runtime scope, via an API call with scope parameters in the request body, or by another workflow as a schedule batch job action. Long-running batches execute as background jobs. The job scheduler table tracks run status, start time, rows processed, rows succeeded, rows failed, and current progress. Batch runs support pause and resume: the engine checkpoints position in the iteration so a paused or interrupted batch can resume without reprocessing completed rows.

Batch workflows support the same three state toggles as event-triggered workflows, with the exception that Attached is not applicable. Test mode and Detailed Auditing operate identically. An ad hoc test run of a batch workflow executes against the scoped row set in test context with no writes. A live run in Test mode processes all qualifying rows with actions suppressed.

## Implementation Phasing

**Wax v1 (MVP):** Linear rule engine only. This is the single biggest scope reduction in the roadmap. Ship post-event rules only (when X happens, do Y). Linear execution: one trigger, one condition, one action. No pre-event interception, no provisional state, no rejection propagation, no DAG. Fixed action types: change status, send notification, assign to queue, update field, create task. No batch workflows. No workflow designer UI; rules configured through a simple admin form. System workflows (balance recalculation on payment, etc.) implemented as event handlers in code, not configurable workflows.

Critical v1 requirements: the event type registry must exist (every event type declares its scope); workflow execution must produce events through normal command handlers (no shortcuts bypassing the event pipeline); the workflow definition schema should be forward-compatible (store v1 rules in core.workflow_definition with a nullable graph_json column for v2 DAG data).

**Wax v2:** DAG execution within single workflow definitions. Pre-event and post-event support. Pluggable action type interface (C# interface). Two-keyring condition resolution. Rejection propagation. Workflow designer UI (visual graph builder). Batch workflows. Workflow state toggles.

**Wax v3+:** Cross-workflow chain detection and cycle prevention. Downstream workflow suppression. Execution chain context and provenance. Scheduled future events with re-evaluation. Workflow provenance and version tracking (clone-and-override model).

**Breaking change risk: MEDIUM.** The critical investments are the event type registry and the discipline of routing all workflow-initiated changes through command handlers. If v1 takes shortcuts (direct SQL updates from rules), the v2 engine cannot trust the event history.

## Implications For Contributors

The workflow engine subscribes to the event stream through the same subscription mechanism as read model projections. It does not have privileged access to the event pipeline.

All state changes produced by workflow actions must pass through normal command handlers. Workflow actions may not directly mutate authoritative state tables.

Every event produced as a result of a workflow action carries the execution chain context including root_event_pk, parent_event_pk, and chain depth. The engine uses chain context for cycle detection.

Module authors who want their events available as workflow triggers must register those event types in the workflow event type registry as part of their module contract, including scope declaration, key ring definition, pre/post designation, GUI-initiatable flag, and property payload schema.

Module authors who contribute action types must implement the action type interface fully, including all required capability flags, input and output schema declarations, and test mode behavior. An action type that does not correctly implement test mode suppression will be rejected from the repository.

Custom action types installed locally are the installing agency's responsibility and bypass Collective review. The designer UI must clearly communicate this at installation time.

## Workflow Provenance and System Workflow Visibility

Workflows in Wax carry a source type: Wax-delivered, Seed Pack-delivered, or User-defined. Wax-delivered workflows are the nuts-and-bolts system operations: updating aggregate balance fields when a payment posts, updating is_active when an account closes, detecting orphaned sets when an account leaves. These workflows are hidden by default from the workflow designer UI. An administrator with an explicit RBAC privilege and a 'show system workflows' toggle can view them. They may be modified (it is OSS) but the UI makes clear that modification of system workflows affects platform integrity.

The workflow definition record carries source_type (core, seed_pack, or user) and source_identifier (the contributing pack, for pack-delivered workflows). These fields establish the origin of a workflow definition. The full clone-and-override provenance model, including source_workflow_version_fk and the immutable clone entry in the version history table, is described in the Workflow Provenance and Version Tracking section below.

## Terminology: Domain Events, Triggers, and Workflow Executions

Three distinct concepts share the word "event" in workflow engine literature. Wax uses precise terminology to keep them separate, because conflating them leads to architectural confusion for contributors trying to understand what lives where.

**Domain event. **A row in core.event. A recorded, immutable fact about a state change to an aggregate. Every row has a before value, an after value, an actor, a timestamp, and a reason. Domain events are the permanent audit record. They are described fully in [Wax Design Decision 1](WAX-0001-enriched-event-sourcing.md). The word "event" used without qualification in this document always means a domain event.

**Trigger. **A signal that causes the workflow engine to evaluate one or more workflow definitions. Triggers may originate from a domain event (when a domain event is written, its event_type becomes a trigger signal), from the scheduler (a named trigger fires on a configured schedule), from an inbound API call, or from a workflow action that fires a downstream trigger. Triggers are not stored in core.event. They are signals, not records of state change. The phrase "when a trigger fires" throughout this decision refers to this concept.

**Workflow execution. **One instance of a workflow definition being evaluated against a specific trigger. Each execution produces a record in the workflow execution log, references the trigger, and records the outcome. Domain events produced during an execution reference the execution via correlation_pk_ref with correlation_type = 'workflow_execution'.

## Wax-Delivered Workflows and the Clone-and-Override Model

Wax ships a set of structural workflows that implement the platform's own operational logic: nightly user inactivity checks, orphan detection on account sets, key retention scheduling, aggregate balance maintenance, and similar. These are real workflow definitions that run through the same engine as agency-defined workflows. They are not hardcoded logic paths. An administrator with the appropriate RBAC privilege can enable a "show system workflows" view in the designer and inspect exactly what Wax does and why.

Wax-delivered workflows are read-only in their delivered form. The agency cannot edit the Wax section of the catalog directly. To customize the behavior of a Wax-delivered workflow, the agency clones it. The clone lives in the Custom section of the catalog. The agency attaches the clone and detaches the Wax original. The Wax original remains present, visible, and reactivatable at any time. The override relationship is visible in both directions: the Wax entry shows which Custom workflow overrides it, and the Custom entry shows which Wax workflow it was cloned from.

The same clone-and-override model applies to module-delivered workflows. A module's workflows live in that module's section of the catalog, read-only. Clones live in Custom. The module's original is never modified and always reflects what the module actually delivers.

> **TRANSPARENCY AS A DESIGN PRINCIPLE**
>
> The platform cannot prevent modification of source code. HiveAR is open-source software. Every agency that deploys it has the full source. A technically sophisticated actor could modify the WSM, recompile it, or alter Core workflow definitions at the database level. No technical restriction closes this gap completely for an actor who controls their own deployment. The correct response is to make the legitimate path easy. The clone-and-override model gives agencies full flexibility to customize any Core or module behavior through supported, audited, documented means. An agency that can achieve what they need through cloning has no reason to work around the system. Working around the system requires significant effort, leaves no legitimate audit trail, and forfeits the support relationship. The benefit is never worth the cost. The platform earns trust by being transparent, not by being locked down. Full visibility into system behavior is a feature. An agency that can read the Core workflow for user inactivity deactivation understands exactly what the platform does to their user accounts. That understanding builds confidence. It also means any misconfigured or misbehaving workflow is discoverable by the agency without requiring Collective intervention. Transparency serves both parties.

## Configuration-Parameterized Workflows

Wax-delivered workflows that implement agency-configurable behavior read their parameters from agency-controlled configuration values at evaluation time rather than from hardcoded constants in the workflow graph. This is the pattern that allows standard system behavior to be controlled from the appropriate configuration surface without requiring the agency to clone and edit the workflow.

The user inactivity deactivation workflow illustrates the pattern. The workflow fires nightly. Its conditions evaluate two configuration values read from the user record: inactivity_deactivation_enabled and inactivity_threshold_days. If the flag is false for a user, the condition is not met and the workflow produces no action for that user. If the flag is true and the threshold has been exceeded, the deactivation action fires. The agency controls the behavior by editing the user record, not by editing the workflow. A system-wide default for the threshold is held in a system configuration table; the per-user value overrides it when set.

Configuration values that parameterize workflow behavior are governed by the versioned configuration architecture from [Wax Design Decision 21](WAX-0021-configuration-management-and-environment-lifecycle.md). Changes to these values are tracked, exportable, and promotable between environments. The workflow graph itself does not change when the agency adjusts a threshold. The separation between the workflow definition and the values it reads is deliberate: it keeps the workflow catalog clean and puts configuration where operators expect to find it.

## Workflow Execution Log

Every trigger evaluation produces a record in the workflow execution log regardless of outcome. The execution log is separate from core.event. It records operational facts about the workflow engine's activity; core.event records facts about domain state changes. These are different things and must not be mixed.

> **WORKFLOW EXECUTION LOG: MINIMAL RECORD (ALWAYS WRITTEN)**
>
> **trigger_type**: domain_event, scheduler, api_call, or workflow_action.
>
> **trigger_reference_pk**: the PK of the triggering record (the domain event row, the scheduler task row, etc.).
>
> **workflow_definition_version_fk**: FK to the specific version history row of the workflow definition that evaluated. Carries both the definition identity and the version at execution time.
>
> **affected_aggregate_pk and affected_aggregate_type**: the aggregate this execution concerned. Required even for no-op and abort executions, because these records must be queryable by aggregate without a core.event anchor.
>
> **outcome**: completed, aborted, or no_op.
>
> **executed_at**: UTC timestamp of evaluation.

Detailed auditing adds a full execution trace to a supplemental table keyed to the execution log row. The trace records every condition evaluated and its resolved value, every branch taken and why, every action parameter, and every external response. The trace lives in a separate table rather than as a jsonb payload on the execution row so that it can be purged independently on a shorter retention schedule without touching the execution record.

## Workflow Execution Log Retention

The retention obligation of a workflow execution row is determined by whether any core.event row references it via correlation_pk_ref. The purge job checks this before deleting any candidate row. A referenced row is ineligible for purge regardless of age.

| **Execution type** | **Referenced by core.event** | **Purgeable** | **Retention rule** |
| --- | --- | --- | --- |
| Produced domain event(s) | Yes | No | Permanent (core.event is permanent; execution record must remain valid as the correlation target) |
| Abort (blocked a command) | No | Yes | Configurable; longer minimum recommended. The abort record explains why no domain event exists. Queryable by aggregate PK. |
| No-op (conditions not met) | No | Yes | Configurable; short. Purely operational. Bulk of execution volume. |
| Trace records (any execution) | No | Yes | Configurable; shortest. Diagnostic only. Independent of execution record retention. |

Abort records carry a special requirement: they must be queryable by affected_aggregate_pk. When a compliance officer asks why no domain event exists for a command that a collector reported submitting, the abort record in the execution log is the answer. It must remain findable by the aggregate it concerned for the duration of its retention window, independent of any core.event anchor.

## Workflow Provenance and Version Tracking

The existing provenance model (source_type: core, seed_pack, or user; source_identifier recording the contributing pack) is extended to support the full clone-and-override model. The workflow definition version history table is the authoritative provenance record.

**source_workflow_version_fk. **When a workflow definition is created by cloning an existing definition, this field on the new definition record points to the specific version history row of the source. A single FK to a version history row carries both the source definition identity and the version that was cloned, with no redundancy. Null for original definitions.

The version history entry created at clone time is system-generated and immutable. It reads: "Cloned from [Wax / module name] workflow '[name]' version [N] on [date] by [actor]." This entry cannot be edited or deleted. Subsequent entries record agency changes from that point forward. The same mechanism applies when an agency clones one of their own workflow definitions: the source version is recorded at clone time and the change history of the clone is independent from that point.

The catalog organizes workflow definitions by ownership. Wax-delivered workflows live in the Wax section. Module-delivered workflows live in their module's section. All clones, regardless of what they were cloned from, live in the Custom section. A Wax entry that has been overridden displays the name of the overriding Custom workflow. A Custom entry that overrides a Wax or module workflow displays its source. The override relationship is visible and navigable in both directions.
