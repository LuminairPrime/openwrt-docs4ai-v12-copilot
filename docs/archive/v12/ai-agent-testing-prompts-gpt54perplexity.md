"ai-agent-testing-prompts.md"

````markdown
# AI Agent Prompt Pack: Python Scrape / Process / Output Pipeline Testing

## Purpose

This file collects a set of reusable prompts for AI programming agents to analyze, test, and harden a Python pipeline that:

- scrapes input data
- parses and transforms it
- validates and deduplicates it
- writes final output artifacts

## Suggested Use

- Give one prompt at a time to one agent.
- Give the same prompt to multiple agents and compare results.
- Provide the full script or repo plus a short pipeline description.
- Prefer deterministic local fixtures over live network access when possible.
- Save all discovered failures as regression tests.

## Prompt Index

### Static analysis
1. Static correctness / dataflow audit
2. Static security / robustness audit
3. Static control-flow / dead-code / output-integrity audit
4. Static config / schema / flag-contract audit

### Fuzz testing
5. Mutation / coverage-guided fuzzing
6. Property / metamorphic fuzzing

### Property-based testing
7. Schema / invariant property testing
8. Metamorphic / round-trip property testing

### Symbolic execution
9. Concolic / path-exploration symbolic execution
10. Goal-directed / sink-targeted symbolic execution

### Model checking
11. State-machine / temporal-property model checking
12. Bounded reachability / fault-combination model checking

### Mutation testing
13. General mutation testing for test-suite strength
14. Domain-specific mutation testing for scrape pipelines

### Differential testing
15. Independent reference-implementation differential testing
16. Cross-version / cross-mode differential testing

---

<!--
Test type: Static analysis — correctness, dataflow, typing, and silent corruption review.
Good for: Hidden logic bugs, weak assumptions, type drift, None/empty handling mistakes, and output-integrity problems.
Typical output: pipeline map, findings table with severity and fixes, top-risk bugs, invariants to enforce, and refactor suggestions.
-->
## 1) Static Analysis — Correctness / Dataflow Audit

```text
You are performing a static correctness analysis of a Python data pipeline that scrapes input data, transforms it, validates it, and writes output files.

Your job is to review the code without executing it and find likely bugs, weak assumptions, edge cases, and maintainability problems.

Focus on these areas:
- End-to-end dataflow: trace data from scrape/input stage to parse stage to transform stage to output stage.
- Type consistency: identify values whose types may vary across functions, branches, exception paths, or empty-result cases.
- None/empty handling: look for missing checks on None, empty lists, empty dicts, missing keys, blank strings, NaN-like values, and failed lookups.
- Schema drift: find places where the code assumes input fields, HTML structure, JSON keys, CSV columns, or object attributes always exist.
- Control-flow gaps: find code paths where variables may be used before assignment, overwritten unexpectedly, or partially initialized.
- Error masking: flag broad except blocks, ignored return values, fallback behavior that hides bugs, and retry logic that can produce stale or partial data.
- Output integrity: find ways the pipeline could write incomplete, duplicated, truncated, unsorted, or internally inconsistent output while still appearing to succeed.
- State and mutation: check for in-place mutation of shared dicts/lists, aliasing bugs, reuse of mutable defaults, and accidental cross-record contamination.
- Idempotence: identify steps that may produce different outputs on rerun from the same inputs.
- Function contracts: infer what each function expects and returns; flag mismatches between caller assumptions and callee behavior.

Instructions:
1. Read the whole script first and identify the pipeline stages.
2. Build a short mental model of data structures used between stages.
3. Report only issues that are plausibly real from static inspection; do not pad with style nits.
4. For each issue, include:
   - Severity: critical / high / medium / low
   - Category: typing, dataflow, control flow, validation, output integrity, mutation, error handling, dead code, maintainability
   - Exact code location
   - Why it is risky
   - A concrete failure scenario
   - A minimal fix
5. After listing issues, provide:
   - Top 5 highest-risk bugs
   - Suggested type annotations or TypedDict/dataclass models to add
   - Assertions or invariants that should be enforced between stages
   - A short list of functions that should be split or simplified

Be especially suspicious of:
- scrape failures that become empty successful outputs
- partial records being treated as valid
- deduplication logic that can drop good records
- timestamp, encoding, and normalization inconsistencies
- assumptions that test data covers real-world weirdness

Output format:
- Pipeline map
- Findings table
- Highest-risk fixes first
- Suggested invariants
- Suggested refactors
```

<!--
Test type: Static analysis — security and robustness review.
Good for: Trust-boundary mistakes, unsafe parsing, filesystem and network hazards, denial-of-service risks, and false-success recovery behavior.
Typical output: trust-boundary map, ranked findings table, hardening checklist, safer helper patterns, and missing validation rules.
-->
## 2) Static Analysis — Security / Robustness Audit

