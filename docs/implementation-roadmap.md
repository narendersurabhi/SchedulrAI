# SchedulrAI Implementation Roadmap

## 1. Roadmap Goals

This roadmap turns the system design into a thin-slice delivery plan that emphasizes deterministic scheduling before broad AI orchestration. Each phase is intentionally scoped to produce a usable, testable repo milestone with clear module boundaries, demo artifacts, and issue-level execution steps.

## 2. Delivery Principles

- Ship one vertical slice per phase.
- Keep recommendation and execution as separate services and interfaces.
- Add LLM functionality only after typed schemas and deterministic scheduling are stable.
- Start evaluation harnesses in Phase 0 and expand them every phase.
- Prefer transparent heuristics before introducing workflow or optimization complexity.
- End every phase with a demo path, automated tests, and updated docs.

## 3. Target Repository Evolution

### Phase 0-2 structure

```text
apps/
  api/
services/
  scheduler/
  calendar/
shared/
  schemas/
  utils/
tests/
  unit/
  fixtures/
docs/
  system-design.md
  implementation-roadmap.md
```

### Phase 3-7 structure

```text
apps/
  api/
  worker/
  demo-ui/
services/
  intent_parser/
  scheduling_core/
  calendar_connectors/
  execution/
  workflow/
  meeting_intelligence/
shared/
  schemas/
  observability/
  utils/
evals/
  parsing/
  scheduling/
  summarization/
tests/
  unit/
  integration/
  fixtures/
docs/
  architecture/
  api/
```

## 4. Module List and Ownership Boundaries

| Module | Purpose | Introduced | Notes |
| --- | --- | --- | --- |
| `shared/schemas` | Typed request/response and domain contracts | Phase 0 | Pydantic models shared across API, scheduler, parser, and executor |
| `tests/fixtures` | Seed users, calendars, preference fixtures, sample payloads | Phase 0 | Basis for evals and deterministic tests |
| `services/calendar_connectors` | Provider abstraction plus Google Calendar adapter | Phase 1 | Reads free/busy first, write paths in Phase 2 |
| `services/scheduling_core` | Candidate generation, hard constraints, ranking, reason codes | Phase 1 | Deterministic scheduling backbone |
| `services/execution` | Create/update/cancel flows, audit logging, idempotency | Phase 2 | Write-safe calendar actions only |
| `services/intent_parser` | NL-to-schema extraction and clarification detection | Phase 3 | Strict JSON output, no direct tool execution |
| `apps/api` | FastAPI endpoints and request validation | Phase 4 | First end-to-end demo surface |
| `apps/demo-ui` | Minimal CLI or web chat demo | Phase 4 | Keep presentation layer intentionally thin |
| `shared/observability` | Trace IDs, structured logging, metrics helpers | Phase 4 | Shared across API and worker |
| `services/workflow` | Durable workflow orchestration and webhook handling | Phase 5 | Temporal or LangGraph-backed async state |
| `apps/worker` | Background consumers and workflow workers | Phase 5 | Webhooks, retries, delayed actions |
| `evals/scheduling` | Scenario-based scheduling quality checks | Phase 0, expanded in Phase 6 | Tracks slot quality and preference satisfaction |
| `evals/parsing` | Expected JSON outputs for NL prompts | Phase 3 | Measures parsing accuracy and clarification quality |
| `services/meeting_intelligence` | Transcript ingestion, summaries, actions, follow-ups | Phase 7 | Narrow start with transcript text upload |
| `evals/summarization` | Summary and action-item reference cases | Phase 7 | Quality gates for meeting intelligence |

## 5. Milestones

