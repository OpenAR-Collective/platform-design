---
id: WAX-0029
title: "Tasking"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 29: Tasking

## Decision

Wax will provide a Tasking subsystem for human work: assigning, tracking, discussing, and completing units of work performed by people. A task is an event-sourced aggregate in its own right. Its lifecycle, creation, assignment, reassignment, status change, comment, linkage, and completion, is a stream of task events, and the operational task store that worklists and queues read from is a projection of those events. A task may reference an account or another aggregate, or none, but always has its own task identity.

## Not To Be Confused With the Schedulers

Tasking is the third of three scheduling-adjacent subsystems and the only one whose work is performed by a human. The Pending Event Register ([Wax Design Decision 27](WAX-0027-pending-event-register.md)) fires autonomous future-dated domain events. The Job Scheduler ([Wax Design Decision 28](WAX-0028-job-scheduler.md)) runs system-level jobs. The Tasking subsystem routes and tracks work that a person must do. A task may use the Pending Event Register for its own due-date timing, but the task itself is human work, not a machine-fired event or a system job.

## Why Tasks Are Event-Sourced

Tasks are event-sourced for the same reason domain facts are: the history must be trustworthy and queryable. The lifecycle of a task, who created it, who it was assigned to, who commented and what they said, when it escalated, and how it resolved, is exactly the kind of account narrative agencies reconstruct today from fuzzy free-text notes. As task events in core.event, that narrative is structured, attributed, timestamped, hash-chained, and queryable. The thread of comments is the task's event stream, so the back-and-forth between people is auditable by construction rather than by building a separate messaging log. Comment bodies that contain personal information sit in the same encryption envelopes as other payloads and are crypto-shreddable on the same terms, because a task is a standard aggregate and inherits the platform's encryption, retention, and integrity behavior uniformly.

Task volume is human-paced, so the cost of event-sourcing tasks is negligible against a chain that already carries every payment, contact, and status change. The uniformity is worth more than any selectivity would save: every task is recorded the same way, so no one consults a definition to learn whether a given task is in the record.

## The Task Aggregate

A task carries its own status lifecycle, open, in progress, blocked, completed, and cancelled, independent of any account or other aggregate status. Each transition is a task event. A task holds a title and a description, a set of classification tags, an optional due time, an optional reference to a related aggregate such as an account, and a participant set. The task accumulates a thread of comment events from any participant, in order, each attributed and timestamped.

## Participants and Roles

A task has participants with roles, in the shape of an email's from, to, and copied recipients rather than a single assignee field. A creator opens the task, one or more assignees are responsible for acting on it, and watchers are kept in the loop without owning the work. Each change to the participant set is a task event, so who was looped in and when is part of the auditable history. The participant model is generic at the Wax layer: a participant is a user. Which users may participate, including external client-portal users, is determined by HiveAR and the portals, which keeps cross-party tasking possible without baking portal specifics into the framework.

## Assignment: Push and Pull

Tasking supports both assignment models. A push assignment directs a task to a specific user. A pull assignment places a task in a shared queue from which an eligible user claims it. The claim uses the platform's standard SKIP LOCKED model, with one difference from the machine cases: the claim transaction is brief, grab the row, set the assignee, mark it claimed, and commit, so two users never claim the same task, and the resulting assignment lives in the task's state rather than as a held database lock. A human works a claimed task for as long as the work takes without holding any lock.

## Classification by Tags

Tasks are classified by multi-membership tags rather than a single type, consistent with the classification model used elsewhere in the platform. A task may carry several tags at once, such as a channel and a function, and worklist filtering, routing, and reporting operate over those tags. Because tags do not partition the way a single type would, a task counts under every tag it carries; routing resolution when a task's tags imply more than one queue, and reporting that treats tags as facets rather than as a partition, are workflow-rule concerns rather than properties of the tasking store itself.

## Timing, Routing, and Escalation Are Borrowed, Not Built