```text
You are performing a static security and robustness analysis of a Python scraping-and-processing pipeline.

Review the code without running it. Assume the pipeline interacts with untrusted external inputs such as web pages, APIs, files, environment variables, config files, command-line args, and previously generated intermediate data.

Focus on these areas:
- Trust boundaries: identify where untrusted data enters the system and where it is trusted too early.
- Dangerous parsing and deserialization: flag risky use of eval, exec, pickle, yaml loaders, HTML/XML parsers, regexes vulnerable to pathological input, and unsafe subprocess construction.
- Path and file safety: inspect path joins, temp files, overwrites, deletes, globbing, archive extraction, relative paths, and output paths influenced by external data.
- Injection risks: shell injection, SQL injection, template injection, command construction with string formatting, unsafe URL construction, and log injection.
- Requests and network hygiene: missing timeouts, unchecked status codes, redirect assumptions, retry storms, bad backoff, broken cache assumptions, and weak content-type validation.
- Resource exhaustion: unbounded memory growth, huge response bodies, recursive parsing, quadratic loops, giant string concatenation, and infinite pagination / retry loops.
- Error and recovery behavior: broad exception handling, swallowed exceptions, partial writes, inconsistent cleanup, and “success” states after internal failure.
- Secrets and privacy: accidental logging of credentials, tokens, cookies, full response bodies, or sensitive fields in output artifacts.
- Concurrency and race conditions: output file clashes, shared temp names, non-atomic writes, and inconsistent state if interrupted.
- Supply-chain and dependency assumptions: risky imports, version-sensitive parsing logic, and libraries used in unsafe default modes.

Instructions:
1. Map all external inputs, side effects, and output sinks.
2. Flag only substantive issues and rank by exploitability or production impact.
3. For each finding, include:
   - Severity: critical / high / medium / low
   - Risk type: injection, unsafe parsing, filesystem, network robustness, denial of service, secret exposure, race condition, dependency risk
   - Exact code location
   - Why the pattern is dangerous
   - A realistic bad-case scenario
   - A safer replacement or patch pattern
4. Then provide:
   - A prioritized hardening checklist
   - Guardrails to add immediately
   - Safe wrapper/helper functions the codebase should standardize on
   - Missing validation rules for inputs and outputs

Be especially suspicious of:
- output filenames derived from scraped data
- requests without timeout or content validation
- regex-heavy parsing on attacker-controlled text
- archive, JSON, HTML, or YAML parsing with implicit trust
- logging that dumps raw payloads on failure
- cleanup or retry code that can corrupt outputs

Output format:
- Trust-boundary map
- Findings table
- Immediate hardening actions
- Safer coding patterns to adopt
```

<!--
Test type: Static analysis — control-flow truth audit.
Good for: Dead code, unreachable branches, contradictory success logic, dead validation, and “looks successful but output is wrong” paths.
Typical output: control-flow map, success/failure exit map, findings table, output-integrity assertions, and cleanup/refactor list.
-->
## 3) Static Analysis — Control-Flow / Dead Code / Output-Integrity Audit

```text
You are an AI programming agent performing a static control-flow and output-integrity audit of a Python pipeline that scrapes data, parses it, transforms it, validates it, and writes output artifacts.

Goal:
Find dead code, unreachable branches, contradictory conditions, fake-success paths, and static signs that the pipeline can appear to succeed while producing wrong, partial, stale, duplicated, or internally inconsistent output.

Do not run the code. Infer behavior from control flow, dataflow, conditionals, exception handling, return values, and output-writing logic.

Focus on these areas:
- Dead code: functions, branches, conditions, fallback paths, retries, handlers, or validations that can never execute or are effectively inert.
- Unreachable branches: mutually contradictory conditionals, always-true / always-false predicates, shadowed branches, and logic that is bypassed by earlier returns or exceptions.
- False-success paths: code paths that mark a run successful even when scrape, parse, validate, dedupe, or write stages partially failed.
- Integrity gaps: places where output can be written despite missing records, failed validation, stale intermediates, or mismatched counts.
- Silent bypasses: flags, defaults, try/except blocks, or early returns that skip important checks without surfacing failure.
- Contradictory success criteria: places where “completed”, “valid”, “non-empty”, and “written” are treated as interchangeable when they are not.
- Dead validation: validators whose result is ignored, warnings that should be fatal, or checks that log issues but allow invalid output onward.
- Partial-state hazards: code that leaves output directories, temp files, caches, or in-memory state in a misleading “looks complete” state.
- Output integrity invariants: row counts, unique IDs, summaries, manifests, hashes, metadata, pagination completeness, and per-stage counts that should line up but may not.
- Pipeline observability: places where logs claim success even though the state machine implied by the code says otherwise.

Instructions:
1. Read the full script and sketch the actual control-flow graph at a high level.
2. Identify all success, partial-success, retry, fallback, and failure exits.
3. Infer the intended output-integrity contract:
   - what must be true before output is considered valid
   - what must be true before a run is considered successful
4. Find branches that cannot be reached or checks whose outcomes do not influence control flow.
5. Flag any place where internal failure can be converted into empty, stale, default, or partial output without a hard failure or explicit degraded-state marker.
6. For each issue, provide:
   - Severity: critical / high / medium / low
   - Category: dead code, unreachable branch, false success, integrity gap, dead validation, contradictory logic, stale-output risk, observability mismatch
   - Exact code location
   - Why the branch/path is suspect
   - A concrete realistic failure scenario
   - Minimal fix
7. After findings, provide:
   - A list of branches that should be deleted, simplified, or asserted
   - A list of “success” conditions that should be tightened
   - Output-integrity assertions to add before write/commit
   - Suggested refactors to make states explicit

Be especially suspicious of:
- success = no exception, even if nothing useful was produced
- empty outputs treated as valid outputs
- write steps that occur after warnings or partial parse failures
- retry/fallback code that can reuse stale intermediate data
- multiple return paths with inconsistent success semantics
- lenient validations that do not gate output
- counters logged from pre-filter data while files are written from post-filter data
- dedupe/merge paths that can reduce counts without explanation
- “best effort” paths that are not marked as degraded mode

Output format:
- High-level control-flow map
- Success/failure exit map
- Findings table
- Fake-success risks first
- Output-integrity assertions to add
- Dead-code / unreachable-branch cleanup list
```

<!--
Test type: Static analysis — configuration, schema, and mode/flag contract audit.
Good for: Config drift, schema drift, hidden required fields, dangerous default values, cache contract mismatches, and contradictory modes.
Typical output: interface map, canonical schema/config model, findings table, high-risk flag interactions, and startup validation rules.
-->
## 4) Static Analysis — Config / Schema / Flag-Contract Audit

