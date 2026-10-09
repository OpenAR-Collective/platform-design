---
id: HIVE-0003
title: "Demographic History, Golden Record, and Contact Intelligence"
status: Accepted
version: 1.0
area: hivear
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# HiveAR Design Decision 3: Demographic History, Golden Record, and Contact Intelligence

## Decision

HiveAR maintains a complete history of every demographic value ever received for an entity, organized in separate tables per attribute type. Every instance is permanently stored with its source, recency date, composite score, and current tier. A confidence scoring engine incorporating source reliability, recency, frequency of corroboration, and contact outcome history determines which value in each attribute type achieves Gold status. Silver values are valid and contactable. Void values are known bad or severely demoted. Gold/Silver/Void tiering drives contactability rankings, which power dialer campaigns, dynamic work queues, and best-contact selection. All decay and scoring updates are driven by events and workflows.

## Design Philosophy: Collect Everything, Surface the Best

Incumbent collection systems typically store one address, one phone, and one SSN per debtor. When new data arrives, the old value is overwritten. No history is retained. This means a skip trace result that turned out to be wrong cannot be recovered from. It means an agency receiving a demographics update cannot see whether the incoming data is better or worse than what they already have. It means a regulatory dispute about what address was on file at a given time cannot be resolved.

HiveAR takes the opposite approach. Every demographic value ever received is stored permanently with full provenance. Nothing is overwritten. The question of which value is the best current representation of ground truth is answered by the confidence scoring engine, not by the order in which data arrived. An older, highly corroborated address from a reliable source outranks a newer, unverified address from a low-trust source. The agent sees both, understands why one is ranked higher, and can act on that understanding.

## Demographic History Tables

Demographic history is organized in separate tables per attribute type rather than a single unified table. A single table with a type discriminator produces awkward schema: an address has very different fields from a phone number, and forcing both into the same row structure requires many nullable columns. Separate tables per attribute type produce clean, queryable schemas with appropriate indexes and constraints for each type.

> **ATTRIBUTE TYPE TABLES**
>
> **entity_name_history**: name component values by locale. Each row represents one name instance as received from one source. Fields vary by Locale Module (given_name, family_name, etc. for US; primary_name for single-name cultures; and so on). The table carries the locale identifier to distinguish US name records from Philippines name records for the same entity.
>
> **entity_address_history**: address values. Fields vary by Locale Module satellite schema. A US address row carries addr1, addr2, city, state_code, postal_code, county. A Philippines address row carries street, barangay, municipality_city, province, region, postal_code. Both coexist in the same table under different locale identifiers.
>
> **entity_phone_history**: phone numbers. Fields: e164_formatted_number (canonical format), display_number, phone_type (mobile, landline, voip, unknown), locale identifier.
>
> **entity_email_history**: email addresses. Fields: email_address, is_valid_format.
>
> **entity_tax_id_history**: national identity and tax identification numbers. Fields: id_type (ssn, ein, itin, tin, umid, and others declared by Locale Modules), id_value (PII-encrypted), locale identifier.
>
> **entity_birth_date_history**: dates of birth. Fields: birth_date (PII).
>
> **entity_employer_history**: employment records. Fields: employer_entity_fk (if the employer is also an entity in the system), employer_name_freeform, job_title, employment_status.

Every row in every attribute history table carries: entity_fk, source_type_fk (client, skip_trace_vendor, credit_bureau, agency_verified, consumer_provided, court_record, and others), source_identifier (which specific client or vendor), recency_date (from the source file or defaulted to load date), load_batch_fk (which import batch introduced this record), account_fk (which account it arrived with, if applicable), current_composite_score, tier (gold, silver, or void), bad_flag, bad_flag_actor_fk, bad_flagged_at, and standard created_at, updated_at audit fields.

## Four Scoring Dimensions

The composite score for each demographic instance is computed from four independent dimensions. Each dimension contributes a component score. The composite is a weighted combination of the four components. Weights are configurable per installation within ranges established by the Collective.

