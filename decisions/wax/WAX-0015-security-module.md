---
id: WAX-0015
title: "Security Module"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 15: Security Module

## Decision

Wax will ship a distinct, self-contained component called the Wax Security Module (WSM). The WSM is the platform's sole authority for all cryptographic operations. Application code, modules, and contributors never implement cryptographic logic directly. They call the WSM through a narrow, stable interface. The WSM also owns the enforcement of all integrity-critical operations: event chain hashing, checkpoint anchoring, break-glass authorization, and key lifecycle management. Its pre-compiled binary is distributed separately from the rest of the platform and is governed by the code integrity architecture in [Wax Design Decision 15](WAX-0015-security-module.md).

## Purpose and Scope

Two motivations drive the WSM design. The first is security correctness. Cryptographic operations are notoriously easy to implement incorrectly in ways that appear to work while being fundamentally insecure: wrong key lengths, insecure padding modes, improper IV reuse, timing side channels, and many others. Having one implementation, authored and reviewed by the Collective, eliminates the risk of contributors introducing cryptographic defects across dozens of independently written modules.

The second is contributor accessibility. Module authors who need to handle a PII field should not need to understand AES-GCM key derivation. They should annotate the field and call a named interface method. The complexity lives inside the WSM. The interface is simple typed operations with names that describe what they do in business terms rather than cryptographic ones.

## Cryptographic Operations Owned by the FSM

All of the following operations are implemented exclusively inside the WSM. No code outside the WSM may implement equivalent functionality independently.

> **FSM CRYPTOGRAPHIC RESPONSIBILITIES**
>
> **PII field encryption**: accepts a plaintext field value and a subject identifier, returns ciphertext. Selects the algorithm, generates the IV, retrieves the subject's key from the key store, and produces authenticated ciphertext. The caller never sees or handles key material.
>
> **PII field decryption**: accepts ciphertext and a subject identifier, returns plaintext or a typed inaccessible indicator if the subject's key has been destroyed.
>
> **Key generation**: generates per-subject encryption keys on first encounter with a new subject identifier. Keys are generated inside the WSM and stored in the WSM's key store. They never leave the WSM in plaintext.
>
> **Key lifecycle management**: assigns retention dates to subject keys, executes scheduled key destruction per the retention workflow, and records every lifecycle event to the key audit log.
>
> **Key destruction**: destroys a subject's encryption key on schedule or via the break-glass process. Records the destruction to the tamper-evident key audit log with a timestamp and the authorizing path.
>
> **Event hash computation**: computes the SHA-256 hash of an event payload and prior_event_hash before the event is committed. Returns the hash values for storage in core.event. Application code cannot write an event that bypasses this computation.
>
> **Checkpoint hash computation and submission**: computes the delta checkpoint hash over the declared sequence number window and submits it to the configured RFC 3161 TSA. Stores the returned token in the checkpoint table.
>
> **Checkpoint verification**: walks the checkpoint sequence, recomputes hashes, and verifies TSA tokens against the cached public certificate. Returns a structured verification report.
>
> **Break-glass authorization**: enforces the two-person authorization requirement for privileged chain operations. Collects the request, stores it pending approval, verifies the approving administrator's credential, and executes the authorized operation only after both conditions are satisfied.
>
> **Break record creation**: generates and stores the signed break record with RFC 3161 anchoring after a break-glass operation executes.
>
> **Key audit log writes**: records all key lifecycle events to the tamper-evident key audit log. The key audit log is maintained using the same hash chain architecture as core.event.

## Interface Design Principles

The WSM interface is designed so that the correct path is also the easy path. Every interface method accepts business-meaningful parameters rather than cryptographic parameters. The caller specifies what they want done in domain terms. The WSM decides how to do it cryptographically.

The interface is intentionally narrow. There are no methods that expose key material, algorithm configuration, or cryptographic primitives to callers. There is no escape hatch through which application code can reach into the WSM's internals. The interface is the complete boundary between the WSM and the rest of the system.