```text
You are an AI programming agent performing a static configuration, schema-contract, and mode-flag audit of a Python scraping and data-processing pipeline.

Goal:
Find mismatches between configuration, environment variables, CLI options, parser assumptions, transform-stage contracts, and output schema expectations.

Do not run the code. Infer interface contracts statically from function signatures, defaults, conditionals, config reads, object shapes, dict access patterns, dataclasses, TypedDicts, comments, and write logic.

Focus on these areas:
- Configuration drift: config keys that are read in some places but not validated centrally, renamed settings, legacy aliases, duplicate config sources, or settings whose defaults conflict with current code.
- Mode-flag interactions: combinations of CLI flags, feature flags, dry-run flags, cache flags, skip flags, validation toggles, overwrite flags, and debug flags that create contradictory or dangerous behavior.
- Schema-contract drift: parse-stage record shape vs transform-stage expectations vs output-stage requirements.
- Hidden required fields: fields treated as optional in one stage but assumed mandatory later.
- Default-value hazards: sentinel defaults, None defaults, empty-string defaults, magic constants, and fallback values that can silently alter semantics.
- Cross-stage interface ambiguity: functions returning inconsistent structures depending on branch, error case, or mode.
- Backward-compatibility traps: code trying to support old field names, old output formats, or old config keys in ways that create ambiguous precedence.
- Output schema guarantees: whether all code paths produce the same required columns, field names, types, metadata, and manifests.
- Caching and resume contracts: cache readers/writers and intermediate files that assume a structure not guaranteed by producers.
- Operational contract mismatches: log messages, docstrings, argparse help text, README comments, and code behavior disagreeing about what a mode or setting actually does.

Instructions:
1. Read the whole codebase/script and build an interface map:
   - CLI arguments
   - environment variables
   - config files and defaults
   - stage input/output schemas
   - output artifact contracts
2. Infer the canonical schema for records and the canonical config model.
3. Identify places where multiple sources of truth exist.
4. Flag mode combinations that can lead to:
   - skipped validation
   - empty outputs marked valid
   - stale cache reuse
   - schema mismatch
   - partial writes
   - inconsistent output formats
5. For each finding, provide:
   - Severity: critical / high / medium / low
   - Category: config drift, contract drift, flag interaction, hidden required field, default hazard, backward-compat risk, cache contract mismatch, output schema mismatch
   - Exact code location
   - Why the interface is ambiguous or dangerous
   - A realistic failure scenario
   - Recommended fix
6. Then provide:
   - A proposed single source of truth for config
   - A proposed explicit record schema for every stage
   - Illegal or risky flag combinations to reject at startup
   - Assertions/validators to run at stage boundaries
   - Suggested TypedDict/dataclass/pydantic models to reduce drift

Be especially suspicious of:
- flags that disable validation implicitly
- config values interpreted as bool/int/str in different places
- defaults that change behavior silently when a key is missing
- schema changes not reflected in writers or summaries
- optional fields used as dedupe keys or identifiers
- output column order or names depending on mode
- cache files loaded without schema/version checks
- CLI help text promising behavior not actually enforced by code

Output format:
- Interface map
- Canonical schema and config model
- Findings table
- Highest-risk flag/config interactions
- Stage-boundary contracts to formalize
- Startup validation rules to add
```

---

<!--
Test type: Fuzz testing — mutation or coverage-guided fuzzing.
Good for: Crashes, hangs, parser failures, resource exhaustion, and malformed-output cases caused by bad or adversarial inputs.
Typical output: fuzz target map, harness code, seed corpus plan, mutation strategy, bug oracles, triage checklist, and regression fixtures.
-->
## 5) Fuzz Testing — Mutation / Coverage-Guided Fuzzing

```text
You are designing a fuzz-testing plan and fuzz harness for a Python pipeline that scrapes data, parses it, transforms it, validates it, and writes output files.

Your goal is to find:
- unhandled exceptions
- hangs and infinite loops
- memory blowups
- parser failures
- bad assumptions about input shape
- malformed-output bugs
- retry/timeout edge cases
- cases where the pipeline silently writes partial or corrupted output

Assume external inputs are untrusted and messy:
- HTML pages with missing or reordered elements
- JSON with wrong types, missing keys, nulls, giant strings, weird Unicode, duplicated keys, and nested junk
- CSV/text with encoding issues, embedded delimiters, truncated rows, broken newlines, and huge fields
- URLs, filenames, timestamps, and IDs with unusual but plausible values

Your tasks:
1. Identify the best fuzz targets in the codebase, especially pure parsing and transformation functions.
2. Avoid real network access; isolate functions so fuzzing feeds payloads directly into parser/transform stages.
3. Build a mutation-based fuzzing strategy using both:
   - valid seed inputs captured from real examples
   - malformed and edge-case mutations
4. Generate a Python fuzz harness for the highest-value target functions.
5. Include timeouts, resource guards, and crash reproduction support.
6. Save failing inputs as regression fixtures.
7. Minimize or simplify failing inputs when possible.
8. Distinguish expected validation failures from real bugs; do not report normal input rejection as a crash.
9. Report findings in a way that helps a developer reproduce and patch them quickly.

Be aggressive about mutating:
- encodings
- whitespace and invisible characters
- nesting depth
- repeated fields
- giant field sizes
- partial truncation
- duplicated records
- invalid numeric formats
- timestamp variants
- unexpected content types
- broken pagination markers
- mixed valid and invalid records in one payload

Priorities:
- Find stages where one bad record can poison the whole batch.
- Find cases where empty or partial data is treated as success.
- Find paths that can write output after internal parse failure.
- Find loops whose termination depends on malformed page structure or pagination tokens.
- Find payloads that trigger pathological regex or parser behavior.

Output format:
- Fuzz target map
- Proposed harness code
- Seed corpus plan
- Mutation strategy
- Bug oracle rules
- Crash triage checklist
- Regression test plan

When writing the harness:
- Prefer deterministic local fuzz entry points.
- Catch only exceptions that represent expected invalid input.
- Treat unhandled exceptions, timeouts, excessive memory use, and corrupted output as bugs.
- Save failing seeds to disk with a short label and reproduction note.
```

