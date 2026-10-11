# Open Questions

These are the architectural areas where the Foundation has not yet committed to a direction. They are where contribution helps most.

Each item carries two framings. The technical framing describes the design work. The experience framing is a question anyone who works in collections can answer from their own floor, with no technical background required. Answering the experience framing **is** contributing to the design.

How to answer one: open a GitHub issue using the "How we actually handle this" template, post in the #platform-design channel if you are on the Collective's Discord, or ask your AI assistant to read [START-HERE.md](START-HERE.md) and interview you. Each item below will link to a tracking issue as issues are filed.

Version targets indicate when the item is expected to ship, not when the decision will be made. Targets are reassessed as each decision is approached; an item tagged v2 can move to v1 when the work shows it belongs there.

## HiveAR (AR domain)

### Payment arrangements

**Technical:** The arrangement definition: installment schedules, amounts and due dates, promise-to-pay tracking, and broken-arrangement handling. Reuses the persisted application directive from [HIVE-0007](decisions/hivear/HIVE-0007-payment-application-and-waterfall.md), which already governs how each arrangement payment applies through the waterfall.
**From experience:** A consumer on a six-month plan misses month three, then pays double in month four. What should happen to the remaining schedule? What counts as a broken arrangement at your company, and what happens the moment it breaks?
**Target:** HiveAR v2. Issue: #1.

### Settlement rules

**Technical:** Settlement of a debt for less than the full balance: settlement offers and approval authority, settlement-in-full versus partial settlement, payment terms and settlement arrangements, the write-off of the forgiven remainder, and the commission and remittance treatment of settled amounts. The settlement payment itself applies through the [HIVE-0007](decisions/hivear/HIVE-0007-payment-application-and-waterfall.md) waterfall.
**From experience:** Walk through the last settlement that got complicated. Who had authority to approve it, what got documented, and what happened to the forgiven remainder in your books and in the client's?
**Target:** HiveAR v2. Issue: #2.

### Action and result codes

**Technical:** Contact attempt logging vocabulary, the compliance implications that each jurisdiction's Compliance Pack states, client reporting integration, and relationship to the reason code registry ([WAX-0020](decisions/wax/WAX-0020-reason-code-registry.md)).
**From experience:** What action and result codes does your company actually use every day, which ones exist only because a client demands them, and where does your current system's vocabulary fail to describe what really happened on a call?
**Target:** HiveAR v2. Issue: #3.

### Debt lineage

**Technical:** Architecture for recording prior instances of a debt created by rollover or re-placement. Prior instances are never simultaneously active. Display label is Debt Lineage.
**From experience:** When a debt leaves and comes back, whether recalled and re-placed, rolled from first to second placement, or returned and resold, what history do you wish traveled with it, and what history must **not** travel with it?
**Target:** HiveAR v2. Issue: #4.

### Debt Group system actions

**Technical:** Automatic lifecycle actions on debt groups at every level of a grouping scheme: orphan detection, aggregate field maintenance workflows, status propagation, and lock and unlock event handling. Specification of Core-delivered workflow definitions for debt group maintenance. Builds on [HIVE-0004](decisions/hivear/HIVE-0004-debt-groups.md).
**From experience:** When you group debts, for a lawsuit, a payment plan, or a family of debts, what should happen automatically when one debt in the group changes status, gets paid, or gets recalled?
**Target:** HiveAR v2. Issue: #5.

### Compliance unit in a grouping hierarchy

**Technical:** When each charge is a debt, which level of the grouping hierarchy a notice that a jurisdiction requires, such as the United States validation notice, a dispute, a cease-communication request, and a payment arrangement attach to, so that a charge-level debt does not multiply notices. The regional rules that bear on this need verification by someone with compliance standing. Builds on [HIVE-0004](decisions/hivear/HIVE-0004-debt-groups.md) and [HIVE-0005](decisions/hivear/HIVE-0005-debt-structure-and-balance-composition.md).
**From experience:** When a physician practice or a toll agency places individual charges with you, what do you send the consumer a validation notice for: each charge, each invoice, each visit, or the patient? What happens when the consumer disputes just one charge?
**Target:** HiveAR v2.

### Group-level entity relationships