When a key has been destroyed (as part of retention-triggered erasure), the WSM's decryption method returns a typed inaccessible result rather than throwing an unhandled exception. The caller receives a clear indication that the field exists, that it was encrypted, and that it is no longer accessible, allowing the application to handle the condition gracefully, for example by displaying a compliance notice rather than an error message.

## The Interface Boundary as a Secondary Integrity Mechanism

Because all cryptographic operations pass through the WSM, the WSM can enforce invariants that application code cannot circumvent through the normal interface. An event cannot be written to core.event without the WSM computing its hash. A key cannot be destroyed without the WSM recording the destruction. A break-glass operation cannot execute without two-person authorization passing through the WSM's enforcement logic.

If an agency modifies application code in a way that attempts to write directly to tables the WSM owns, bypassing the interface, the WSM's internal hash chains detect the discrepancy at the next verification run. The bypass does not succeed silently. The architectural boundary between the WSM and the application is itself a detection mechanism.

## Deployment and Distribution

The WSM is distributed as a pre-compiled, code-signed binary for all supported platforms: Windows Server x64, Linux x64, and common cloud VM images. It is included in the standard HiveAR installer and is also available as a standalone download from the Collective's GitHub releases page and website. The WSM binary is versioned independently of the rest of the platform. When the Collective releases a new WSM version, it is distributed through the same channels and agencies update it independently of their application code deployments.

Agencies running the standard HiveAR installer use the pre-compiled WSM binary directly. Agencies that have built custom versions of HiveAR's application code continue to use the Collective's pre-compiled WSM binary. The WSM is never expected to be recompiled by an agency. Its source is published for transparency and audit, and changes to it are accepted only through the Collective's contribution process. The code integrity architecture governing the WSM binary is documented in [Wax Design Decision 15](WAX-0015-security-module.md).

## Relationship to the Standard Installer and Custom Deployments

The HiveAR will be distributed as a standard installer package containing all pre-compiled components including the WSM. This is the intended deployment path for the majority of agencies. The installer handles component version compatibility, initial configuration, and the WSM's key store initialization.

Agencies that choose to take advantage of HiveAR's open-source nature, for example to build custom modules, modify UI components, or extend the platform's capabilities, deploy their custom application code alongside the Collective's pre-compiled WSM binary. The WSM and the custom application code are independently deployable and independently versioned. The agency's custom code calls the WSM through the published interface in the same way that all Collective-authored code does. There is no distinction from the WSM's perspective between Collective code and agency-authored code on the other side of the interface.

## Implementation Phasing

**Wax v1 (MVP):** Not implemented as a separate component. Cryptographic operations (password hashing, token signing) are handled by standard .NET libraries within the application. No separate WSM binary, no reproducible build infrastructure, no code integrity verification.

**Wax v2:** WSM extracted as a distinct component with a narrow interface. Pre-compiled binary distribution. Reproducible build specification.

**Wax v3+:** Runtime self-attestation. Code signing. Binary hash publication.

**Breaking change risk: MEDIUM.** The interface boundary must be designed in v1 even if the separate binary does not ship. If v1 scatters cryptographic operations throughout the codebase, extracting them into the WSM in v2 becomes a refactoring project.

## Implications For Contributors

No module or Wax component may implement cryptographic operations directly. All encryption, decryption, hashing, key management, and integrity-critical operations must go through the WSM interface.

PII field annotation in the payload schema is how a contributor declares that a field requires FSM-managed encryption. The serialization layer calls the WSM automatically based on the annotation. Contributors do not call encryption methods directly.

The WSM interface is a stable contract. Breaking changes to the interface require a major version increment and a documented migration path. Contributors must not design module code that depends on FSM internals rather than the published interface.

Any proposed change to WSM source code goes through an elevated review process within the Collective's contribution workflow. WSM changes require security review in addition to standard code review. Changes that alter the cryptographic operation of the WSM require independent cryptographic review before acceptance.

