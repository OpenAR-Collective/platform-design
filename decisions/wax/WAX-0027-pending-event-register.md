---
id: WAX-0027
title: "Pending Event Register"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 27: Pending Event Register

## Decision

Wax will provide a Pending Event Register: an operational store of individual future-dated domain events scheduled against specific aggregates. Each entry names a target event type, the target aggregate key ring, optional parameter overrides, and a due time. When an entry comes due, the Register fires a fresh independent domain event, which then runs its own workflows. The scheduling and cancellation of entries are themselves recorded as events in core.event, and the Register is an operational projection built from those events.

## Not To Be Confused With the Job Scheduler

The Pending Event Register is paired with the Job Scheduler in [Wax Design Decision 28](WAX-0028-job-scheduler.md), and the two are easily conflated. The Pending Event Register schedules individual future-dated domain events aimed at a single aggregate, at the granularity of one account needing one action. The Job Scheduler runs system-level jobs that operate over scoped sets of rows or perform maintenance routines. The two share a wall-clock polling mechanism but are distinct subsystems with separate stores and separate operational views.

## Events as Truth, the Register as Projection

The decision to schedule a future event, and the decision to cancel one, are themselves events written to core.event and carried in the hash chain established in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md). The Pending Event Register is the operational projection of those events: the due-work store that worker instances claim from. The events are the record of truth, and the Register is the working set derived from them.

This split delivers a practical payoff beyond auditability. The history of what an account had scheduled, what fired, and what was cancelled and why becomes structured and queryable, in place of the free-text notes agencies rely on today to reconstruct that story. A query can then surface the gaps that notes never could: entries that were scheduled, never fired, and never cancelled, or cancellations with no preceding schedule.

## Register Entries

A Register entry carries the target event type, the target aggregate key ring, optional parameter overrides, a due time, and a status of pending, fired, or cancelled. The entry holds no condition predicate of its own. Whether the fired event does anything is decided by the workflows that run when it fires, not by logic stored on the entry.

## Firing

Worker instances claim due entries, those whose due time has passed, using SKIP LOCKED on a polling interval. Polling is the correct mechanism here rather than a latency compromise, because the Register waits on wall-clock time rather than on an event, so there is nothing to push a notification from. The broker wake-up pattern in [Wax Design Decision 24](WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md) does not apply. When an entry fires, it triggers a new independent domain event with no chain context inherited from the entry that scheduled it, consistent with the scheduled future event behavior in [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md). The fired event runs its own workflows and may schedule further entries of its own.

## Implicit No-Op

A fired event whose workflows find that conditions no longer warrant action simply does nothing. There is no separate predicate to re-check on the entry, because re-evaluation is just the ordinary workflow evaluation of the freshly fired event loading current state through its key ring. A reminder scheduled for an account that has since paid fires, finds the account paid, and takes no action. The Register deliberately stores no condition layer of its own, since duplicating the workflow engine's evaluation on the entry would be redundant and would risk drift between the two.

## Cancellation

A workflow may cancel pending entries through a cancel action with four breadths of targeting: a specific entry, all pending entries of a given event type for an aggregate, all pending entries in a classification group for an aggregate, and all pending entries for an aggregate regardless of type. The broader forms are resolved by query at fire time against the aggregate key the firing event already carries, so the firing event does not need to know which entries are pending in advance.

The classification-group form is the one that future-proofs cancellation. Because group membership is resolved at fire time, a new event type added later under the same group is automatically swept by an existing cancellation workflow with no edit. A consumer who sends a cease-and-desist limiting contact to telephone can have a single cancel-all-physical-mail workflow void every pending letter, including letter types introduced after the workflow was written. A cancellation is itself recorded in core.event, and it records both the predicate it ran and the specific entries it voided, so the trail shows exactly what was cancelled rather than only the instruction that was issued.

## Classification and the Shared Trigger Registry

Scheduled event types carry classification tags in the trigger registry defined in [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md). The tags are multi-membership, so a payment reminder letter can be tagged with both its function and its channel, and cancellation can target either dimension. The same registry serves both scheduling and cancellation: a single event type definition makes a type both schedulable as a future event and targetable by a cancellation, with no separate vocabulary of cancellable types to maintain alongside the firing ones. One registration grants both capabilities.

## Implementation Phasing

**Wax v2:** The Pending Event Register, the schedule future event action that writes to it, the four cancellation breadths, the implicit no-op behavior, and the classification tagging. Scheduling depends on the event-triggered workflow engine, which matures past the Wax v1 linear rule engine described in [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md), so the Register is a v2 capability.

**Breaking change risk: LOW. The Register is an operational projection rebuildable from the scheduling and cancellation events in core.event, so its schema can evolve without data loss. Additional cancellation breadths and classification dimensions are additive.**