**Technical:** Whether an entity can be related to a debt group and inherited by every debt beneath it, such as a guarantor responsible for everything under one patient, instead of being related to each debt. Builds on [HIVE-0001](decisions/hivear/HIVE-0001-entity-data-model-person-business-and-entity-relationships.md) and [HIVE-0004](decisions/hivear/HIVE-0004-debt-groups.md).
**From experience:** When one person is responsible for every charge for a patient, how does your system record that, and what breaks when a new charge arrives for the same patient?
**Target:** HiveAR v2.

### Changing a debt's grouping scheme

**Technical:** Moving existing debts from one grouping scheme to another when a client changes how it places, including what happens to the groups, their aggregates, and their history. Builds on [HIVE-0004](decisions/hivear/HIVE-0004-debt-groups.md).
**From experience:** When a client changes how it sends you data, for example from account-level to charge-level placements, what do you do with the debts you already hold?
**Target:** HiveAR v3.

### Client hierarchies

**Technical:** Architecture for parent-company and subsidiary-client relationships, including whether cross-client debt groups and entity associations are supported within a client hierarchy.
**From experience:** Where do parent and subsidiary client relationships actually bite in daily work: reporting, remittance, work standards, or consumer conversations that span both?
**Target:** HiveAR v2. Issue: #6.

### Legal module

**Technical:** Legal case lifecycle, debt and debt group association with cases, debt group lock behavior during legal proceedings, interaction between legal status and debt status codes, appeals and re-filings.
**From experience:** Walk through a debt's handoff to legal at your company. What gets locked, what keeps moving, who can still touch it, and where has your current system let something happen on a debt that should have been frozen?
**Target:** HiveAR v2. Issue: #7.

### Itemization and service lines

**Technical:** Full healthcare module specification for the lines of an itemization: the complete service-line field set, payer and claim detail, and service-line semantics. The core itemization is defined in [HIVE-0005](decisions/hivear/HIVE-0005-debt-structure-and-balance-composition.md), and the mechanism by which a module extends its lines is [HIVE-0009](decisions/hivear/HIVE-0009-debt-type-structure-extension.md); this item is the module realization. Whether a charge belongs to a debt's itemization or is a debt in its own right depends on how the client tracks balances: part of the itemization for a credit card or a hospital claim, a debt for a physician charge or a toll. Where a charge is a debt, the grouping scheme of [HIVE-0004](decisions/hivear/HIVE-0004-debt-groups.md) supplies the invoice, visit, and patient levels above it. The seed set of line types that the first modules supply, each in one of the six classifications, is also open.
**From experience:** For medical debt or any debt that comes with an itemization, which line-level details do collectors and consumers actually ask about, and which does your system fail to show you?
**Target:** HiveAR v2. Issue: #8.

### Reference dates beyond the United States set

**Technical:** Whether the candidate reference dates that a client provides stay the five that [HIVE-0005](decisions/hivear/HIVE-0005-debt-structure-and-balance-composition.md) stores, or become a registry that Compliance Packs extend, so that the notice of another jurisdiction can name a date the five do not cover. Builds on [MOD-US-0001](decisions/modules/united-states/MOD-US-0001-itemization-date-and-validation-itemization.md).
**From experience:** If you collect outside the United States, what date does the first notice to the consumer state the amount as of, and where does your system get it?
**Target:** HiveAR v2.

### Restrictions a party places on contact

**Technical:** The mechanism by which a party, or someone acting for the party, limits contact: a request to stop, to use only certain channels, or not to be contacted at certain times or places, with its evidence, scope, duration, and release. It can only narrow what the contact window and frequency checks of [HIVE-0010](decisions/hivear/HIVE-0010-contact-windows-and-contact-frequency.md) permit, and the effect each jurisdiction gives such a request belongs to its Compliance Pack.
**From experience:** When a consumer tells a collector not to call at work, or to send everything in writing, how does your system make sure every collector and every dialer honors it, and where does it fail?
**Target:** HiveAR v2.

### Commercial collection rules in the United States