<!--
Test type: Fuzz testing — property/metamorphic fuzzing.
Good for: Silent logic bugs, semantic drift, unstable normalization, wrong dedupe behavior, and output corruption without crashes.
Typical output: stage invariants, metamorphic relations, harness/tests, bug oracles, failing cases, and regression strategy.
-->
## 6) Fuzz Testing — Property / Metamorphic Fuzzing

```text
You are designing a property-based and metamorphic fuzz-testing plan for a Python data pipeline that scrapes, normalizes, transforms, deduplicates, and outputs structured data.

Do not focus only on crashes. Your main job is to find silent logic bugs where the pipeline completes successfully but the output is incorrect, inconsistent, unstable, or lossy.

Your tasks:
1. Identify key invariants for each stage of the pipeline.
2. Design generators for valid, near-valid, and adversarial structured inputs.
3. Write property-based tests or fuzz-style tests that check those invariants.
4. Propose metamorphic relations: controlled input changes that should preserve or predictably change output.
5. Find assumptions around normalization, deduplication, sorting, grouping, and serialization.
6. Save any failing examples in minimal reproducible form for regression tests.

Focus on these bug classes:
- parse succeeds but fields are misassigned
- normalization changes meaning
- deduplication drops legitimate records
- ordering changes output unexpectedly
- repeated runs produce different results from the same input
- round-trip serialization loses information
- invalid records leak into valid output
- one malformed record causes unrelated records to disappear
- counters, summaries, or aggregates become inconsistent with row-level output

Generate fuzz tests around these properties:
- Idempotence: running normalization twice should not change results after the first pass.
- Round-trip stability: parse -> normalize -> serialize -> parse should preserve required fields and record identity.
- Order invariance: record order changes should not change deduplicated output unless order is explicitly part of the spec.
- Partition invariance: processing data in one batch vs split batches and then merging should produce equivalent results when the pipeline claims batch independence.
- Schema integrity: every output record must satisfy required keys, types, and non-empty constraints.
- Duplicate handling: adding an exact duplicate should not create an inconsistent aggregate or silently delete the wrong record.
- Monotonicity checks where applicable: adding valid records should not reduce unrelated valid output counts.
- Encoding robustness: equivalent Unicode forms, whitespace variants, or line-ending variants should not create duplicate identities or broken parsing unless explicitly intended.

Be especially suspicious of:
- slug generation
- key normalization
- timestamp parsing
- implicit locale assumptions
- case folding
- whitespace trimming
- float/string/int coercions
- fallback defaults
- grouping keys
- sort keys
- dedupe keys
- null handling
- schema evolution across stages

Output format:
- Pipeline invariants by stage
- Metamorphic relations to test
- Generated test/harness code
- High-risk bug oracles
- Example failing cases to preserve as fixtures
- Regression strategy

When writing tests:
- Prefer small composable generators for records and payload fragments.
- Include both fully valid and almost-valid inputs.
- Shrink or simplify failing inputs.
- Flag silent output corruption as a failure even when no exception occurs.
- Explain what each property is supposed to guarantee.
```

---

<!--
Test type: Property-based testing — schema and invariant testing.
Good for: Ensuring records stay valid and consistent across parse, normalize, validate, and output stages.
Typical output: stage map, inferred schemas, property list, Hypothesis tests, high-risk invariants, and regression suggestions.
-->
## 7) Property-Based Testing — Schema / Invariant Testing

```text
You are an AI programming agent. Write property-based tests for a Python pipeline that scrapes data, parses it, normalizes it, validates it, and writes structured output.

Goal:
Find bugs where the pipeline accepts messy real-world input but produces invalid, inconsistent, lossy, or partially corrupted records.

Testing style:
Use property-based testing with generated structured inputs. Focus on invariants that must always hold for individual records and collections of records.

Tasks:
1. Read the pipeline code and identify each stage:
   - raw scraped input
   - parsed records
   - normalized records
   - validated records
   - serialized/output records
2. Infer the expected schema at each stage.
3. Write property-based tests that generate:
   - valid records
   - near-valid records
   - records with missing fields
   - records with wrong field types
   - records with null/blank values
   - weird Unicode, whitespace, and line ending variations
   - timestamps, IDs, slugs, URLs, and numeric fields with unusual but plausible forms
4. Define invariants for each stage and assert them.

Important invariants to test:
- Every emitted output record has all required fields.
- Required fields have the expected types after normalization.
- Normalization is idempotent: normalizing twice gives the same result as once.
- Validation rejects malformed records explicitly instead of silently converting them into valid-looking output.
- A malformed record does not corrupt unrelated records in the same batch.
- Deduplication never merges distinct records that differ in identity-bearing fields.
- Deduplication removes exact duplicates consistently.
- Output serialization preserves required values and does not drop fields unexpectedly.
- Record counts, summary counts, and output rows remain internally consistent.

Implementation requirements:
- Use pytest + Hypothesis.
- Build reusable strategies for input records and batches.
- Keep generators composable and readable.
- Prefer direct calls to parse/normalize/validate functions over full network execution.
- Save any minimal failing cases as regression tests after discovering them.
- Treat silent data corruption as a test failure even if no exception occurs.

Output format:
- Brief pipeline stage map
- List of inferred schemas
- Property list with rationale
- Test code
- Notes on the highest-risk invariants
- Suggested follow-up regression tests
```

<!--
Test type: Property-based testing — metamorphic and round-trip testing.
Good for: Catching wrong behavior under reordering, duplication, batching, formatting changes, and serialization round-trips.
Typical output: semantic model, metamorphic relations, round-trip properties, test code, likely bug classes, and regression fixtures.
-->
## 8) Property-Based Testing — Metamorphic / Round-Trip Testing

