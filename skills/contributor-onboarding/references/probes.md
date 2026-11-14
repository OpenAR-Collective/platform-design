# Interview Probes by Territory

> **DRAFT.** These seed probes were drafted for founder review and have not yet been tuned against real conversations. Improve them as interviews reveal which questions open people up. The patterns to preserve: walk-me-throughs anchored to a specific recent instance, edge cases ("what makes this go sideways"), forgotten exceptions, and the wish list ("what would you want to happen here if nothing limited you"). Pricing, rates, and fee structures are never probed; see the antitrust guardrail in START-HERE.md.

Use three to five probes per conversation, adapted to what the person says. These are seeds, not a script. The decisions in this repository say debt where many people say account, so accept whichever word the person uses and ask which record in their system carries the balance that gets collected, because that is the unit the decisions care about.

## 1. New business intake and placements

- Walk me through the last placement file that arrived in bad shape. What was wrong with it, and what did it take to get those debts workable?
- When a client places debts with you, what information do they routinely leave out that you need on day one?
- Think of the last healthcare, toll, or card placement you loaded. What was the unit you collected against (the account, the claim, the visit, or a single charge), how did the client's file identify it, what itemization of charges or transactions came with it, and what did the levels above it let you do?
- A client places a debt whose charges, payments, and adjustments do not add up to the balance they sent. What does your company do with it: load it, hold it, or send it back?
- What happens at your company when the same debt shows up in two different placement files?
- What would you want to happen when new business is loaded, if nothing limited you?

## 2. Work queues and debt treatment strategy

- Walk me through a debt that arrived this morning. What decides whose queue it lands in by this afternoon, and what decides how it gets worked?
- Pick one treatment path at your company: a letter series, a dialer campaign, or a text sequence. What pulls a debt off it, and what has to happen for it to go back on?
- When two rules claim the same debt at the same time, say a legal review and an active payment arrangement, which one actually wins today, and who decided that?
- What does your team fix by hand in its work queues, and what would you want to happen there if nothing limited you?

## 3. Consumer contact and communications

- Walk me through what happens after a consumer answers the phone and says "I just lost my job." Who records what, and what changes on the debt?
- When a letter comes back undeliverable, what actually happens next at your company?
- How do you decide which phone number to try when a debt has five of them?
- What is the exception everyone forgets when it comes to contact frequency or timing?

## 4. Disputes and validation

- Tell me about the last dispute that was a pain to resolve, from the moment it arrived to the moment it closed. Who touched it, what got written down, and what stopped while it was open?
- When a consumer disputes three debts in one phone call, how does your company record that?
- What happens when the client never sends the validation documents?
- When you put together a validation notice, where do the interest, fees, payments, and credits since the itemization date come from: the client's file, your own postings, or both?
- What would you want to happen with disputes if nothing limited you?

## 5. Payments, plans, and arrangements

- A consumer on a six-month arrangement misses month three, then pays double in month four. Walk me through what happens to the rest of the schedule at your company.
- Tell me about the last split payment that had to cover several debts. How was the split decided, and who could override it?
- What happens when a payment posts and then bounces after you have already reported or remitted?
- What makes a payment plan go sideways in ways the paperwork never anticipated?

## 6. Trust accounting, remittance, and client billing

- Walk me through the last remittance that would not reconcile. Where was the discrepancy hiding?
- When a payment reverses after the client has already been paid, what does your company actually do?
- What does month-end close look like, and which part of it depends on a spreadsheet nobody else understands?
- What would you want to happen in trust accounting if nothing limited you?

## 7. Compliance and complaints

- Tell me about the last regulator or BBB complaint you worked. What records did you need to pull, and how long did it take to assemble them?
- When a cease-communication request comes in mid-conversation, what has to change on the debt, and how fast?
- What do you have to prove after the fact that your current system makes hard to prove?
- What is the exception everyone forgets in complaint handling?

## 8. Legal collections and judgments

- Walk me through a debt's handoff to legal. What gets locked, what keeps moving, and who can still touch it?
- Tell me about the last case where activity happened on a debt that should have been frozen for litigation.
- After judgment, what changes about how the debt is worked and accounted for?
- What would you want to happen with legal inventory if nothing limited you?

## 9. Recalls, closures, and returns