> **SCORING DIMENSIONS**
>
> **Source reliability weight**: the agency assigns a trust score to each source type. A credit bureau pull is typically weighted higher than a client-provided value. A skip trace vendor is in between. Agency-verified data (confirmed by a collector in a right party contact) may be the highest weight of all. Source type weights are configuration, not code, and are organization-scoped.
>
> **Recency**: more recent data scores higher within the same source reliability tier. A phone number received last month from a mid-tier source may outrank a phone number received three years ago from a high-tier source if the recency gap is large enough. Recency scoring applies a configurable time-decay function to the recency_date field.
>
> **Frequency of corroboration**: when multiple independent sources provide the same value, the frequency count adds to the score. Two mid-tier sources agreeing on an address can collectively outrank a single high-tier source providing a different address. Corroboration is detected by value matching within a configurable similarity threshold per attribute type.
>
> **Contact outcome**: successful contact through a channel boosts the score of the demographic value used. Failed contact attempts progressively degrade the score. This dimension is dynamic: it changes as new contact attempts are recorded and as time passes without successful contact.

## Completeness as a Hard Gate

Completeness validation is declared by Locale Modules per attribute type and returns a Boolean. A demographic value that fails completeness validation is ineligible for Gold or Silver status regardless of its composite score on the four dimensions. Incomplete values are stored in history and remain visible to agents, but the tier field is set to void-incomplete to distinguish them from bad-flagged void values.

The principle is: a complete older record is better than an incomplete newer one. An address missing its street number, a phone number with too few digits, or a name with only a last name and no given name are all practically useless for contact purposes even if they arrived recently from a high-trust source. Completeness is a prerequisite for usefulness.

Locale Modules declare completeness validators as part of the module contract. The US Locale Module declares that a US address requires at minimum addr1, city, state_code, and postal_code. Middle name and suffix are not required for a US name to be complete. Other locales declare their own rules. Wax calls the relevant Locale Module's completeness validator when scoring an attribute instance. If no Locale Module declares a completeness validator for a given attribute type and locale, Core defaults to non-empty as the completeness criterion.

The exception to the completeness gate is: it is better to have an incomplete golden record than no golden record at all. If all available values for an attribute type fail completeness validation, the highest-scoring incomplete value is promoted to Gold with a completeness warning flag. The agent is shown the warning and understands that the best available data for this attribute is incomplete.

## Gold, Silver, and Void Tiering

Tiering determines how demographic values are used for contact, display, and reporting. The semantics differ between attribute types that are inherently one-to-one with a person and those that are naturally many-to-one.

For one-to-one attributes, meaning attributes where a person has only one authoritative value at a time: name, SSN, date of birth. Gold is the single best-scoring complete value. Silver values are credible alternatives that did not rank highest but remain plausible (a maiden name on record, an SSN variant suggesting a generational suffix). Void values are bad-flagged or fail completeness. Only one Gold value exists per attribute type per entity at any time.

For many-to-one attributes, meaning attributes where a person legitimately has multiple valid values simultaneously: phones, addresses, emails, employers. Gold is the best-scoring complete value, the primary contact method for that attribute type. Silver values are additional valid values that warrant contact attempts. An entity may have one Gold phone, three Silver phones, and two Void phones. Contact campaigns attempt Gold first, then Silver in score order. Void values are not contacted. This distinction means there is no ambiguity: gold is the best, silver is valid and contactable, void is known bad or unusable.

## Contact Outcome Scoring

Contact outcomes are the most dynamic scoring dimension because they change as collection activity proceeds. Outcomes are recorded as events in core.event through the normal command handler path and trigger workflow-driven score updates on the demographic values involved.