```text
You are an AI programming agent. Write metamorphic and round-trip property-based tests for a Python pipeline that scrapes, parses, transforms, deduplicates, aggregates, and outputs data.

Goal:
Find bugs where the pipeline appears to succeed but produces subtly wrong output when inputs are reordered, duplicated, reformatted, split into batches, or serialized and parsed again.

Testing style:
Use property-based testing to generate valid and near-valid input datasets, then apply transformations that should preserve meaning or change results in a predictable way.

Tasks:
1. Identify the main semantic units in the pipeline:
   - a single source document or response
   - a parsed record
   - a collection or batch of records
   - final output artifacts
2. Define metamorphic relations and round-trip properties.
3. Write property-based tests that generate datasets and then derive related datasets from them.

Metamorphic properties to test:
- Order invariance: reordering equivalent input records should not change deduplicated output unless order is explicitly meaningful.
- Batch invariance: processing all records at once vs processing chunks and merging should produce equivalent results when the pipeline claims batch independence.
- Duplicate stability: adding exact duplicates should not create inconsistent counts or alter unrelated records.
- Formatting equivalence: harmless differences in whitespace, Unicode normalization, casing, or line endings should not create new identities unless the spec says they should.
- Round-trip stability: serialize -> parse or parse -> serialize -> parse should preserve required semantic fields.
- Normalization stability: once a record is normalized, repeating the normalization should not keep changing it.
- Monotonicity where applicable: adding one valid unrelated record should not reduce the number of other valid records.
- Projection consistency: aggregate summaries should remain consistent with row-level output after transformations.

Implementation requirements:
- Use pytest + Hypothesis.
- Build strategies for whole batches, not just single records.
- Include edge cases such as empty batches, one-record batches, mixed-validity batches, duplicates, and partially malformed records.
- Avoid real network access; test deterministic local functions.
- When a property fails, keep the smallest reproducible failing example and convert it into a regression test.
- Flag silent semantic drift as a failure even when the code runs successfully.

Output format:
- Semantic model of the pipeline
- Metamorphic relations with explanations
- Round-trip properties
- Test code
- Likely bug classes each property can reveal
- Regression fixtures to add immediately
```

---

<!--
Test type: Symbolic execution — broad path exploration / concolic testing.
Good for: Systematic branch exploration, edge-condition discovery, and generating concrete inputs for hidden paths.
Typical output: candidate entry points, path map, concolic harness, uncovered branches, generated concrete tests, and regression cases.
-->
## 9) Symbolic Execution — Concolic / Path-Exploration

```text
You are an AI programming agent performing concolic / path-exploration symbolic execution planning for a Python pipeline that scrapes data, parses it, transforms it, validates it, and writes output files.

Goal:
Generate high-value test cases by systematically exploring feasible branches and turning path constraints into concrete inputs.

Important constraints:
- Do not rely on live network access.
- Isolate deterministic functions wherever possible.
- Prefer symbolic execution of pure or mostly pure functions such as parsing, normalization, validation, deduplication, record merging, routing, and output formatting.
- Stub or model nondeterministic boundaries such as HTTP requests, current time, random values, filesystem state, and environment variables.

Tasks:
1. Read the code and identify candidate symbolic-execution entry points.
2. Break the pipeline into stages:
   - input acquisition
   - parsing
   - transformation
   - validation
   - aggregation/deduplication
   - output writing
3. For each stage, identify:
   - branch conditions
   - boundary conditions
   - assertions and implicit assumptions
   - exceptional paths
   - silent-success paths that may still produce wrong output
4. Design a concolic testing harness that:
   - starts with realistic seed inputs
   - records path conditions
   - negates or flips unexplored branch constraints
   - generates concrete inputs for alternate feasible paths
5. Prioritize branches involving:
   - missing keys
   - empty collections
   - type coercions
   - malformed timestamps
   - whitespace and Unicode normalization
   - dedupe key generation
   - sort/group logic
   - fallback defaults
   - partial failures
   - file-output conditions
6. Treat these as bugs unless explicitly documented:
   - unhandled exceptions
   - use of partially initialized records
   - output written after internal stage failure
   - data silently dropped without a tracked reason
   - inconsistent summaries vs row-level output
7. For every feasible bug-triggering path, produce:
   - exact branch path summary
   - concrete input
   - expected vs actual behavior
   - smallest reproducible test case
   - suggested fix

Implementation guidance:
- Convert external inputs into symbolic models at function boundaries.
- Keep network, filesystem, and clock dependencies mocked or abstracted.
- Prefer exploring the parser/transform layers before the top-level orchestration layer.
- If loops cause path explosion, bound them or summarize them while preserving high-risk behaviors.
- Save generated bug-triggering inputs as regression fixtures.

Output format:
- Candidate entry points
- Path map by stage
- Proposed concolic harness
- Highest-value unexplored branches
- Generated concrete test cases
- Regression tests to add immediately
```

<!--
Test type: Symbolic execution — goal-directed / sink-targeted analysis.
Good for: Forcing execution into specific dangerous states such as false success, bad output, swallowed exceptions, or bad dedupe behavior.
Typical output: sink inventory, reachability plan, symbolic conditions, concrete tests, feasible vs infeasible targets, and guard recommendations.
-->
## 10) Symbolic Execution — Goal-Directed / Sink-Targeted