- A client recalls two hundred debts effective Friday. Walk me through what happens between the email and the debts being gone.
- What happens to a payment that arrives the week after the debt went back to the client?
- When a debt closes and later comes back, what history do you wish had traveled with it?
- What makes a recall messy in ways the client never sees?

## 10. Credit reporting

- Walk me through the last e-OSCAR dispute you handled end to end.
- When a debt is paid, settled, or recalled, what has to happen to the tradeline, and how does your company make sure it actually happens?
- Tell me about a time reporting got out of sync with reality. How was it caught?
- What would you want to happen in Metro 2 reporting if nothing limited you?

## 11. File imports and exports

- Take one client file you receive on a schedule. What is wrong with it more often than not, and who fixes it?
- When a placement file fails halfway through loading, what state are the debts in, and how do you recover?
- Which files leave your company every day (remittances, status updates, credit bureau files, files for service providers), and which one breaks most often?
- Describe the last layout change a client made without telling you. What broke, and how did you find out?

## 12. Reporting and data visualization

- Which five numbers do you look at before anything else in the morning, and where does each one come from?
- Take one report you export to a spreadsheet to finish. What does the system get wrong or leave out?
- When a client's numbers and yours disagree on placements, payments, or liquidation, how do you reconcile them, and whose number wins?
- What has a client asked to see that you could not produce, and what did you send them instead?

## 13. Vendor integration

- Which kinds of service providers does your collection system exchange data with: letter printing, dialer, texting, payment processing, skip tracing, e-signature? Which connection fails without telling anyone?
- Walk me through what happens when a service provider's file or API is a day late. Who notices, and how?
- When a service provider returns data that changes a debt (a new address, a bankruptcy hit, a payment), where does it land, and what does it overwrite?
- Think of the last time your company changed service providers for one of these. What made it slow: the data, the workflow built around the old provider, or the people?

## 14. Programming

- What is the last thing you had to build around your collections system because it could not do it, and what would you have wanted from the system instead?
- Where does your system's API or database fail to tell you what actually happened on a debt, so you had to infer it?
- Describe one integration you maintain that nobody wants to touch. What makes it fragile?
- What question about a debt's history can you not answer from the data model you have today?

## 15. IT infrastructure and data security

- When a client or auditor asks who viewed a specific consumer's record and when, how do you produce the answer today, and how long does it take?
- Walk me through a user leaving your company. What has to be shut off, in what order, and what should the system have handled on its own?
- What does your current system rely on policy or training to prevent that software should make impossible by design?
- The last time you restored from a backup, what did the system lose that you did not expect: in-flight payments, the audit trail, attachments?

## 16. Client management

- Walk me through the last new client your company brought on. What had to be set up before their first placement could load, and what turned out to be missing afterward?
- Think of a client whose rules differ from everyone else's. What is different, where is it recorded, and how does a collector learn it before working one of their debts?
- Tell me about the last time a client changed a rule partway through a contract, such as when to call, which letters to send, or how to remit. How did the change reach everyone who needed it, and how could you show later when it took effect?
- What did a client last ask to see in an audit or a performance review, and which part took longest to produce?

## 17. Collector operations and performance

- Walk me through a collector's first hour yesterday. What told them which debt to work first, and what did they do when that was wrong?
- Tell me about the last payment that two collectors both claimed. Who got credit for it at your company, and who decided?
- Think of the last time a supervisor had to step in on a call or a debt. How did they find out, and what got recorded?
- What does a collector keep on paper or in a spreadsheet because the system does not keep it for them?

## 18. Skip tracing and demographics

- Walk me through the last debtor you had to locate. Where did you look first, and how did you decide which new address or phone number to trust?
- When a new address arrives that conflicts with one a collector confirmed last month, what happens at your company, and who decides which one wins?
- Tell me about a time a phone number or address you found turned out to belong to someone else. How was it caught, and what had to be undone?
- When a debtor dies, moves abroad, or changes their name, how does the change reach every debt they owe?

## 19. Debt buying and portfolios

- Walk me through the last portfolio your company bought or sold. What arrived with the debts, what was missing, and how long was it before they could be worked?
- Tell me about a purchased debt that turned out to be paid, disputed, or in bankruptcy. What happened to it, and how was it returned to the seller or written off?
- When purchased debts are placed with an agency or a law firm, what does the owner need to track about each debt while someone else works it?
- What history about a purchased debt do you need from the seller and from the owners before them, and what do you do when it is not there?