**Technical:** The federal and state rules that govern collecting commercial debt in the United States, such as licensing, bonding, conduct, and contact rules for collectors of business debts, researched separately from the consumer rules of [MOD-US-0001](decisions/modules/united-states/MOD-US-0001-itemization-date-and-validation-itemization.md) and [MOD-US-0003](decisions/modules/united-states/MOD-US-0003-federal-contact-times-and-call-frequency.md) and supplied as Compliance Pack content for debts whose debt type declares the commercial regulatory nature under [HIVE-0009](decisions/hivear/HIVE-0009-debt-type-structure-extension.md). Which consumer protections do not reach commercial debt, and which apply anyway, needs verification by someone with compliance standing.
**From experience:** If you collect business debts, which rules do you follow that differ from consumer collection: licensing, bonding, when and how you may call, or something else?
**Target:** HiveAR v2.

### Generative consumer-facing content

**Technical:** AI-generated member-facing content across texts, emails, letters, chat, and voice, with the content, review, approval, and audit controls that a jurisdiction's content rules may require, which its Compliance Pack states and which need verification. The highest-compliance-exposure surface in the platform.
**From experience:** If software drafted consumer messages for your agency, what would have to be true before your compliance officer would let one go out the door?
**Target:** HiveAR v2. Issue: #9.

### AI toolbox implementation

**Technical:** AR-specific AI tools and the debt-data and compliance-documentation content exposed through the AI toolbox infrastructure ([WAX-0031](decisions/wax/WAX-0031-ai-agent-infrastructure.md)).
**From experience:** What is the most tedious judgment-free task in your day that you would hand to an assistant tomorrow, and what task would you never hand over?
**Target:** HiveAR v2. Issue: #10.

### Reporting and BI content

**Technical:** AR-specific reporting content: the set of native operational dashboards HiveAR ships, the prefab AR report pack with its anchored business intelligence tool selected under the license-discipline principle, and any read model projections that a Module delivers for users to query. Builds on [WAX-0032](decisions/wax/WAX-0032-reporting-and-business-intelligence.md).
**From experience:** Which five reports actually run your company, and which numbers do you still compute in a spreadsheet because no system gets them right?
**Target:** HiveAR v2. Issue: #11.

### Module roadmap: communications

**Technical:** Telephony integration (dialer, PBX, transcript capture, recording storage), texting (SMS, MMS, RCS, two-way with transcript storage), email, and letters (in-house print, template designer with mail merge, bulk print-to-file for external vendors).
**From experience:** Rank the channels by what actually collects at your company today, and describe the worst integration seam you live with between your dialer, your texting platform, and your system of record.
**Target:** HiveAR v2. Issue: #12.

### Module roadmap: integrations and portals

**Technical:** Metro2 credit reporting, credit report pulling (Equifax, Experian, TransUnion, Innovis), consumer portal, client portal, and data analytics module.
**From experience:** What do consumers and clients most often call about that a portal should have answered, and what has stopped your company from giving them one?
**Target:** HiveAR v2. Issue: #13.

### Contractual data-use restrictions and merge scope

**Technical:** Client-level restrictions on data co-mingling applied to entity matching and the golden record. Provenance becomes a rich record carrying not just where a value came from but how it may be used. Merge scope is constrained by client policy: a restricted client's consumer records resolve to an isolated canonical record that neither contributes values to nor draws values from other clients' records, while merging within that client's own records continues. Extends [HIVE-0002](decisions/hivear/HIVE-0002-entity-matching-golden-record-and-locale-aware-identity-resolution.md) and [HIVE-0003](decisions/hivear/HIVE-0003-demographic-history-golden-record-and-contact-intelligence.md).

**From experience:** Which of your clients restrict how their debt data may be used, what exactly do the restrictions forbid (discussing other debts on a call, combined letters, shared contact data), and how does your shop enforce those restrictions today?

**Target:** HiveAR v2. Issue: #20.

### Accounting period close

**Technical:** How an accounting period closes and what a close locks, including what happens to a payment, reversal, or adjustment dated in a period that is already closed. Builds on [HIVE-0006](decisions/hivear/HIVE-0006-gaap-journal-and-general-ledger.md).

**From experience:** If your books close each month, what happens when a payment or an adjustment arrives for a month that is already closed? Who can post into the closed month, and what record does that leave?

**Target:** HiveAR v2.

### Interest calculation and posting points