```text
You are an AI programming agent performing goal-directed symbolic execution for a Python scraping and data-processing pipeline.

Goal:
Work backward from risky sinks and generate concrete inputs that force the pipeline into dangerous but feasible states.

Do not optimize for generic coverage first. Optimize for reaching specific target conditions.

Target sink categories:
- parser accepts malformed input but misassigns fields
- a record reaches output with missing required fields
- deduplication merges distinct records
- one malformed record causes unrelated records to disappear
- partial batch failure still produces “successful” output
- aggregation counts differ from row-level data
- output path or filename becomes invalid or dangerous
- exception recovery masks a real failure and continues
- serialization drops or rewrites important values
- retry/fallback logic reuses stale or mismatched data

Tasks:
1. Read the pipeline and identify high-risk sink states, assertions, and invariants.
2. Build symbolic targets around:
   - specific branches
   - assertion failures
   - invalid output states
   - inconsistent counters
   - bad write conditions
   - paths that swallow exceptions
3. For each sink, derive the symbolic conditions needed to reach it.
4. Solve for concrete inputs that satisfy those conditions.
5. Generate minimal reproducing tests for each reachable sink.
6. Mark infeasible sinks separately from feasible ones.
7. Recommend where to add guards, assertions, and pre/postconditions to block those paths.

Focus areas:
- parse -> normalize -> validate transitions
- dedupe keys and identity logic
- timestamp parsing and normalization
- empty/None handling
- mixed-validity batches
- fallback defaults
- output-writing preconditions
- “success” return values after partial internal failure

Implementation guidance:
- Use targeted path search rather than naive full-path enumeration.
- Abstract or stub external systems.
- Keep symbolic state focused on fields that influence sink reachability.
- Prefer function-level symbolic execution for risky transformations over whole-program exploration.
- Bound loops and pagination, but preserve branches affecting correctness and output integrity.
- Generate one concrete test per distinct reachable sink path.

For each finding, provide:
- sink name
- symbolic conditions
- concrete input
- path summary
- why the path is dangerous
- whether the sink is feasible
- patch recommendation
- regression test

Output format:
- Risk sink inventory
- Reachability plan
- Symbolic conditions by sink
- Concrete tests generated
- Infeasible vs feasible targets
- Guardrails and assertions to add
```

---

<!--
Test type: Model checking — state-machine and temporal-property checking.
Good for: Workflow correctness, retry behavior, safety/liveness rules, and explicit transition validation.
Typical output: abstract state machine, transition rules, safety/liveness properties, counterexample traces, and code-level guard recommendations.
-->
## 11) Model Checking — State-Machine / Temporal-Property Checking

```text
You are an AI programming agent performing model-checking oriented analysis for a Python pipeline that scrapes data, parses it, transforms it, validates it, deduplicates it, and writes output files.

Goal:
Build an abstract finite-state model of the pipeline and check temporal properties over all allowed execution paths, including failure and retry paths.

Important instructions:
- Do not test by running random examples first.
- First derive a small explicit model of the pipeline as states, transitions, guards, and invariants.
- Abstract away irrelevant implementation detail.
- Replace large real-world data with small categories such as:
  - valid record
  - malformed record
  - duplicate record
  - empty batch
  - partial batch
  - stale cached input
  - write failure
  - retry success
  - retry failure
- Model external systems such as network, filesystem, time, and cache as nondeterministic but bounded environment actions.

Tasks:
1. Read the Python code and identify the pipeline stages and side effects.
2. Create a finite-state model with states such as:
   - idle
   - fetching
   - fetch_failed
   - parsing
   - parse_failed
   - transforming
   - validating
   - deduplicating
   - writing_output
   - write_failed
   - completed
   - completed_with_partial_data
   - aborted
3. Define transition guards and environment events.
4. Identify safety properties that must always hold.
5. Identify liveness properties that must eventually hold if certain conditions are met.
6. Encode the model in a model-checking-friendly form, such as a transition system, PlusCal/TLA+-style spec, explicit state graph, or equivalent pseudo-formal notation.
7. Check the model for counterexamples.
8. For every violated property, produce the shortest counterexample trace and map it back to the Python code.

Safety properties to check:
- The pipeline never writes output before parsing and validation are complete.
- No record with missing required fields can reach final output.
- A parse failure cannot be marked as a successful completed run.
- Distinct records are never merged by deduplication unless dedupe keys truly match.
- Summary counts must always match row-level output counts.
- A failed write cannot leave the system in a “success” state.
- Partial internal failure cannot silently produce final output unless explicitly marked partial.

Liveness properties to check:
- If input is fetchable and parseable, the pipeline can eventually reach completed.
- If a transient fetch failure is retried and later succeeds, the run can progress to completion.
- If output writing is retried under valid conditions, the system does not remain stuck forever in an intermediate state.

Output format:
- Abstract state machine
- State variables and domains
- Transition rules
- Safety properties
- Liveness properties
- Counterexample traces
- Python-code locations implicated by each counterexample
- Recommended guards/assertions to add
```

<!--
Test type: Model checking — bounded reachability and bad-state search.
Good for: Small but realistic combinations of failures, retries, malformed records, and output corruption states.
Typical output: bounded model, reachability queries, minimal counterexample traces, unreachable-state explanations, and regression tests.
-->
## 12) Model Checking — Bounded Reachability / Fault-Combination Checking

```text
You are an AI programming agent performing bounded model checking and reachability analysis for a Python scraping and data-processing pipeline.

Goal:
Find whether dangerous states are reachable within small bounded executions, using a compact abstract model of the pipeline and its environment.

Scope:
Model only a bounded number of records, retries, pages, failures, and output artifacts, but include the most important correctness and recovery behavior.

Instructions:
- Build a minimal abstract model of the pipeline.
- Use small finite domains for data and environment choices.
- Bound loops such as pagination, retries, batching, and deduplication windows.
- Search systematically for bad reachable states rather than broad random test coverage.
- Produce minimal counterexample traces and concrete regression scenarios.

Suggested bounds:
- 0 to 3 pages fetched
- 0 to 5 records per batch
- 0 to 2 malformed records
- 0 to 2 retries
- 0 to 2 output files
- 0 to 1 interrupted write event
- 0 to 1 stale-cache event

Bad states to check for reachability:
- pipeline reports success but output file is empty or incomplete
- output contains malformed records
- valid records disappear because one malformed record poisoned the batch
- deduplication drops distinct records
- duplicate records inflate aggregates
- summary/report counts disagree with row-level data
- interrupted or failed writes leave corrupted output that later runs treat as valid
- retry logic reuses stale data and still marks the run successful
- parse failure followed by fallback path produces semantically wrong output
- processing order changes final results when order is supposed to be irrelevant

Tasks:
1. Read the Python pipeline and identify:
   - control states
   - relevant data-state variables
   - environment inputs
   - failure events
   - success criteria
2. Build a bounded transition system.
3. Define reachability queries for each dangerous state.
4. Explore all executions within the chosen bounds.
5. For each reachable bad state, return:
   - the minimal trace
   - the triggering inputs/events
   - the code path likely responsible
   - the guard, invariant, or refactor that would block it
6. For each unreachable bad state, explain which invariant or control rule prevents it.
7. Convert each reachable counterexample into a concrete deterministic regression test.

Modeling hints:
- Abstract records into categories instead of full real payloads.
- Treat environment events as nondeterministic choices.
- Separate “run succeeded” from “output is actually valid.”
- Track batch integrity, record counts, and write completeness explicitly.
- Model atomic vs non-atomic writes as separate behaviors.

Output format:
- Bounded model definition
- State variables and bounds
- Reachability queries
- Reachable bad states with minimal traces
- Unreachable bad states with explanation
- Regression tests to add
- Hardening changes to the Python pipeline
```

