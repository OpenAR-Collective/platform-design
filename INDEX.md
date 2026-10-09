# Decision Index

One line per decision. Read a decision's file for the full context, reasoning, and implications.
An AI assistant helping with this repository should read this index first, then load the specific decisions relevant to the task.

## Shared Framework Decisions

- **[SHARED-0001](decisions/shared/SHARED-0001-repository-architecture-and-layer-separation-wax-and-hivear.md)** Repository Architecture and Layer Separation (Wax and HiveAR). The platform is developed as two distinct codebases housed in separate repositories, each with independent version cadences.
- **[SHARED-0002](decisions/shared/SHARED-0002-decoupled-frontend-and-backend.md)** Decoupled Frontend and Backend. The HiveAR will be built with a strict separation between the backend and the frontend.
- **[SHARED-0003](decisions/shared/SHARED-0003-api-surface.md)** API Surface. The HiveAR will expose a REST API as its published interface between the backend and all frontends.
- **[SHARED-0004](decisions/shared/SHARED-0004-frontend-framework.md)** Frontend Framework. The HiveAR reference frontend will be built using Blazor WebAssembly.
- **[SHARED-0005](decisions/shared/SHARED-0005-frontend-internationalization.md)** Frontend Internationalization. The HiveAR frontend will implement internationalization at two distinct layers: the data layer, where all user-visible reference values and domain labels are resolved by the backend and delivered locale-aware through the API, and the UI chrome layer, where button labels, field labels, navigation items, error messages, and all other interface strings are sourced from locale-specific resource bundles.
- **[SHARED-0006](decisions/shared/SHARED-0006-file-interface-engine.md)** File Interface Engine. Wax will include a file interface engine that supports bidirectional data exchange between the platform and external systems.
- **[SHARED-0007](decisions/shared/SHARED-0007-devops-and-contribution-lifecycle.md)** DevOps and Contribution Lifecycle. The Foundation operates a unified DevOps and contribution lifecycle across the Wax framework, the HiveAR platform, and all module repositories under Foundation control.
- **[SHARED-0008](decisions/shared/SHARED-0008-reference-deployment-architecture.md)** Reference Deployment Architecture. The Foundation provides Docker Compose reference architectures for deploying HiveAR and other applications built on Wax, for use by agencies hosting the platform themselves or by vendors hosting it on their behalf.

## Wax Framework Decisions