> **CONTACT OUTCOME EFFECTS BY CHANNEL**
>
> **Right party contact (RPC) via phone**: major confidence boost applied to the phone number used. The boost persists but decays gradually with subsequent failed attempts. An RPC from eighteen months ago with forty failed attempts since scores lower than an RPC from three months ago with ten failed attempts.
>
> **No answer**: gradual confidence decay on the phone number attempted. The decay rate is configurable. Repeated no-answers over a long period degrade confidence significantly even without a hard negative signal.
>
> **Disconnected or invalid number**: severe demotion, equivalent to a bad flag. The phone number moves to void tier.
>
> **Unreturned letter (address)**: a positive signal when no return mail is received within the NCOA response window. Lends confidence to the address.
>
> **NCOA hit**: informative but not negative. The old address was valid at some point but the person has moved. The old address is demoted. The forwarding address, if present, is a new address history instance from a postal source type.
>
> **Returned mail (nixie)**: negative signal, demotes the address. A returned mail with a change-of-address sticker is both a negative on the old address and a new demographic instance for the new address.
>
> **Email delivered and opened**: strong positive signal for the email address.
>
> **Email bounce**: severe demotion for the email address.
>
> **Text delivered and replied**: strong positive signal for the phone number as a text-capable line.
>
> **Text undelivered**: negative signal. Carrier-level invalid responses are severe demotions.

An elegant outcome of contact outcome decay is natural contact method rotation. As the best phone number decays from repeated no-answers, a previously untried silver phone climbs in relative score and eventually becomes the gold phone. An agency dialing only the gold number at any given time will naturally rotate through available phone numbers without any manual intervention or campaign configuration changes.

## Confidence Decay and the Maintenance Event Architecture

Confidence decay is handled through two mechanisms working together. Event-triggered decay fires immediately when a contact outcome event is recorded. A returned mail event, a disconnected phone recording, or a failed text delivery fires through the event and workflow engine, which applies the appropriate decay function to the demographic value involved.

Periodic decay for time-based degradation is handled through the configurable maintenance event system. The agency configures maintenance events with a name, a scope (a query defining which demographic records to target), and a frequency. The standard seed pack delivers pre-built maintenance event definitions and corresponding workflows: a nightly event firing on all active phone records, with a delivered workflow that catches the event and applies a small time-decay function to each phone's confidence score. Agencies may accept the seed pack defaults, modify the decay parameters, or define entirely custom maintenance schedules.

This architecture is intentional. Periodic decay is not a special subsystem. It is a specific application of the workflow engine's batch capability to demographic scoring. The same event and workflow infrastructure that drives all other system automation drives demographic score maintenance. Agencies understand how to configure it because it uses the same tools they use for everything else.

## Contactability as a Derived Output

Contactability is not a stored field on the entity record. It is a derived ranking produced on demand by querying the demographic history tables and applying the current scoring state. For a given entity, contactability produces: best phone to call (highest Gold or Silver phone by composite score), best phone to text (which may differ if cellular versus landline is tracked), best address for mail, and best email.

Contact pools are dynamically computed sets of contact methods across a population of entities or accounts, ranked by contactability score. A dialer campaign specifies a population scope (all active accounts for client XYZ in payment arrangement status) and a contact method type (phone). The pool computation queries the demographic history tables for all entities associated with those accounts, ranks available phone numbers by composite score, and returns a prioritized contact list. The pool updates continuously as new contact outcomes are recorded and scores change.

Dynamic work queues for agents working accounts manually are a direct extension of contact intelligence. A queue sorted by highest contactability ranking presents accounts where the best available phone or address is most likely to produce successful contact. An agent working from a contactability-sorted queue naturally calls the best numbers first without needing to know the underlying scoring mechanics.

## Agent Visibility and Bad Flagging

For any demographic value currently in Gold status, an agent can see its full provenance: which source it came from, when it was loaded, its recency date, which account it arrived with, how many corroborating sources provided the same value, and its current composite score breakdown by dimension. The agent can also see all Silver and Void values for the same attribute type, their scores, and why each is ranked where it is.