---

<!--
Test type: Mutation testing — broad test-suite strength audit.
Good for: Measuring whether existing tests actually detect realistic code changes across parsing, validation, dedupe, aggregation, and output logic.
Typical output: mutation target map, mutant classifications, survived-mutant findings, missing assertions, and a test-improvement roadmap.
-->
## 13) Mutation Testing — General Test-Suite Strength Audit

```text
You are an AI programming agent performing mutation testing design and triage for a Python pipeline that scrapes data, parses it, transforms it, validates it, deduplicates it, and writes output files.

Goal:
Evaluate whether the existing test suite is actually capable of detecting realistic code defects in the pipeline.

Your job:
1. Read the Python pipeline and the existing tests.
2. Identify the highest-value mutation targets, especially:
   - parsing logic
   - normalization rules
   - validation checks
   - dedupe conditions
   - filtering logic
   - aggregation/counting logic
   - output-writing decisions
   - success/failure status logic
3. Design and apply general mutation operators such as:
   - comparison flips: == to !=, > to >=, in to not in
   - boolean flips: and/or negation, condition inversion
   - constant mutations: 0/1/None/empty string/default values
   - arithmetic mutations: + to -, increment/decrement changes
   - return-value mutations: return None, return empty collection, return stale/default value
   - exception mutations: remove raise, broaden except, skip error path
   - control-flow mutations: early return, skipped branch, altered loop boundary
   - collection mutations: append/remove/slice/off-by-one changes
4. Run or simulate mutation analysis conceptually and classify mutants as:
   - killed
   - survived
   - equivalent or probably equivalent
   - flaky / inconclusive
5. Prioritize survived mutants that indicate likely blind spots in the tests.

Focus especially on these pipeline-specific failure modes:
- empty output incorrectly treated as success
- malformed records slipping through validation
- dedupe deleting legitimate records
- duplicate records inflating counts
- partial parse failures being silently ignored
- summaries disagreeing with row-level outputs
- output files being written under incorrect preconditions
- fallback/default behavior masking real failures

For each survived mutant, provide:
- Severity: critical / high / medium / low
- Exact mutated location
- Original behavior
- Mutated behavior
- Why current tests missed it
- What test or assertion should kill it
- Whether the mutant may be equivalent

At the end, provide:
- Mutation target map by pipeline stage
- Top 10 most valuable survived mutants
- Missing assertions to add immediately
- Weak areas in the current test suite
- Suggested new unit, integration, and regression tests

Output format:
- Pipeline map
- Mutation operator plan
- Findings table
- Highest-risk survived mutants first
- Test improvements
- Mutation-testing roadmap
```

<!--
Test type: Mutation testing — domain-specific semantic mutants.
Good for: Realistic scrape-pipeline defects such as selector drift, schema loss, bad normalization, bad dedupe keys, stale-cache output, and false success.
Typical output: semantic contract map, domain-specific mutant catalog, survived-mutant analysis, tests to add, and invariants to formalize.
-->
## 14) Mutation Testing — Domain-Specific Semantic Mutants

```text
You are an AI programming agent performing domain-specific mutation testing for a Python scraping and data-processing pipeline.

Goal:
Create and analyze realistic mutants that mimic the kinds of bugs scraping pipelines actually suffer from, not just generic syntax-level mutations.

Your job:
1. Read the code and identify the semantic contracts of the pipeline:
   - what counts as a valid scraped record
   - how fields are extracted
   - how fields are normalized
   - what defines record identity
   - what makes output complete and trustworthy
2. Design domain-specific mutants that represent realistic production bugs in scraping pipelines.
3. Evaluate whether the current tests would detect each mutant.
4. For survived mutants, propose precise new tests and assertions.

Create mutants in these categories:
- Selector drift mutants: change field selectors, lookup keys, attribute names, or parsing paths so the wrong field is extracted but the code still “works”.
- Schema-loss mutants: drop a required field, rename one field, or replace one field with a fallback/default.
- Normalization mutants: change trimming, casing, Unicode normalization, timestamp parsing, slug generation, or numeric coercion.
- Validation mutants: weaken required-field checks, skip one validator, convert hard failures to warnings, or allow partial records through.
- Dedupe mutants: alter dedupe key construction, remove one identity field, or treat near-matches as exact matches.
- Aggregation mutants: change counting/grouping/sort behavior so summaries diverge from row-level output.
- Batch-isolation mutants: let one malformed record poison the entire batch or let a skipped record alter unrelated records.
- Output-integrity mutants: write rows in the wrong order, omit metadata, emit stale cache data, or mark partial output as successful.
- Recovery mutants: retry with stale intermediate data, swallow exceptions, or continue after partial write failure.

For each mutant, answer:
- Is this a realistic bug for this codebase?
- Would the current tests catch it?
- If not, why not?
- What is the smallest test that should kill it?
- What invariant should be asserted to prevent this class of bug permanently?

Important priorities:
- Prefer semantically dangerous mutants over trivial ones.
- Focus on mutants that preserve apparent success while corrupting meaning.
- Flag “false confidence” tests that only check non-empty output, file existence, or status codes.
- Distinguish equivalent mutants from genuinely dangerous survivors.

At the end, produce:
- A ranked catalog of domain-specific mutants
- The most dangerous survived mutants
- New regression tests to add
- Invariants to enforce at stage boundaries
- A recommended ongoing mutation profile for this pipeline

Output format:
- Semantic contract map
- Domain-specific mutant catalog
- Survived mutant analysis
- Tests to add immediately
- Invariants to formalize
- Ongoing mutation strategy
```

