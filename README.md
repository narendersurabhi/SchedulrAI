# SchedulrAI

SchedulrAI is an early-stage scheduling assistant scaffold focused on a thin, deterministic vertical slice: parse a narrow natural-language scheduling request, rank valid meeting slots, and book the best option through a mock calendar provider.

The current repository is intentionally small and constrained. It is designed to prove the core scheduling loop before expanding into broader AI orchestration, real calendar integrations, or meeting-intelligence workflows.

## Current Slice

Today the repo implements a Phase 3 thin-slice milestone:

> Parse a narrow scheduling request, ask for clarification when key details are missing, then schedule and safely book the best option through the mock provider.

This phase includes:

- Shared schema contracts for scheduling, candidate slots, parser results, booking payloads, and execution audit records
- A narrow parser service that emits validated `SchedulingRequest` payloads, confidence scores, and clarification questions
- A deterministic happy-path parser for requests like `Schedule 30 minutes with Sarah next Tuesday afternoon`
- A deterministic scheduler with constraint filtering, ranking, and reason codes
- A mock calendar provider backed by fixture data, supporting create, update, and cancel flows
- A booking executor that supports dry-run previews, idempotent writes, and audit logging
- A CLI demo that runs parse → recommend → preview → book end to end
- Unit tests plus fixture-based parsing and scheduling eval inputs for the current slice

This phase intentionally does **not** yet include:

- Live LLM-backed parsing or hosted model integrations
- Multi-turn clarification state or conversation memory
- Real Google Calendar or Outlook integrations
- OAuth, persistence, or workflow orchestration
- Multi-attendee optimization
- Webhook-driven lifecycle handling
- API or web UI surfaces

## Repository Layout

```text
apps/
  cli/                  # End-to-end demo entrypoint
services/
  calendar/             # Provider abstraction and mock implementation
  execution/            # Safe booking execution, previews, and audit logging
  intent_parser/        # Narrow natural-language parsing and clarification handling
  scheduler/            # Deterministic slot generation and ranking
shared/
  schemas/              # Shared scheduling, parsing, and execution contracts
tests/
  fixtures/             # Example availability and request payloads
  unit/                 # Unit coverage for parser, scheduler, provider, and executor behavior
evals/
  parsing/              # Frozen evaluation cases for parser disposition behavior
  scheduling/           # Frozen evaluation cases for scheduling behavior
docs/
  implementation-roadmap.md
  phase-1-execution-board.md
  phase-2-execution-board.md
  phase-3-execution-board.md
  system-design.md
```

## How the Current Flow Works

1. The CLI accepts a natural-language scheduling request.
2. The narrow parser service classifies the request as parsed, clarification-needed, or unsupported.
3. When parsed, the happy-path parser converts that text into a typed `SchedulingRequest`.
4. The scheduler queries the mock provider for availability windows.
5. Candidate slots are generated inside the allowed availability window.
6. Hard constraints reject invalid slots, and soft preferences adjust scores.
7. The top-ranked slot is turned into a booking request with a deterministic idempotency key.
8. The executor emits a dry-run preview, then performs the real provider-backed booking.
9. The CLI prints parse metadata, the structured request, scheduling decision, execution outcomes, and audit log as JSON.

## Quick Start

### Prerequisites

- Python 3.10+

### Create a virtual environment and install test dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Run the CLI demo

```bash
python -m apps.cli.demo "Schedule 30 minutes with Sarah next Tuesday afternoon"
```

Expected behavior:

- The parser emits a `parsed` result with confidence metadata
- The request is converted into a structured scheduling payload
- Ranked candidate slots are returned with reason codes
- A dry-run preview is emitted before any write
- The top slot is booked through the mock provider
- Execution audit records are printed to stdout

### Try an ambiguous request

```bash
python -m apps.cli.demo "Schedule with Sarah next Tuesday"
```

Expected behavior:

- The parser emits `needs_clarification`
- A clarification question explains which fields are still missing
- No scheduling or booking write occurs

### Run tests

```bash
pytest
```

## Core Modules

### `shared/schemas`
Contains the shared dataclass-based contracts used across the parser, scheduler, provider, executor, and demo. These models normalize attendees, time ranges, preferences, parser outcomes, decisions, booking requests, booking results, and audit entries.

### `services/intent_parser/happy_path.py`
Implements the current narrow parser service. It supports one validated happy-path request template, emits parser dispositions and clarification prompts, and converts supported text into a `SchedulingRequest` anchored to a reference datetime.

### `services/scheduler/core.py`
Implements deterministic candidate-slot generation and ranking. The scheduler currently applies:

- working-hours checks
- busy-event conflict detection
- focus-block penalties
- preferred-time bonuses
- avoid-window penalties
- minimum-notice filtering

Each candidate slot carries reason codes to support explainability.

### `services/calendar/provider.py`
Defines the provider interface and a fixture-backed `MockCalendarProvider`. The mock implementation returns seeded availability windows and supports idempotent create, update, and cancel operations for event writes.

### `services/execution/core.py`
Wraps calendar provider write actions in a safer execution layer. The executor currently supports dry-run previews, deterministic idempotency-key helpers, and an in-memory audit log for create, update, and cancel actions.

### `apps/cli/demo.py`
Provides a demo-ready entrypoint for the current end-to-end flow. It parses the input text, surfaces clarification state when needed, ranks slots for supported requests, previews the booking, executes it, and prints the full structured output.

## Documentation

- `docs/system-design.md` describes the long-term product and platform architecture.
- `docs/implementation-roadmap.md` breaks the system into phased milestones and module boundaries.
- `docs/phase-1-execution-board.md` defines the original frozen scope for the Phase 1 thin slice.
- `docs/phase-2-execution-board.md` defines the Phase 2 execution milestone for safe writes and auditability.
- `docs/phase-3-execution-board.md` defines the Phase 3 parser milestone for typed parsing plus clarification handling.
- `AGENTS.md` tracks repository status and change history for future agents.

## Project Status

SchedulrAI should now be treated as a Phase 3 proof of concept for deterministic parsing, deterministic scheduling, and safe mock execution behavior, not as a production-ready assistant.

Recommended next steps are already documented in the roadmap and include:

- exposing API or demo surfaces beyond the CLI
- introducing trace IDs, structured logging, and session state
- adding more scheduling and parsing evaluation depth
- introducing persistent audit storage and workflow orchestration
- later layering in live LLM-assisted parsing and meeting intelligence

## Contributing Notes

When extending this repository:

- keep the current slice narrow unless the docs explicitly broaden scope
- prefer extending shared contracts and fixtures before adding integrations
- preserve deterministic behavior and testability
- update `AGENTS.md` whenever the repository state materially changes
- keep README and docs aligned with the actual implemented surface area