| Milestone | Phase | Exit Criteria | Demo Artifact |
| --- | --- | --- | --- |
| `v0.1 constraint-aware scheduler` | Phase 1 | Structured request returns top valid slots with reason codes and deterministic tests | CLI/API response showing ranked slots |
| `v0.2 bookable scheduling engine` | Phase 2 | Safe event creation and cancellation with idempotency and audit trail | Dry-run plus real booking flow |
| `v0.3 NL-to-scheduling parser` | Phase 3 | Natural language converts to validated `SchedulingRequest` with confidence and clarification handling | Parser demo with seed utterances |
| `v0.4 end-to-end scheduling assistant` | Phase 4 | Happy-path parse → recommend → confirm → book flow exposed via API/demo UI | Recorded repo demo |
| `v0.5 durable workflow automation` | Phase 5 | Async events survive retries and restarts with inspectable workflow state | Webhook/reschedule simulation |
| `v0.6 optimization-aware scheduler` | Phase 6 | Ranking quality improves over baseline with measurable preference gains | Benchmark comparison report |
| `v0.7 meeting intelligence` | Phase 7 | Transcript input yields summary, action items, and follow-up draft tied to meeting IDs | Transcript-to-summary demo |

## 6. Phase-by-Phase Plan With Repo Issues

### Phase 0 — Project framing and contracts

**Objective**
Establish the canonical contracts, fixtures, and evaluation baselines used by every downstream service.

**Primary deliverables**
- Pydantic models for scheduling and meeting artifacts
- Provider interface contracts
- Example request/response payloads
- Seed fixtures for users, preferences, and calendars
- Initial eval packs for deterministic scheduling scenarios

**Suggested repo issues**
- `ROADMAP-001` Define core domain schemas: `SchedulingRequest`, `CandidateSlot`, `SchedulingDecision`, `MeetingSummary`, `ActionItem`
- `ROADMAP-002` Define provider interfaces including `CalendarProvider` read/write contracts
- `ROADMAP-003` Add fixture packs for users, calendars, and preference profiles
- `ROADMAP-004` Add sample JSON payloads and schema validation tests
- `ROADMAP-005` Create initial scheduling eval scenarios and expected outputs
- `ROADMAP-006` Document service boundaries and error taxonomy

**Phase exit criteria**
- Static JSON requests validate against shared schemas
- Scheduler, parser, and executor all depend on the same contracts
- No LLM dependency exists yet

### Phase 1 — Deterministic scheduling MVP

**Objective**
Return conflict-free, ranked candidate slots from a structured request.

**Primary deliverables**
- Google Calendar provider adapter for free/busy reads
- Timezone normalization utilities
- Candidate interval generation
- Hard constraint filtering and soft scoring
- Top 3-5 ranked slots with reason codes

**Suggested repo issues**
- `ROADMAP-101` Implement Google Calendar free/busy adapter behind `CalendarProvider`
- `ROADMAP-102` Normalize timezone handling and UTC internal representation
- `ROADMAP-103` Build candidate interval generation over requested ranges
- `ROADMAP-104` Implement hard constraints: no-overlap, working hours, focus block avoidance
- `ROADMAP-105` Implement weighted scoring and explanation reason codes
- `ROADMAP-106` Add deterministic scheduler unit tests across timezone and conflict scenarios

**Phase exit criteria**
- Structured request returns ranked slots deterministically
- Conflicting slots are never proposed
- Unit tests cover timezone and constraint behavior

### Phase 2 — Booking executor and idempotent actions

**Objective**
Safely convert approved slots into provider-backed calendar events.

**Primary deliverables**
- `create_event`, `update_event`, and `cancel_event` executor flows
- Idempotency key support and duplicate protection
- Audit logging and execution result persistence
- Dry-run previews before writes

**Suggested repo issues**
- `ROADMAP-201` Implement event creation flow with title/description templating
- `ROADMAP-202` Implement cancel and update flows with provider response normalization
- `ROADMAP-203` Add idempotency key generation and replay protection
- `ROADMAP-204` Add execution audit log schema and persistence hooks
- `ROADMAP-205` Add dry-run mode and preview responses
- `ROADMAP-206` Add integration tests for create/cancel retry safety

**Phase exit criteria**
- Retries do not create duplicate events
- Every action is recorded in an audit log
- Dry-run and real execution both work end to end

### Phase 3 — LLM intent parser as a narrow service

**Objective**
Translate natural language scheduling requests into validated structured input.

**Primary deliverables**
- Intent classification and entity extraction prompt/service
- Temporal parsing and participant extraction
- Confidence scoring and clarification detection
- Strict schema validation and parser eval harness