---

<!--
Test type: Differential testing — compare against an independent reference implementation.
Good for: Finding semantic disagreements when there is no perfect oracle, especially in parsing, normalization, dedupe, and serialization.
Typical output: comparison boundaries, reference implementation plan, canonical comparison schema, differential harness, mismatch triage rules, and regression fixtures.
-->
## 15) Differential Testing — Independent Reference Implementation

```text
You are an AI programming agent designing and implementing differential tests for a Python pipeline that scrapes data, parses it, transforms it, validates it, deduplicates it, and writes structured output.

Goal:
Find bugs by comparing the primary pipeline against an independent reference implementation on the same inputs.

Core idea:
Do not rely on one implementation alone. Build or identify a second implementation that is intentionally different in structure, then compare normalized outputs. Treat meaningful disagreement as a probable defect unless the difference is explicitly allowed by the spec.

Tasks:
1. Read the pipeline and identify high-value comparison boundaries:
   - raw fetch response -> parsed records
   - parsed records -> normalized records
   - normalized records -> deduplicated records
   - deduplicated records -> final serialized output
2. Create or identify a reference path that is independent from the main logic, for example:
   - a simpler parser written from scratch
   - a different extraction strategy
   - a second normalization path with explicit steps
   - a minimal trusted implementation for a subset of fields
3. Define a canonical comparison format so outputs can be compared fairly:
   - normalized field names
   - normalized types
   - stable ordering
   - ignored non-semantic metadata
   - explicit tolerances for acceptable differences
4. Generate a corpus of inputs including:
   - known-good real examples
   - historical tricky examples
   - malformed but partially parseable inputs
   - edge cases around empty fields, Unicode, timestamps, duplicates, and pagination
5. Compare the main and reference outputs at multiple levels:
   - record counts
   - required fields
   - record identity keys
   - per-field values
   - aggregate summaries
   - output artifact metadata
6. Classify differences as:
   - definite bug
   - likely bug
   - spec ambiguity
   - acceptable difference
7. For each meaningful mismatch, produce:
   - exact input
   - diff summary
   - which implementation is more likely wrong and why
   - smallest reproducible fixture
   - regression test to add

Important priorities:
- Focus on semantic differences, not cosmetic formatting noise.
- Catch cases where both paths “succeed” but disagree on meaning.
- Be suspicious of missing records, merged records, dropped fields, wrong timestamps, wrong dedupe behavior, and inconsistent aggregates.
- Prefer a deliberately simple reference implementation over a second copy of the same logic.

Output format:
- Comparison boundaries
- Reference implementation plan
- Canonical comparison schema
- Differential test harness
- Mismatch triage rules
- Regression fixtures and tests
```

<!--
Test type: Differential testing — compare versions, modes, flags, and execution paths.
Good for: Regression detection, feature-flag drift, cache-related mismatches, and “same input, different semantics” problems over time.
Typical output: compared modes/versions, corpus plan, normalization rules, differential harness, mismatch classification, and regression locks.
-->
## 16) Differential Testing — Cross-Version / Cross-Mode Comparison

```text
You are an AI programming agent designing and implementing cross-version and cross-mode differential tests for a Python scraping and data-processing pipeline.

Goal:
Detect semantic drift, unintended behavior changes, and hidden mode-dependent bugs by running the same input corpus through multiple versions or modes of the pipeline and comparing the results.

Core idea:
Use differential testing to compare:
- old version vs new version
- cache-enabled vs cache-disabled
- strict-validation mode vs normal mode
- one-batch processing vs chunked processing
- one output writer vs another
- alternate parser backends or feature flags

Tasks:
1. Read the pipeline and identify all meaningful modes, options, feature flags, and behavioral branches.
2. Build a replayable corpus of representative inputs:
   - golden real-world fixtures
   - previously failing cases
   - malformed-but-salvageable inputs
   - duplicate-heavy inputs
   - ordering-sensitive inputs
   - empty and partial batches
3. Define which result differences are expected and which are bugs.
4. Create a differential harness that runs the same corpus through paired configurations such as:
   - current branch vs previous stable branch
   - strict vs lenient validation
   - cache hit vs fresh parse
   - full batch vs chunked batch + merge
   - different serializers or output formats
5. Normalize outputs before comparison:
   - sort records canonically
   - normalize timestamps and encodings
   - ignore allowed metadata differences
   - compare both row-level data and summary-level data
6. Flag these as likely bugs unless explicitly allowed:
   - missing or extra records
   - changed identity keys
   - changed field values without a documented reason
   - different dedupe outcomes
   - summary totals diverging from row data
   - success status differing while outputs are equivalent
   - equivalent status while outputs differ materially
7. For each mismatch, provide:
   - compared modes or versions
   - exact input fixture
   - minimal diff
   - likely source of semantic drift
   - whether the change looks intentional, ambiguous, or broken
   - regression test to lock desired behavior

Important priorities:
- Detect “looks successful” regressions where output changed silently.
- Distinguish intentional improvements from accidental contract drift.
- Compare semantic meaning, not file formatting alone.
- Pay special attention to dedupe keys, normalization rules, timestamp handling, and output completeness.

Output format:
- Modes and versions selected for comparison
- Corpus plan
- Output-normalization rules
- Differential harness
- Mismatch classification rules
- High-risk semantic drifts found
- Regression tests to add
```
````