The Tasking subsystem deliberately contains no timer and no rules engine of its own. A task's due date is realized as a Pending Event Register entry; when that entry fires, a workflow evaluates whether the task is still open and applies the escalation policy. Routing and escalation policy live in the workflow engine and read task tags as conditions. Timing comes from the Register, policy from the workflow engine, and tasking stays a thin store of work and its history. Task lifecycle events are registered trigger types, so the workflow engine subscribes to task creation, completion, and other transitions exactly as it subscribes to any domain event.

## Task Links and Spin-Off Work

A task may reference other tasks through typed, directional links such as spawned-from, blocks, and relates-to. Each link is itself a task event, so the relationship is part of the auditable history rather than an informal note. In the interface, links render as navigable references: from one task a user jumps to a linked task and reads its closed thread. The most common pattern is spin-off work, where completing one task triggers a workflow that creates a follow-up task carrying a spawned-from link back to the task that produced it. The whole pattern is expressible with the existing workflow engine: task lifecycle events are triggers, create task is an existing action, and the link is a parameter that action sets.

## Account Domain Facts Emerge From the Work

Working a task produces domain facts on an account only when the work touches account state, and it does so through the normal command handlers, not through any task-specific mechanism. Requesting validation of debt, recording a contact, or instructing cancellation of a garnishment each lands on the account chain because a command was issued, while completing a purely internal task such as coaching an employee touches no account and produces no account event. The account record therefore fills with exactly the right domain facts and none of the operational churn, with no per-task configuration, because emission is emergent from whether the work touched account state.

## Attachments

A task attachment is a reference to a document in the shared document store, not a copy of the document held on the task. The same stored document may be referenced from the task, from the account, and from other aggregates at once, so the interface shows the attachment on the task and the identical document on the account because they are one stored object with several references. The document entity, the multi-aggregate referencing model, and the underlying storage mechanism are specified in the Document Storage Architecture decision. Tasking holds the pointer; the document store owns the bytes.

> **ILLUSTRATIVE WORKFLOW: VALIDATION OF DEBT, END TO END**
>
> **Step 1, request.
>
> **A workflow creates a task assigned to a client-portal user: provide validation of debt for this account. The task references the account, carries a debt-validation tag, and surfaces in the client portal.
>
> **Step 2, client responds.
>
> **The client completes the task in the portal and attaches the validation document. The attachment is a reference to the document store, and the same document is now referenced from the account as well.
>
> **Step 3, two events fire.
>
> **The task completion is recorded as a task event. Separately, validation of debt received lands on the account chain through the normal command handler, because real domain work occurred.
>
> **Step 4, the engine reacts.
>
> **The workflow engine, subscribed to the task completion trigger like any other event, runs a create task action and produces a new task assigned to the agent: review the validation and provide it to the consumer.
>
> **Step 5, the trail links itself.
>
> **The agent task carries a spawned-from link to the now-closed client task, navigable in the interface, and references the same validation document. Nothing in this flow required a feature built specifically for it: tasks, events, tags, links, the document store, and the generic workflow engine compose into it.

## Implementation Phasing

**Wax v2:** The task aggregate and event model, the operational task projection, status lifecycle, the participant set with roles, push and pull assignment, classification tags, task links, and the comment thread. Due-date timing through the Pending Event Register and escalation through the workflow engine. Tasking depends on the event-triggered workflow engine, which matures past the Wax v1 linear rule engine, so it is a v2 capability. Attachments land with the Document Storage Architecture decision.

**Breaking change risk: LOW. The operational task store is a projection rebuildable from the task events in core.event. Additional participant roles, link types, classification dimensions, and status values are additive. The attachment reference depends on the document store and is additive once that decision lands.**

## Implications For Contributors

Tasks are recorded as events. Task lifecycle changes flow through command handlers into core.event like any other aggregate, and the operational task store is a projection. No code path may mutate the task store directly without producing the corresponding task events.

Tasking borrows timing and policy. A module or contributor must not build a parallel timer or escalation engine inside tasking. Due dates use the Pending Event Register, and routing and escalation use the workflow engine reading task tags.

Attachments are references, never copies. A task stores a pointer to a document in the shared document store. The bytes are never copied onto the task, and the same document may be referenced by other aggregates concurrently.