**Suggested repo issues**
- `ROADMAP-301` Design strict parser prompt and structured JSON response contract
- `ROADMAP-302` Implement parser service wrapper with schema validation and retries
- `ROADMAP-303` Add confidence thresholds and clarification decision rules
- `ROADMAP-304` Create parsing eval dataset with expected JSON outputs
- `ROADMAP-305` Add parser regression tests for ambiguous and malformed requests
- `ROADMAP-306` Document parser limitations and fallback behavior

**Phase exit criteria**
- Seed natural language requests parse into valid contracts
- Ambiguous cases trigger clarification rather than unsafe execution
- Model output never bypasses schema validation

### Phase 4 — Thin end-to-end assistant slice

**Objective**
Expose a full scheduling flow from natural language request through booking confirmation.

**Primary deliverables**
- FastAPI endpoints for parse, recommend, confirm, and execute
- Minimal chat or CLI demo surface
- Session state, trace IDs, and structured logs
- Happy-path demo-ready orchestration

**Suggested repo issues**
- `ROADMAP-401` Implement FastAPI endpoints for scheduling request lifecycle
- `ROADMAP-402` Add session state store for current task context
- `ROADMAP-403` Implement response shaping for slot presentation and selection
- `ROADMAP-404` Add trace ID propagation and structured logging middleware
- `ROADMAP-405` Build CLI or minimal web demo for happy-path scheduling
- `ROADMAP-406` Add API integration tests and demo script fixtures

**Phase exit criteria**
- User can submit natural language, receive options, confirm one, and book it
- Logs make every pipeline step inspectable
- Repo has a recordable demo path

### Phase 5 — Workflow automation and async lifecycle

**Objective**
Support long-running, retry-safe scheduling workflows driven by external events.

**Primary deliverables**
- Workflow state machine and worker runtime
- Webhook ingestion for provider events
- Retry, deduplication, compensation, and delayed follow-up logic
- Inspectable workflow status and state transitions

**Suggested repo issues**
- `ROADMAP-501` Select workflow engine and document rationale (Temporal vs LangGraph)
- `ROADMAP-502` Implement webhook ingestion and event normalization
- `ROADMAP-503` Add deduplication keys and bounded retry policies for async events
- `ROADMAP-504` Implement attendee decline and alternative-slot recovery workflow
- `ROADMAP-505` Implement delayed reminder/nudge workflow
- `ROADMAP-506` Add workflow inspection endpoints and restart-survival tests

**Phase exit criteria**
- Duplicate webhook deliveries do not duplicate work
- Workflows survive worker restarts
- Async meeting lifecycle paths are observable and testable

### Phase 6 — Optimization engine v2

**Objective**
Improve recommendation quality beyond simple weighted ranking while preserving explainability.

**Primary deliverables**
- Expanded scoring dimensions: batching, context-switch, overload, timezone fairness
- Benchmark harness and baseline comparison reporting
- Optional advanced-mode solver spike with OR-Tools/CP-SAT
- Explanation metadata retained for every score contribution

**Suggested repo issues**
- `ROADMAP-601` Expand scoring model with additional preference and fairness dimensions
- `ROADMAP-602` Create benchmark harness comparing baseline vs v2 ranking quality
- `ROADMAP-603` Add preference satisfaction and focus-time preservation metrics
- `ROADMAP-604` Produce explanation payloads for score breakdowns
- `ROADMAP-605` Prototype OR-Tools advanced mode behind a feature flag
- `ROADMAP-606` Document optimization tradeoffs and fallback behavior

**Phase exit criteria**
- Benchmark pack shows measurable improvement over v0.1 scoring
- Recommendation explanations remain transparent
- Advanced optimization remains optional rather than mandatory

### Phase 7 — Meeting intelligence

**Objective**
Extend the platform from scheduling into post-meeting intelligence.

**Primary deliverables**
- Transcript ingestion and normalization
- Summary generation and action-item extraction
- Owner and due-date extraction
- Follow-up draft generation tied to meeting IDs

