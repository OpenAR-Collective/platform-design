---
id: WAX-0031
title: "AI Agent Infrastructure"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 31: AI Agent Infrastructure

## Decision

Wax will provide infrastructure for AI agents to operate against the platform. An AI agent is an ordinary principal in the existing access-control model, reaching the platform's capabilities through a Model Context Protocol server that adapts existing commands and queries, and drawing on a retrieval layer over the agency's non-personal knowledge corpus. Models are pluggable providers, with self-hosted and cloud options treated as co-equal. The governing principle is that an AI agent can do nothing a human principal could not do, bounded by the same access control, hash-chained audit, and pre-event guardrails as every other actor.

## AI Agents Are Principals

[Wax Design Decision 18](WAX-0018-access-control.md) already makes principals cover human users and service accounts identically, with role-based access control and database row-level security. An AI agent is simply another principal. It holds roles, its reads are filtered by row-level security before any decryption runs, and its actions flow through the normal command handlers, recorded in core.event and attributed as AI-originated. There is no AI backdoor and no parallel permission system.

The platform supports many distinct AI principals, each with its own user identity and its own roles: a validation agent, an account-summarization agent, and a virtual-collector agent are separate principals, each scoped to exactly what its job requires. Least privilege is the rule, but least is measured against oversight. An agent whose every action a human approves may be broadly empowered, because the approval gate is a genuine compensating control and a hobbled supervised agent is useless. An agent that runs unattended is held to the minimum its task requires, because it has no such backstop. The reference configurations will demonstrate this oversight-calibrated posture.

An agent is invoked in one of two modes. In delegated mode, an agent acts on behalf of a user, and its effective authority is the intersection of the agent's role and the user's, the lesser of the two. In system mode, there is no invoking user, and the agent's own role is the entire boundary. Both modes resolve through the same permission evaluation path as every other principal.

## The Model Context Protocol Server

Wax exposes a Model Context Protocol server using the official C# SDK, which has reached a stable release developed in collaboration with Microsoft. The server is a thin adapter, not a parallel capability system. MCP tools map onto existing commands and the pluggable action types from [Wax Design Decision 23](WAX-0023-workflow-automation-engine.md), which already declare typed input and output schemas, and onto the published API catalog from [Wax Design Decision 18](WAX-0018-access-control.md). MCP resources map onto row-level-security-filtered queries and views. A tool call executes as the agent's principal through the ordinary command path, so it inherits access control, row-level security, hash-chained audit, and pre-event guardrails without any AI-specific enforcement. This decision covers the platform acting as an MCP server, the inward direction. The platform acting as an MCP client, calling out to AI through workflow action types, is addressed with the HiveAR implementation and the generative-content decision.

## Security Posture and the Untrusted-Input Rule

The AI ecosystem has seen a wave of serious vulnerabilities around tool poisoning, indirect prompt injection, and exfiltration through model sampling. The platform's defense is structural rather than a filter bolted on afterward. Because an agent is a principal bounded by access control and row-level security, a manipulated agent still cannot read a record row-level security hides, take an action its role forbids, or bypass a pre-event rejection. The blast radius of a compromised or misled agent is exactly its principal's authority, no more, which is why distinct, narrowly scoped agents matter.

Data an agent ingests, account notes, dispute text, document contents, and transcripts, is treated as untrusted input that can never elevate the agent's authority or redirect it past its permission boundary. Tool and resource descriptions are likewise untrusted. The principal model is the backstop that holds these guarantees regardless of what an agent is told or fed.

## Propose and Approve Through the Existing UI

The central pattern for AI accelerating human work is propose-and-approve. An agent invoked by a user prepares an action and presents it for approval in the normal interface, and the human commits it. A request to mark an account bankrupt fills in the bankruptcy action and shows it for a save. A request to send a payment-past-due email composes a draft from the account's payment history and shows it for approval. A systems request such as creating an event handler that texts a template seven days after a missed payment if unrecovered navigates to the workflow designer, builds the proposed workflow, and presents it in the same designer the administrator would have used by hand. The pattern is not a special AI screen; the agent drives the existing interfaces and stops at the save button. The approval gate is configurable by action sensitivity and rides the approval and pre-event mechanisms already in the platform.

## Retrieval: Knowledge, Not Accounts

Retrieval is reserved for the shared, stable, non-personal knowledge corpus: regulations, compliance documentation, agency policies, and platform knowledge. A collector who asks what to do when a consumer mentions bankruptcy gets an answer grounded in the agency's own written procedures. Structured platform data, accounts, events, and balances, reaches the agent through MCP tools over the row-level-security-filtered query API, exact and current and permission-bounded, never through embeddings.