**Technical:** How interest is calculated, shown, and recorded. The leading direction is to calculate accrued interest at read time for display, without writing anything, and to record it as an event on the debt only at posting points, the first of which is applying a payment. A daily accrual event for every debt is not the design. Still open are which other events post accrued interest, such as statements, rate changes, balance adjustments, judgments, and closing a debt; how interest is calculated across a period in which the rate or the balance changed; and how the amount quoted to a consumer is kept consistent with the amount later posted. For unsecured consumer debt, interest stays off unless a region pack and the contract authorize it, per [MOD-UNSECURED-0001](decisions/modules/unsecured-consumer-debt/MOD-UNSECURED-0001-definition-and-buckets.md). The disclosure and itemization rules that apply to interest need verification by someone with compliance standing. Builds on [HIVE-0005](decisions/hivear/HIVE-0005-debt-structure-and-balance-composition.md).

**From experience:** When a consumer calls for a payoff amount, how does your system work out the interest owed as of today, and when does that interest actually land on the debt? Have you seen a quoted payoff and the posted amount disagree, and what did it cost you?

**Target:** HiveAR v2.

### Credit reporting history

**Technical:** How the platform keeps the record of what it reported to the credit bureaus without bloating the event store. Reporting every active debt twice a month, with the full reported record stored each time, would add an event per debt per cycle, each one hashed and kept forever. A candidate design stores each generated file once in document storage ([WAX-0030](decisions/wax/WAX-0030-document-storage.md)) with its hash anchored, writes an event on a debt only when its reportable values change, and keeps a compact index that answers what was reported for a debt on a given date. Whether that record satisfies dispute investigation and record retention obligations needs verification by someone with compliance standing. How a correction to a past report is recorded is also open. Relates to the credit reporting item under Module roadmap: integrations and portals.

**From experience:** When a consumer disputes what you reported, what do you need to pull up to answer it, and how far back do you go? How much of your current system's storage goes to credit reporting history, and what in it have you never once looked at?

**Target:** HiveAR v2.

## Wax (framework)

### Custom action type sandboxing

**Technical:** Sandboxed execution environment for power-user-installed custom C# action types, limiting default permissions and requiring explicit privilege escalation. Extends [WAX-0023](decisions/wax/WAX-0023-workflow-automation-engine.md).
**Target:** Wax v3+. Issue: #14.

### System-to-system configuration promotion UI

**Technical:** Purpose-built interface for promoting configuration between instances with diff preview, mandatory comments, and full audit history. Extends [WAX-0021](decisions/wax/WAX-0021-configuration-management-and-environment-lifecycle.md).
**Target:** Wax v3+. Issue: #15.

### Running bulk writes during live hours

**Technical:** How bulk chunk writes coexist with live users, workflow rules, and readers while the system is in use. A chunk locks the state row of every aggregate in it until its transaction commits, so a user's write to one of those aggregates waits for the chunk, and a burst of bulk writes loads the database and the read models that follow it. Ideas to settle for the live system: throttling by working hours, with fewer workers and smaller chunks while people are working and full speed in the batch window; a lock-wait policy, such as skipping aggregates that are already locked and retrying them later, or a lock timeout with a retry; limits on chunk size and on concurrent chunks; how bulk workers and live commands that lock several aggregates avoid deadlocking one another; and whether a chunk could read and decide without holding locks, then lock, verify each aggregate's version, and write briefly, which would shorten lock time but loosens the rule that locks come before any read. Extends [WAX-0024](decisions/wax/WAX-0024-high-availability-disaster-recovery-and-distributed-workloads.md) and builds on [WAX-0013](decisions/wax/WAX-0013-event-chain-integrity-and-tamper-evidence.md).
**Target:** Wax v2, with the bulk framework.

### Combining Compliance Packs across jurisdiction layers

**Technical:** How a federal Compliance Pack and a state pack combine when both speak to one subject, which one controls, and how a pack states that no rule was found or that a jurisdiction is not yet researched. Builds on [WAX-0008](decisions/wax/WAX-0008-extensibility-construct-nomenclature.md) and [MOD-US-0001](decisions/modules/united-states/MOD-US-0001-itemization-date-and-validation-itemization.md).
**From experience:** When a federal rule and a state rule differ on the same point, how does your company decide which one governs, and who signs off on that choice?
**Target:** Wax v2.