- **[WAX-0001](decisions/wax/WAX-0001-enriched-event-sourcing.md)** Enriched Event Sourcing. The Wax will use enriched event sourcing as its primary audit and persistence strategy.
- **[WAX-0002](decisions/wax/WAX-0002-cqrs-model.md)** CQRS Model. The Wax will implement simple CQRS: a strict separation of the command path (writes) from the query path (reads) within the same application and the same PostgreSQL database.
- **[WAX-0003](decisions/wax/WAX-0003-database-platform.md)** Database Platform. The Wax will use PostgreSQL as its primary relational database.
- **[WAX-0004](decisions/wax/WAX-0004-schema-architecture-and-module-extension-pattern.md)** Schema Architecture and Module Extension Pattern. Wax will own a dedicated database schema named core.
- **[WAX-0005](decisions/wax/WAX-0005-naming-conventions.md)** Naming Conventions. All database object names across the core schema and all modules will follow verbose snake_case.
- **[WAX-0006](decisions/wax/WAX-0006-deployment-model.md)** Deployment Model. HiveAR will be designed for agency-controlled deployment: installed on the agency's own infrastructure, or hosted by a vendor of the agency's choosing.
- **[WAX-0007](decisions/wax/WAX-0007-modular-composition-architecture.md)** Modular Composition Architecture. The Wax will be built as a modular composition system.
- **[WAX-0008](decisions/wax/WAX-0008-extensibility-construct-nomenclature.md)** Extensibility Construct Nomenclature. Wax's extensibility system uses two top-level constructs distinguished by a single principle: Modules contain code; Packs contain data.
- **[WAX-0009](decisions/wax/WAX-0009-module-contract-standard.md)** Module Contract Standard. The Wax module contract standard will use a hybrid model: a manifest file for discovery, metadata, and dependency declarations, combined with a C# interface for runtime behavioral contracts.
- **[WAX-0010](decisions/wax/WAX-0010-module-registry.md)** Module Registry. The Wax will maintain a module registry in the core schema.
- **[WAX-0011](decisions/wax/WAX-0011-internationalization-architecture-and-reference-value-system.md)** Internationalization Architecture and Reference Value System. The Wax will store all reference values, status codes, reason codes, and lookup values as language-neutral UUID surrogate keys.
- **[WAX-0012](decisions/wax/WAX-0012-date-time-timezone-and-freeform-note-language.md)** Date, Time, Timezone, and Freeform Note Language. All instants, meaning values that name a moment in time, will be stored in UTC, and display to users will be rendered in each user's configured timezone.
- **[WAX-0013](decisions/wax/WAX-0013-event-chain-integrity-and-tamper-evidence.md)** Event Chain Integrity and Tamper-Evidence. Wax will implement cryptographically verifiable, tamper-evident audit history through three complementary mechanisms: per-aggregate hash chaining within core.event, delta-based periodic checkpoint anchoring to an external RFC 3161 trusted timestamp authority, and a formal break-glass process for authorized chain modifications.
- **[WAX-0014](decisions/wax/WAX-0014-encryption-and-data-protection.md)** Encryption and Data Protection. TLS is required and enforced for all API and UI connections.
- **[WAX-0015](decisions/wax/WAX-0015-security-module.md)** Security Module. Wax will ship a distinct, self-contained component called the Wax Security Module (WSM).
- **[WAX-0016](decisions/wax/WAX-0016-data-access-architecture-read-layer-and-direct-query-interface.md)** Data Access Architecture, Read Layer, and Direct Query Interface. No INSERT, UPDATE, or DELETE operations are permitted on the platform's database tables by any user, tool, or connection other than the application's own service credentials operating through the command handler path.
- **[WAX-0017](decisions/wax/WAX-0017-identity-and-authentication.md)** Identity and Authentication. Every human user and every API service account is a row in core.user.
- **[WAX-0018](decisions/wax/WAX-0018-access-control.md)** Access Control. Wax ships with a complete, non-bypassable role-based access control model.
- **[WAX-0019](decisions/wax/WAX-0019-organizational-model.md)** Organizational Model. Every HiveAR installation contains at least one organization, created during the installation wizard.
- **[WAX-0020](decisions/wax/WAX-0020-reason-code-registry.md)** Reason Code Registry. Reason codes are a defined subset of the reference value system established in Wax Design Decision 11.
- **[WAX-0021](decisions/wax/WAX-0021-configuration-management-and-environment-lifecycle.md)** Configuration Management and Environment Lifecycle. All user-configurable items are treated as versioned configuration with full change history.
- **[WAX-0022](decisions/wax/WAX-0022-user-defined-tables-and-user-defined-windows.md)** User-Defined Tables and User-Defined Windows. Wax will support two distinct user-extensibility constructs.
- **[WAX-0023](decisions/wax/WAX-0023-workflow-automation-engine.md)** Workflow Automation Engine. Wax will include a user-configurable workflow automation engine.
- **[WAX-0024](decisions/wax/WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md)** High Availability, Disaster Recovery, and Distributed Workloads. Wax's application tier is stateless, enabling horizontal scaling and instance-level failover without coordination.
- **[WAX-0025](decisions/wax/WAX-0025-primary-programming-language.md)** Primary Programming Language. The Wax will be built in C# on the .NET runtime.
- **[WAX-0026](decisions/wax/WAX-0026-event-schema-versioning.md)** Event Schema Versioning. Wax will evolve event payload schemas through read-time upcasting, never through in-place migration of stored events.
- **[WAX-0027](decisions/wax/WAX-0027-pending-event-register.md)** Pending Event Register. Wax will provide a Pending Event Register: an operational store of individual future-dated domain events scheduled against specific aggregates.
- **[WAX-0028](decisions/wax/WAX-0028-job-scheduler.md)** Job Scheduler. Wax will provide a Job Scheduler: a store of system-level jobs scheduled to run at a future time, either once or on a recurring cadence.
- **[WAX-0029](decisions/wax/WAX-0029-tasking.md)** Tasking. Wax will provide a Tasking subsystem for human work: assigning, tracking, discussing, and completing units of work performed by people.
- **[WAX-0030](decisions/wax/WAX-0030-document-storage.md)** Document Storage. Wax will store documents by separating the document aggregate from the document bytes.
- **[WAX-0031](decisions/wax/WAX-0031-ai-agent-infrastructure.md)** AI Agent Infrastructure. Wax will provide infrastructure for AI agents to operate against the platform.
- **[WAX-0032](decisions/wax/WAX-0032-reporting-and-business-intelligence.md)** Reporting and Business Intelligence. Wax will not build a reporting or business intelligence engine.
- **[WAX-0033](decisions/wax/WAX-0033-module-composition-model.md)** Module Composition Model. Wax modules will compose from a shared pool of primitive definitions rather than redefining the primitives they have in common.
- **[WAX-0034](decisions/wax/WAX-0034-monetary-values-and-currency.md)** Monetary Values and Currency. Wax will represent every monetary value as a typed quantity: an exact decimal amount together with an ISO 4217 currency code, carried together everywhere the value appears, in event payloads, authoritative state tables, read models, and user-defined fields.

