# Key Principles

These principles govern every decision in this repository. A proposal that conflicts with one of them needs to argue with the principle, not ignore it.

- **Compliance-first, not compliance-guaranteeing**. HiveAR builds the infrastructure for compliant workflows. Agencies configure and operate that infrastructure in accordance with their own legal obligations. The Collective does not accept liability for compliance outcomes.

- **Doing things right the first time**. Architectural decisions are made with deliberate care because retrofitting foundational choices is costly. The depth and thoroughness of this document reflect that philosophy.

- **Open source with integrity**. Both Wax and HiveAR are open source and agencies may modify them freely. The Wax Security Module is also open source for transparency and audit, but is distributed as a signed pre-compiled binary whose modification is forensically detectable. This is not a contradiction: it is the correct balance between community transparency and operational integrity.

- **Core Schema Neutrality**. The core schema owns no locale-specific data. Address conventions, identity number formats, and name component structures are contributed by Locale Modules. A US-focused platform is not a universal one, and Wax is designed to be both.

- **Events and workflows as the primary engine**. The event sourcing architecture and the workflow automation engine are the mechanisms through which almost all system behavior is expressed. Understanding these two foundations unlocks everything else.

- **Framework stability over convenience**. Wax is designed to stabilize early. HiveAR evolves as the AR domain model matures. A change to Wax ripples into every application built on it; the cost of a change increases as it moves down the stack.
