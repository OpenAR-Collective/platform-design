---
id: WAX-0005
title: "Naming Conventions"
status: Accepted
version: 1.0
area: wax
date: 2026-08-30
supersedes: none
license: CC-BY-4.0
---

# Wax Design Decision 5: Naming Conventions

## Decision

All database object names across the core schema and all modules will follow verbose snake_case. Abbreviations in table names, column names, schema names, index names, and all other database object names are prohibited, with the sole exception of object type prefixes, which are classifiers rather than abbreviations. Table names are always singular. Primary keys, foreign keys, and surrogate key conventions follow the rules defined below.

## Verbose Snake Case

Names are written in lowercase with underscores as word separators. Words are spelled out in full. The goal is immediate readability by any contributor, including contributors new to the industry, without reference to an abbreviation dictionary.

> **EXAMPLES: CORRECT VS. PROHIBITED**
>
> account_balance, not acct_bal or acct_balance social_security_number, not ssn date_of_birth, not dob original_creditor_name, not orig_cred_nm last_payment_amount, not last_pmt_amt consumer_address_line_one, not addr_ln_1

## No Exceptions for Industry Terms

Even terms that feel universally understood within the accounts receivable industry, such as ssn or dob, are excluded from the abbreviations list for two reasons. First, HiveAR is an open-source project and will attract contributors from adjacent technical communities who do not share the same mental dictionary. Second, modern development tooling including database clients, code editors, and query tools provides autocomplete, which eliminates any meaningful typing burden associated with verbose names. The savings from abbreviation are negligible; the readability cost is real. Only documented universal abbreviations are allowed in the database, such as pk for primary keys and idx for indexes, as described in the object type prefixes below.

## Singular Table Names

All table names will be singular. A table defines an entity type, not a collection of rows. This convention is adopted for a Wax-specific reason that goes beyond general preference: the naming system for primary and foreign keys depends on the table name as its root. With singular table names, the root is consistent at every level.

> **WHY SINGULAR PRODUCES CLEAN KEY NAMING**
>
> Table: account. Primary key: account_pk. Foreign key in any other table: account_fk. The table name, the primary key root, and the foreign key root are all identical: account. With a plural table name (accounts), the key root (account) differs from the table name. Contributors must mentally singularize the table name to derive the key name. Singular eliminates that step entirely. Reading account_fk, any contributor immediately knows it references account.account_pk without having to reason about pluralization.

## Primary Keys

Every table will have exactly one primary key column. The column will be named using the table name as the root, followed by the _pk suffix. Primary keys will always be UUID surrogate keys. Natural or composite primary keys are not permitted.

> **PRIMARY KEY EXAMPLES**
>
> account.account_pk contact.contact_pk payment.payment_pk account_collector_assignment.account_collector_assignment_pk

## Foreign Keys

Foreign key columns will be named using the root of the primary key they reference, followed by the _fk suffix. The root must exactly match the root of the referenced primary key column. This makes the relationship self-documenting: any contributor can identify what a foreign key references by reading its name alone.

> **FOREIGN KEY EXAMPLES**
>
> account_fk references account.account_pk contact_fk references contact.contact_pk payment_fk references payment.payment_pk

## Surrogate Keys And Composite Uniqueness

Every table carries a UUID surrogate primary key as its sole primary key column. Business or natural composite keys are never used as primary keys. Where the domain requires that a combination of fields be unique (for example, an account may have only one active assignment at a time), that uniqueness is enforced through a unique constraint or unique index, not through a composite primary key. This keeps the foreign key referencing convention uniform across the entire schema and eliminates a category of contributor confusion.

## Object Type Prefixes

Object type prefixes are permitted and encouraged. These are type classifiers, not abbreviations. They communicate what kind of database object a name refers to before the name is read, which is useful in query output, documentation, and tooling. The approved prefixes are:

| **Prefix** | **Object Type** | **Example** |
| --- | --- | --- |
| vw_ | View | vw_active_accounts |
| fn_ | Function | fn_calculate_aging_bucket |
| sp_ | Stored procedure | sp_apply_payment |
| idx_ | Index | idx_accounts_assigned_collector |
| trg_ | Trigger | trg_accounts_after_update |
| seq_ | Sequence | seq_account_number |

## Enforcement

Naming convention compliance is enforced at two tiers. Code review is the primary mechanism: every pull request that introduces or modifies database object names is reviewed against the conventions defined in this decision. Any proposed exception requires a documented rationale and explicit approval in the pull request review, and exceptions will not be accepted on the basis of typing convenience.

Automated enforcement supplements code review through an AI-powered linter that runs in the continuous integration pipeline on every pull request. The linter is scoped to schema and migration SQL: it parses each new or modified database object name (table, column, schema, index, view, function, stored procedure, trigger, and sequence) and evaluates it against the rule set in this decision, including the prohibition on abbreviations, the singular table name requirement, the verbose snake_case convention, the foreign key and primary key suffix conventions, and the object type prefix table.

The linter uses a large language model rather than a deterministic rule engine for the abbreviation check, because identifying an abbreviation is a language comprehension problem rather than a pattern matching problem. The model receives the relevant portion of this decision as its system context, plus a curated table of acceptable and unacceptable example names, and returns a structured verdict for each candidate name in the diff.

To control cost and reduce variance over time, every verdict the model returns is appended to a verdict cache file committed to the repository. The cache maps each adjudicated token to its approved or rejected status with a brief reason. Subsequent pull requests resolve against the cache first and call the model only for tokens never previously adjudicated. Over time, the cache becomes a living record of the project's accepted vocabulary, and the rate of model calls converges toward zero for steady-state development.

The implementation is built on the GitHub Models inference platform via the actions/ai-inference GitHub Action, which removes the need to manage an external API key. The linter consists of a prompt file containing the rules and the example table, a GitHub Actions workflow that invokes the inference action on pull requests, and the verdict cache file. The linter posts a comment on the pull request identifying any violations, with the reviewer remaining the final gate.

## Implementation Phasing

**Wax v1 (MVP):** Full implementation. Naming conventions cost nothing to implement and are extremely expensive to change later. Ship the full convention set from day one. Enforcement is the two-tier approach defined above: code review on every pull request, supplemented by the AI-powered linter scoped to schema and migration SQL.

**Breaking change risk: NONE if done right. CATASTROPHIC if deferred.**
