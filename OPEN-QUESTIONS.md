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

**Technical:** Settlement of an account for less than the full balance: settlement offers and approval authority, settlement-in-full versus partial settlement, payment terms and settlement arrangements, the write-off of the forgiven remainder, and the commission and remittance treatment of settled amounts. The settlement payment itself applies through the [HIVE-0007](decisions/hivear/HIVE-0007-payment-application-and-waterfall.md) waterfall.
**From experience:** Walk through the last settlement that got complicated. Who had authority to approve it, what got documented, and what happened to the forgiven remainder in your books and in the client's?
**Target:** HiveAR v2. Issue: #2.

### Action and result codes

**Technical:** Contact attempt logging vocabulary, FDCPA compliance implications, client reporting integration, and relationship to the reason code registry ([WAX-0020](decisions/wax/WAX-0020-reason-code-registry.md)).
**From experience:** What action and result codes does your company actually use every day, which ones exist only because a client demands them, and where does your current system's vocabulary fail to describe what really happened on a call?
**Target:** HiveAR v2. Issue: #3.

### Account lineage

**Technical:** Architecture for recording prior instances of an account created by rollover or re-placement. Prior instances are never simultaneously active. Display label is Account Lineage.
**From experience:** When an account leaves and comes back, whether recalled and re-placed, rolled from first to second placement, or returned and resold, what history do you wish traveled with it, and what history must **not** travel with it?
**Target:** HiveAR v2. Issue: #4.

### Account Set system actions

**Technical:** Automatic lifecycle actions on sets: orphan detection, aggregate field maintenance workflows, status propagation, and lock and unlock event handling. Specification of Core-delivered workflow definitions for set maintenance. Builds on [HIVE-0004](decisions/hivear/HIVE-0004-account-sets.md).
**From experience:** When you group accounts, for a lawsuit, a payment plan, or a family of debts, what should happen automatically when one account in the group changes status, gets paid, or gets recalled?
**Target:** HiveAR v2. Issue: #5.

### Client hierarchies

**Technical:** Architecture for parent-company and subsidiary-client relationships, including whether cross-client account sets and entity associations are supported within a client hierarchy.
**From experience:** Where do parent and subsidiary client relationships actually bite in daily work: reporting, remittance, work standards, or consumer conversations that span both?
**Target:** HiveAR v2. Issue: #6.

### Legal module

**Technical:** Legal case lifecycle, account and set association with cases, set lock behavior during legal proceedings, interaction between legal status and account status codes, appeals and re-filings.
**From experience:** Walk through an account's handoff to legal at your company. What gets locked, what keeps moving, who can still touch it, and where has your current system let something happen on an account that should have been frozen?
**Target:** HiveAR v2. Issue: #7.

### Charge detail and service lines

**Technical:** Full healthcare and itemized-charge module specification: the complete service-line field set, payer and claim detail, and service-line semantics. The structural mechanism for attaching sub-entities is [HIVE-0009](decisions/hivear/HIVE-0009-debt-type-account-structure-extension.md); this item is the module realization. Charge detail records are not distinct debts.
**From experience:** For medical or itemized debt, which line-level details do collectors and consumers actually ask about, and which does your system fail to show you?
**Target:** HiveAR v2. Issue: #8.

### Generative consumer-facing content

**Technical:** AI-generated member-facing content across texts, emails, letters, chat, and voice, with the content, review, approval, and audit controls that FDCPA and related content rules require. The highest-compliance-exposure surface in the platform.
**From experience:** If software drafted consumer messages for your agency, what would have to be true before your compliance officer would let one go out the door?
**Target:** HiveAR v2. Issue: #9.

### AI toolbox implementation

**Technical:** AR-specific AI tools and the account-data and compliance-documentation content exposed through the AI toolbox infrastructure ([WAX-0031](decisions/wax/WAX-0031-ai-agent-infrastructure.md)).
**From experience:** What is the most tedious judgment-free task in your day that you would hand to an assistant tomorrow, and what task would you never hand over?
**Target:** HiveAR v2. Issue: #10.

### Reporting and BI content

**Technical:** AR-specific reporting content: the set of native operational dashboards HiveAR ships, the prefab AR report pack with its anchored business intelligence tool selected under the license-discipline principle, and any read model projections delivered as seed packs for users to query. Builds on [WAX-0032](decisions/wax/WAX-0032-reporting-and-business-intelligence.md).
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

## Wax (framework)

### Custom action type sandboxing

**Technical:** Sandboxed execution environment for power-user-installed custom C# action types, limiting default permissions and requiring explicit privilege escalation. Extends [WAX-0023](decisions/wax/WAX-0023-workflow-automation-engine.md).
**Target:** Wax v3+. Issue: #14.

### System-to-system configuration promotion UI

**Technical:** Purpose-built interface for promoting configuration between instances with diff preview, mandatory comments, and full audit history. Extends [WAX-0021](decisions/wax/WAX-0021-configuration-management-and-environment-lifecycle.md).
**Target:** Wax v3+. Issue: #15.