**Suggested repo issues**
- `ROADMAP-701` Implement transcript upload and metadata association to meetings
- `ROADMAP-702` Build summarization pipeline for concise executive summaries and decisions
- `ROADMAP-703` Extract structured action items with owners and due dates
- `ROADMAP-704` Generate follow-up drafts from meeting artifacts
- `ROADMAP-705` Persist meeting intelligence artifacts and retrieval metadata
- `ROADMAP-706` Add summarization eval dataset and editability review criteria

**Phase exit criteria**
- Transcript text produces useful summary and structured action items
- Follow-up drafts are readable and editable
- Artifacts are stored against the corresponding meeting record

## 7. Week-by-Week Deliverables

| Week | Theme | Deliverables | Demo/Checkpoint |
| --- | --- | --- | --- |
| Week 1 | Contracts and fixtures | Create shared schemas, provider interfaces, sample payloads, fixtures, and initial eval packs | Validate static JSON payloads end to end |
| Week 2 | Deterministic scheduler core | Add free/busy adapter, candidate generation, hard constraints, ranking, and scheduler tests | Show top 3-5 valid slots for mocked and real calendar reads |
| Week 3 | Safe booking execution | Add create/cancel/update flows, dry-run preview, audit logging, and idempotency coverage | Demo selecting a slot and safely creating/canceling an event |
| Week 4 | Narrow LLM parser | Add NL parser service, confidence scoring, clarification logic, and parsing evals | Demo sentence-to-`SchedulingRequest` conversion |
| Week 5 | End-to-end assistant slice | Add API, session state, trace IDs, structured logs, and thin UI/CLI | Record a happy-path scheduling demo |
| Week 6 | Durable workflows | Add webhook ingestion, worker runtime, retries, dedupe, and async reschedule/reminder flows | Simulate attendee decline and automated alternative suggestion |
| Week 7 | Optimization v2 | Add richer scoring features, benchmark harness, comparison reports, and optional OR-Tools spike | Present measurable ranking improvements over baseline |
| Week 8 | Meeting intelligence and polish | Add transcript summaries, action items, follow-ups, README polish, architecture updates, and final demo assets | End-to-end project showcase with scheduling plus meeting intelligence |

## 8. Recommended Milestone-to-Week Mapping

| Week | Milestone Target |
| --- | --- |
| Week 2 | `v0.1 constraint-aware scheduler` |
| Week 3 | `v0.2 bookable scheduling engine` |
| Week 4 | `v0.3 NL-to-scheduling parser` |
| Week 5 | `v0.4 end-to-end scheduling assistant` |
| Week 6 | `v0.5 durable workflow automation` |
| Week 7 | `v0.6 optimization-aware scheduler` |
| Week 8 | `v0.7 meeting intelligence` |

## 9. Evaluation Gates

### Parsing gates
- Valid schema output rate
- Clarification trigger precision for ambiguous requests
- Participant, duration, and time-range extraction accuracy

### Scheduling gates
- Conflict-free recommendation rate
- Preference satisfaction score
- Focus-time preservation score
- Mean ranking quality against expected top slots

### Execution gates
- Duplicate-booking prevention under retries
- Audit log completeness
- Dry-run vs execute parity

### Workflow gates
- Duplicate webhook suppression rate
- Successful recovery after worker restart
- Bounded retry and compensation coverage

### Meeting intelligence gates
- Summary usefulness review score
- Action item structure accuracy
- Owner/due-date extraction accuracy
- Follow-up draft edit distance / readability review

## 10. Risks and Sequencing Guardrails

- Do not start with a multi-provider abstraction beyond what is required for one provider demo.
- Do not let the LLM call provider APIs or make policy decisions directly.
- Do not introduce vector search, memory layers, or OR-Tools before deterministic scheduling is stable.
- Do not overbuild the frontend before the API and scheduler contracts are proven.
- Keep recurring meeting support and advanced enterprise policy logic out of the MVP path unless the core flow is complete.

## 11. First Deliverable to Optimize Around

The first high-confidence product checkpoint should be:

> Given a typed `SchedulingRequest`, return the top three valid slots with explanation metadata and safely book one of them.

If that flow is reliable, the rest of the roadmap becomes incremental layering rather than speculative infrastructure.