## HiveAR Domain Decisions

- **[HIVE-0001](decisions/hivear/HIVE-0001-entity-data-model-person-business-and-entity-relationships.md)** Entity Data Model, Person, Business, and Entity Relationships. HiveAR models people and businesses as Entity records.
- **[HIVE-0002](decisions/hivear/HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md)** Entity Matching, Golden Record, and Locale-Aware Identity Resolution. HiveAR will include an entity matching engine that identifies duplicate person and business entity records across the database, merges them into a single canonical record while preserving all source data, and maintains a programmatic golden record view that surfaces the best available value for each attribute based on source reliability and data recency, where a multi-field attribute such as a name or an address is selected as a whole unit, never assembled from components of different source records.
- **[HIVE-0003](decisions/hivear/HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md)** Demographic History, Golden Record, and Contact Intelligence. HiveAR maintains a complete history of every demographic value ever received for an entity, organized in separate tables per attribute type.
- **[HIVE-0004](decisions/hivear/HIVE-0004-account-sets.md)** Account Sets. Every account in HiveAR belongs to exactly one Account Set at all times.
- **[HIVE-0005](decisions/hivear/HIVE-0005-account-structure-and-balance-composition.md)** Account Structure and Balance Composition. HiveAR will classify every account on two independent axes and compose its balance from typed buckets rather than fixed columns.
- **[HIVE-0006](decisions/hivear/HIVE-0006-gaap-journal-and-general-ledger.md)** GAAP Journal and General Ledger. HiveAR will maintain a GAAP-compliant double-entry journal and general ledger for the AR money it handles, as a subsystem of the agency's true accounting system rather than a replacement for it.
- **[HIVE-0007](decisions/hivear/HIVE-0007-payment-application-and-waterfall.md)** Payment Application and Waterfall. HiveAR will apply each incoming payment or credit to an account's balance buckets through a configurable waterfall, an ordered priority that determines which buckets a payment pays down and in what order.
- **[HIVE-0008](decisions/hivear/HIVE-0008-client-billing-invoicing-and-statements.md)** Client Billing, Invoicing, and Statements. HiveAR will treat the client as a posting-driven financial aggregate, symmetric with the debtor account, whose balances are the projection of immutable client transactions.
- **[HIVE-0009](decisions/hivear/HIVE-0009-debt-type-account-structure-extension.md)** Debt-Type Account Structure Extension. HiveAR will let a debt-type module attach the subject-matter structure of its debt to the core account, while the core account itself ships no subject-matter structure of its own.

## Module Decisions: Debt-Purchase

- **[MOD-PURCHASE-0001](decisions/modules/debt-purchase/MOD-PURCHASE-0001-chain-of-title-and-ownership-transitions.md)** Chain of Title and Ownership Transitions. The debt-purchase module will record an account's chain of title, the documented history of who has owned the debt from the original creditor to the current owner, and the ownership transitions that build and close it.

## Module Decisions: Unsecured Consumer Debt

- **[MOD-UNSECURED-0001](decisions/modules/unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md)** Definition and Buckets. The unsecured consumer debt module is the platform's first debt-type module and its reference example, the canonical bundle of the common consumer-debt primitives.