The WSM's key store is the WSM's exclusive property. No module, no admin tool, and no migration script may read from or write to the key store outside of the WSM interface. Direct key store access is a schema violation.

## Code Integrity Verification

## Decision

The Collective will publish verified cryptographic hash values for each released version of the Wax Security Module binary for every supported platform. The WSM binary will be code-signed with the Collective's certificate. The WSM source will carry prominent notices establishing that modification voids the integrity guarantees the WSM provides. Binary hash comparison against Collective-published values provides forensic detectability of any unauthorized modification. Agencies run the Collective's pre-compiled WSM binary. The source is published for transparency and audit, not for agency recompilation.

## The Problem This Addresses

HiveAR is open-source software. Every agency that installs it has the full source code. A sophisticated actor who wanted to undermine the integrity guarantees described in [Wax Design Decision 13](WAX-0013-event-chain-integrity-and-tamper-evidence.md) and [Wax Design Decision 15](WAX-0015-security-module.md) could modify the WSM source, recompile it, and run the modified version. They could remove the two-person authorization check from the break-glass workflow. They could modify the checkpoint submission code to silently skip TSA submission. They could alter the key audit log to omit entries. These modifications would appear operationally normal from the inside.

The purpose of the code integrity architecture is not to make these modifications impossible. Open-source software is, by definition, modifiable. The purpose is to make unauthorized modifications forensically detectable, to make the detection path available to any independent examiner without requiring Collective cooperation, and to establish clearly that an agency running a modified FSM is operating outside the Collective's integrity attestation.

## Binary Hash Publication

For each Collective release, the Collective publishes a signed manifest listing the SHA-256 hash of the WSM binary for each supported platform: Windows Server x64 DLL, Linux x64 shared object, and any additional platform targets. The manifest is published in the Collective's GitHub release notes, in the Collective website's security page, and anchored with an RFC 3161 timestamp to establish the publication date. The manifest signing key is the Collective's code signing certificate, verifiable against the Collective's published certificate fingerprint.

Any party, including a forensic examiner, a regulator, opposing counsel in litigation, or a curious agency administrator, can take the WSM binary from any Wax installation, compute its SHA-256 hash, and compare it to the Collective's published hash for the version the installation reports it is running. A match means the binary is unmodified. A mismatch means the binary was altered after the Collective released it, regardless of what explanation is offered.

## Code Signing

The WSM binary is signed with the Collective's code signing certificate before distribution. On Windows Server, the Authenticode signature can be verified by the operating system before the binary is loaded. A deployment policy requiring a valid Collective signature on the WSM binary provides a runtime check that actively prevents loading a modified binary, rather than only detecting the modification forensically after the fact.

On Linux, equivalent runtime enforcement can be achieved through application-level signature verification at load time: the HiveAR application verifies the WSM binary's signature against the Collective's certificate before initializing the WSM interface. A signature verification failure at startup prevents the application from running rather than running with an unverified FSM.

A modified WSM binary will not carry the Collective's signature because the Collective's private signing key is never distributed. An actor who modifies the binary could sign it with their own certificate, but that certificate is not the Collective's and the substitution is detectable by comparing the signing certificate to the Collective's published certificate fingerprint.

## Reproducible Builds

The Collective will publish reproducible builds: given the Collective's published source code and build environment specification, the compiled output will be identical byte-for-byte to the Collective's published binary. The .NET build system supports reproducible builds through compiler flags that eliminate non-deterministic elements such as embedded timestamps and random module versioning identifiers. The Collective's build environment specification documents the exact compiler version, target framework, and build flags required to reproduce the published binary.

Reproducible builds serve two purposes. First, they allow any party to verify independently that the Collective's published binary corresponds to the Collective's published source, confirming that the Collective has not distributed a binary containing code not present in the public source. Second, they establish the baseline for hash comparison: an agency that has correctly reproduced the build will obtain a binary hash identical to the Collective's published hash, confirming their build environment is correct before they run the WSM.