Agents and automated processes can mark a specific demographic value as bad by setting its bad_flag. A bad flag records the flagging actor, the timestamp, and an optional reason. Bad-flagged values receive a severe score demotion that moves them to void tier. They are never deleted. They remain in history with the bad flag visible. If a bad flag was applied in error, it can be reversed by an authorized agent, which removes the demotion and allows the scoring engine to re-evaluate the value's tier.

## False Merge Detection and Auto-Accept Splits

When new demographics are loaded for a previously merged entity, the scoring engine evaluates not only opportunities to merge additional records but also signals that the current merge may be a false positive. Conflicting SSN variants suggesting generational suffixes (John Smith Sr. vs John Smith Jr.), significantly different age signals from different sources, non-overlapping geographic histories that are physically implausible for one person, and different employer histories that do not coexist plausibly are all false merge signals.

False merge signals surface as agent review items, not as automatic splits. The agent sees a finding: this entity may be two people based on conflicting demographic patterns. The agent reviews the finding and either dismisses it (confirming the merge is correct) or initiates a split. For high-volume agencies where manual review of every finding is operationally unrealistic, a configuration flag enables automatic acceptance of system split suggestions. When auto-accept is enabled, the system applies the suggested split, records the split event in core.event as system-initiated with the confidence score that drove the decision, and makes the result available for agent review and reversal after the fact.

## NCOA Integration

NCOA (National Change of Address) processing typically arrives through letter vendor integrations. A certified letter vendor module handles NCOA match detection automatically: when a mailed letter receives an NCOA match response, the vendor module records the old address as an NCOA-hit return and creates a new address history instance from the forwarding address, sourced as a postal service update.

Agencies printing in-house receive returned mail physically. A collector retrieves the account, logs an NCOA action code, and the system prompts them to select which address the letter was returned from (from the entity's address history) and to enter or select the new address from the change-of-address sticker. The system records the old address as returned and creates the new address history instance. The scoring engine processes both updates through the normal event and workflow path.

## Side Notes Captured For Future Discussion

**Dialer vendor module specification**: OSS dialer module plus vendor-specific modules (TCN and others) that expose contact pool query interfaces. The module interface for dialer integration is a HiveAR v2 module roadmap item.

**Nightly and periodic maintenance task system**: fully addressed by the configurable maintenance event architecture described in this decision. No separate maintenance subsystem is required.

## Implementation Phasing

**HiveAR v1 (MVP):** Simple contact storage with history table schema in place. Separate demographic history tables per attribute type ship in v1 (phone_history, address_history, email_history). Each row records the value, source, received date, and a simple is_current flag. No scoring engine, no Gold/Silver/Void tiering, no confidence decay. The best contact is the most recent non-voided value. Users can manually mark a contact as bad.

Why the history tables matter in v1: if v1 stores only the current phone number and overwrites it when a new one arrives, the historical data needed for scoring in v2 is lost. The history tables are cheap storage. The scoring engine is expensive logic.

**HiveAR v2:** Gold, Silver, and Void tiering based on simple rules. Contact outcome scoring (RPC results influence tier). Basic confidence scoring (source + recency, no decay).

**HiveAR v3+:** Full four-dimension scoring with configurable weights. Confidence decay functions. Maintenance event architecture. Natural phone rotation. NCOA integration. False merge detection.

**Breaking change risk: HIGH if history tables are omitted.** You cannot reconstruct history from a single-value field.

## Implications For Contributors

Locale Module authors must declare completeness validators for each attribute type their module contributes. A Locale Module contributing address satellite tables without a completeness validator for addresses will be flagged as non-compliant.

Contact outcome events that affect demographic scoring must fire through the normal event and workflow path. No module may directly update demographic composite scores outside the workflow engine.

The demographic history tables are append-only by convention and policy. No row in a demographic history table is ever deleted. Bad flagging is the mechanism for marking values as unusable.

Source type weights are organization-scoped configuration. The standard seed pack delivers suggested weight defaults. Agencies may modify them without module changes.