A single account does not hold enough unstructured text to justify embedding it. Its notes, transcripts, and OCR text are small enough that the model reads them directly through the tools at query time. Embedding consumer-personal text would mint a derived, decrypted copy of that information in vectors that would then require row-level-security scoping and reachability by cryptographic erasure, so it is deliberately deferred and approached cautiously. The mass-query case, reasoning across all calls or all documents in a range, belongs to the document store and is far down the road. Vectors live in PostgreSQL through the pgvector extension, which has matured into a production vector store, so there is no separate vector service, consistent with [Wax Design Decision 3](WAX-0003-database-platform.md). Embedding generation is one more asynchronous step on the document processing pipeline from [Wax Design Decision 30](WAX-0030-document-storage.md).

## Pluggable, Co-Equal Model Providers

The language model and the embedding model sit behind a provider interface that speaks the OpenAI-compatible API shape, the de facto standard that local runtimes and cloud APIs both expose. An agency points the interface at a local runtime such as Ollama or vLLM, or at a cloud API, by configuration. Self-hosted and cloud are co-equal. Self-hosted keeps all data on the agency's own infrastructure, while cloud reaches more capable frontier models under enterprise agreements that bar training on customer data and hold data-protection standards high. The platform surfaces the data-egress consideration at configuration so the choice is informed, and it neither defaults to nor discourages either path.

## Autonomous Buildout: Sandbox Now, Production Later

A hands-free agent holding configuration-write tools can build large portions of a system autonomously, user-defined tables, workflows, file imports and exports, reports, and job schedules, across many steps, and then present the whole result for review. This is the platform's strongest adoption lever, because it lets a prospective agency evaluate the system without first having to learn it. An evaluator spins up a sandbox, asks for a medical-debt collections setup with specified letters and rules, and watches the configuration assemble. For software this capable and this complex, letting someone judge it before climbing the learning curve materially lowers the barrier to adoption, which is squarely on the Foundation's mission of lowering the barrier to capable infrastructure.

The capability divides by what makes the autonomy safe. The sandbox builder operates in an isolated instance with synthetic data, where the environment itself is the safety boundary and review is simply inspection of what was built. It carries no risk to any production system and ships as a Wax v2 beta, delivered alongside the reference and sandbox tooling. The production builder is the same agent pointed at a live agency's configuration, and it draws its safety from building in a development instance and promoting the entire batch to production through the diff-and-review path described in the System-to-System Configuration Promotion decision. The production builder is v3, riding that promotion path, and it cannot alter a live configuration until a human approves the promotion.

The read-only sibling of this capability, asking an agent to summarize the agency's workflows or find gaps in them, carries no write risk, rides the v2 MCP-over-queries surface, and is a low-stakes way to prove the value early.

## Engine and Domain Split

This decision is the Wax infrastructure: the principal and security model, the MCP server, the retrieval and embedding plumbing, and the provider seams. The separate HiveAR AI toolbox implementation supplies the AR-specific tools exposed, the AR compliance corpus that is embedded, and AR-specific agent behavior. Generative consumer-facing content, an AI composing member-facing texts, emails, letters, chat, and voice, is the highest-compliance-exposure surface in the platform and is a distinct HiveAR decision with its own content, review, and approval controls. This infrastructure leaves the seam open for it through the action-type mechanism without specifying it.

## Implementation Phasing

**Wax v2 (core):** AI agents as principals with multiple distinct identities, oversight-calibrated least privilege, delegated and system invocation modes, AI-attributed hash-chained actions, and pre-event guardrails. The MCP server over existing commands and row-level-security-filtered queries. The propose-and-approve human-in-the-loop pattern. Knowledge-corpus retrieval over pgvector with embedding on the document pipeline. Pluggable, co-equal model providers. The read-only analytical capability. The sandbox autonomous builder as a beta alongside the reference and sandbox tooling.

**Wax v2 enhancement or v3:** Hybrid and reranked retrieval.

**Wax v3+:** The production autonomous builder riding the configuration-promotion path. Cautious embedding of personal content with cryptographic-erasure reach and vector-level row-level security. The platform acting as an MCP client and AI workflow action types, woven with the HiveAR implementation and the generative-content decision. Richer MCP capabilities such as sampling and elicitation.

**Breaking change risk: LOW. AI agents reuse the existing principal, audit, and access-control model rather than introducing a parallel one. Retrieval and embedding are additive layers, and the model provider interface is swappable.**

## Implications For Contributors

AI agents are principals, never exceptions. An agent reaches platform capability only through the same commands, queries, access control, row-level security, and audit path as any other principal. No code may grant an agent a capability outside its roles or a read past row-level security.

Ingested content is untrusted. Data an agent reads cannot change what it is permitted to do. Tool descriptions, resource contents, and account text are input, not instructions that alter authority.

Retrieval is for non-personal knowledge. A contributor must not embed consumer-personal text into the vector store. Account-specific data reaches the agent through row-level-security-filtered tools, not through embeddings.

Autonomous configuration changes never reach production unreviewed. A hands-free builder operates in a sandbox or promotes through the reviewed promotion path. It does not mutate a live configuration directly.
