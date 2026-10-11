# Interview Probes by Territory

> **DRAFT.** These seed probes were drafted for founder review and have not yet been tuned against real conversations. Improve them as booth and Discord conversations reveal which questions open people up. The patterns to preserve: walk-me-throughs anchored to a specific recent instance, edge cases ("what makes this go sideways"), forgotten exceptions, and the vendor complaint ("what does every system get wrong about this"). Pricing, rates, and fee structures are never probed; see the antitrust guardrail in START-HERE.md.

Use three to five probes per conversation, adapted to what the person says. These are seeds, not a script. The decisions in this repository say debt where many systems and many people say account, so accept whichever word the person uses and ask which record in their system carries the balance that gets collected, because that is the unit the decisions care about.

## 1. New business intake and placements

- Walk me through the last placement file that arrived in bad shape. What was wrong with it, and what did it take to get those debts workable?
- When a client places debts with you, what information do they routinely leave out that you need on day one?
- Think of the last healthcare, toll, or card placement you loaded. What was the unit you collected against (the account, the claim, the visit, or a single charge), how did the client's file identify it, what itemization of charges or transactions came with it, and what did the levels above it let you do?
- A client places a debt whose charges, payments, and adjustments do not add up to the balance they sent. What does your company do with it: load it, hold it, or send it back?
- What happens at your company when the same debt shows up in two different placement files?
- What does every collections system get wrong about loading new business?

## 2. Work queues and debt treatment strategy

- Walk me through a debt that arrived this morning. What decides whose queue it lands in by this afternoon, and what decides how it gets worked?
- Pick one treatment path at your company: a letter series, a dialer campaign, or a text sequence. What pulls a debt off it, and what has to happen for it to go back on?
- When two rules claim the same debt at the same time, say a legal review and an active payment arrangement, which one actually wins today, and who decided that?
- What does every collections system get wrong about work queues that your team fixes by hand?

## 3. Consumer contact and communications

- Walk me through what happens after a consumer answers the phone and says "I just lost my job." Who records what, and what changes on the debt?
- When a letter comes back undeliverable, what actually happens next at your company?
- How do you decide which phone number to try when a debt has five of them?
- What is the exception everyone forgets when it comes to contact frequency or timing?

## 4. Disputes and validation

- Tell me about the last dispute that was a pain to resolve, from the moment it arrived to the moment it closed. Who touched it, what got written down, and what stopped while it was open?
- When a consumer disputes three debts in one phone call, how does your company record that?
- What happens when the client never sends the validation documents?
- What do the software vendors always get wrong about disputes?

## 5. Payments, plans, and arrangements

- A consumer on a six-month arrangement misses month three, then pays double in month four. Walk me through what happens to the rest of the schedule at your company.
- Tell me about the last split payment that had to cover several debts. How was the split decided, and who could override it?
- What happens when a payment posts and then bounces after you have already reported or remitted?
- What makes a payment plan go sideways in ways the paperwork never anticipated?

## 6. Trust accounting, remittance, and client billing

- Walk me through the last remittance that would not reconcile. Where was the discrepancy hiding?
- When a payment reverses after the client has already been paid, what does your company actually do?
- What does month-end close look like, and which part of it depends on a spreadsheet nobody else understands?
- What does every system get wrong about trust accounting?

## 7. Compliance and complaints

- Tell me about the last regulator or BBB complaint you worked. What records did you need to pull, and how long did it take to assemble them?
- When a cease-communication request comes in mid-conversation, what has to change on the debt, and how fast?
- What do you have to prove after the fact that your current system makes hard to prove?
- What is the exception everyone forgets in complaint handling?

## 8. Legal collections and judgments

- Walk me through a debt's handoff to legal. What gets locked, what keeps moving, and who can still touch it?
- Tell me about the last case where activity happened on a debt that should have been frozen for litigation.
- After judgment, what changes about how the debt is worked and accounted for?
- What does every system get wrong about legal inventory?

## 9. Recalls, closures, and returns

- A client recalls two hundred debts effective Friday. Walk me through what happens between the email and the debts being gone.
- What happens to a payment that arrives the week after the debt went back to the client?
- When a debt closes and later comes back, what history do you wish had traveled with it?
- What makes a recall messy in ways the client never sees?

## 10. Credit reporting

- Walk me through the last e-OSCAR dispute you handled end to end.
- When a debt is paid, settled, or recalled, what has to happen to the tradeline, and how does your company make sure it actually happens?
- Tell me about a time reporting got out of sync with reality. How was it caught?
- What does every system get wrong about Metro 2?

## 11. File imports and exports

- Take one client file you receive on a schedule. What is wrong with it more often than not, and who fixes it?
- When a placement file fails halfway through loading, what state are the debts in, and how do you recover?
- Which files leave your company every day (remittances, status updates, credit bureau files, vendor files), and which one breaks most often?
- Describe the last layout change a client made without telling you. What broke, and how did you find out?

## 12. Reporting and data visualization

- Which five numbers do you look at before anything else in the morning, and where does each one come from?
- Take one report you export to a spreadsheet to finish. What does the system get wrong or leave out?
- When a client's numbers and yours disagree on placements, payments, or liquidation, how do you reconcile them, and whose number wins?
- What has a client asked to see that you could not produce, and what did you send them instead?

## 13. Vendor integration

- List the vendors your collection system talks to: letter vendor, dialer, texting platform, payment processor, skip tracing, e-signature. Which connection fails without telling anyone?
- Walk me through what happens when a vendor's file or API is a day late. Who notices, and how?
- When a vendor returns data that changes a debt (a new address, a bankruptcy hit, a payment), where does it land, and what does it overwrite?
- Which vendor swap took the longest at your company, and what made it slow: the data, the workflow built around the old vendor, or the people?

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