Reproducing the build correctly requires precisely matching the Collective's build environment, which is non-trivial. This is intentional. An agency that successfully compiles the WSM source and obtains a binary that does not match the Collective's hash has made a build environment error, not a source modification. The correct resolution is to use the Collective's pre-compiled binary rather than continue troubleshooting the build environment. The reproducible build capability exists for independent verification, not as a routine deployment path.

## Runtime Self-Attestation

At startup, the WSM computes a SHA-256 hash of its own loaded assembly and writes the result to the key audit log. This creates a permanent, tamper-evident record of which version of the WSM was running at any given point in time. The key audit log is itself hash-chained and checkpoint-anchored, so the self-attestation record cannot be silently altered after the fact.

If the running WSM binary has been modified from the Collective's published version, the self-attested hash will not match the Collective's published hash for the reported release version. Any party examining the key audit log can identify the discrepancy. An actor who modifies the WSM and also modifies the self-attestation code to report the correct original hash is making a second modification that changes the binary hash further, increasing the evidence of tampering rather than concealing it.

## In-Source Notices

The WSM source files carry prominent notices at the top of each file establishing the Collective's position clearly. The notices state that: the WSM is open-source software licensed under the Collective's published license; the source is made available for transparency, independent audit, and contribution through the Collective's contribution process; agencies are expected to run the Collective's pre-compiled, signed binary rather than compile this source themselves; any modification to this file, including modification of these notices or of comments, will produce a binary that does not match the Collective's published hash values for this release; running a modified WSM binary voids all integrity guarantees described in the platform documentation; and modification is forensically detectable through binary hash comparison against Collective-published values.

These notices serve a legal and forensic purpose beyond deterrence. They establish that any agency running a modified FSM was on notice of the consequences. An agency that modifies the WSM after reading these notices cannot later claim they were unaware that modification was detectable or that it invalidated the integrity guarantees. The notices, published in the open-source repository with a public timestamped commit history, are themselves a public record.

## Certification Implications

Running the Collective's unmodified WSM binary, verified by its published hash, will be a condition of Platform Integration certification and Hosting certification. An agency or vendor that claims certification while running a modified FSM is making a false certification claim. This is a breach of the certification agreement and may carry additional legal implications in jurisdictions where certification claims are subject to consumer protection or professional standards regulation.

Certified hosting vendors are additionally expected to make the WSM binary hash of their hosted installations available to agency clients on request, allowing clients to independently verify that the integrity infrastructure protecting their data has not been modified.

## What Cannot Be Prevented

A sufficiently determined actor with full system access, deep security expertise, and sustained access could in principle cover their tracks: modify the WSM, falsify the self-attestation through a second modification, replace the Collective's signing certificate in the system trust store, scrub filesystem forensic artifacts, and recompute the key audit log hash chain to reflect the modified self-attestation. This is a sophisticated multi-step operation that itself leaves forensic traces at each step and is qualitatively different from casual or opportunistic tampering.

The goal of this architecture is not to make FSM modification impossible. It is to make unauthorized modification expensive, multi-step, leave its own evidence trail, require sustained privileged access, and be legally and contractually consequential. These properties together make FSM modification a serious undertaking rather than a casual act, which is the appropriate deterrent for a compliance-sensitive platform in a regulated industry.

## Implications For Contributors

WSM source changes go through an elevated contribution process including mandatory security review and, for cryptographic changes, independent cryptographic review. Standard pull request review is not sufficient for WSM changes.

Every WSM release requires a corresponding signed hash manifest publication on GitHub and on the Collective website before the release is considered complete. Hash publication is a required release step, not an afterthought.

The Collective's build environment specification for WSM compilation must be kept current with the actual build environment used to produce released binaries. A specification that does not reproduce the published binary is a documentation defect.

FSM in-source notices must not be removed, shortened, or modified. They are part of the Collective's published legal position and are subject to the same elevated review process as all other WSM source changes.
