# SchedulrAI

SchedulrAI is an early-stage scheduling assistant scaffold focused on a thin, deterministic vertical slice: parse a narrow natural-language scheduling request, rank valid meeting slots, and book the best option through a mock calendar provider.

The current repository is intentionally small and constrained. It is designed to prove the core scheduling loop before expanding into broader AI orchestration, real calendar integrations, or meeting-intelligence workflows.

## Current Slice

Today the repo implements a frozen happy-path scenario:

> Schedule 30 minutes with Sarah next Tuesday afternoon.

This phase includes:

- Shared schema contracts for scheduling, candidate slots, and booking payloads
- A regex-based happy-path parser for one narrow request shape
- A deterministic scheduler with constraint filtering, ranking, and reason codes
- A mock calendar provider backed by fixture data
- A CLI demo that runs parse → recommend → book end to end
- Unit tests and fixture-based eval inputs for the current slice

This phase intentionally does **not** yet include:

- Real Google Calendar or Outlook integrations
- OAuth, persistence, audit storage, or workflow orchestration
- Multi-attendee optimization
- Rescheduling, cancellation, or recurrence flows
- LLM-powered parsing or clarification loops
- API or web UI surfaces

## Repository Layout

```text
apps/
  cli/                  # End-to-end demo entrypoint
services/
  calendar/             # Provider abstraction and mock implementation
  intent_parser/        # Narrow natural-language parsing
  scheduler/            # Deterministic slot generation and ranking
shared/
  schemas/              # Shared scheduling and booking contracts
tests/
  fixtures/             # Example availability and request payloads
  unit/                 # Unit coverage for parser, scheduler, and provider behavior
evals/
  scheduling/           # Frozen evaluation cases for scheduling behavior
docs/
  implementation-roadmap.md
  phase-1-execution-board.md
  system-design.md
```

## How the Current Flow Works

1. The CLI accepts a natural-language scheduling request.
2. The happy-path parser converts that text into a typed `SchedulingRequest`.
3. The scheduler queries the mock provider for availability windows.
4. Candidate slots are generated inside the allowed availability window.
5. Hard constraints reject invalid slots, and soft preferences adjust scores.
6. The top-ranked slot is passed to the mock provider for idempotent booking.
7. The CLI prints the structured request, scheduling decision, and booking result as JSON.

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

- The request is parsed into a structured scheduling payload
- Ranked candidate slots are returned with reason codes
- The top slot is booked through the mock provider
- JSON output is printed to stdout

### Run tests

```bash
pytest
```

## Core Modules

### `shared/schemas`
Contains the shared dataclass-based contracts used across the parser, scheduler, provider, and demo. These models normalize attendees, time ranges, preferences, decisions, booking requests, and booking results.

### `services/intent_parser/happy_path.py`
Implements the current narrow parser. It supports one request template and converts it into a validated `SchedulingRequest` anchored to a reference datetime.

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
Defines the provider interface and a fixture-backed `MockCalendarProvider`. The mock implementation returns seeded availability windows and supports idempotent event creation through an idempotency key.

### `apps/cli/demo.py`
Provides a demo-ready entrypoint for the current end-to-end flow. It loads fixture data, parses the input request, ranks slots, books the best option, and prints the complete structured output.

## Documentation

- `docs/system-design.md` describes the long-term product and platform architecture.
- `docs/implementation-roadmap.md` breaks the system into phased milestones and module boundaries.
- `docs/phase-1-execution-board.md` defines the frozen scope for the current thin slice.
- `AGENTS.md` tracks repository status and change history for future agents.

## Project Status

SchedulrAI is currently in an early implementation-scaffold state. The repository should be treated as a Phase 1 proof of concept for deterministic scheduling behavior, not as a production-ready assistant.

Recommended next steps are already documented in the roadmap and include:

- expanding deterministic scheduling coverage
- introducing safer execution and audit capabilities
- adding a stricter parsing/evaluation harness
- exposing an API or demo surface beyond the CLI
- later layering in LLM-assisted parsing and meeting intelligence

## Contributing Notes

When extending this repository:

- keep the current slice narrow unless the docs explicitly broaden scope
- prefer extending shared contracts and fixtures before adding integrations
- preserve deterministic behavior and testability
- update `AGENTS.md` whenever the repository state materially changes
- keep README and docs aligned with the actual implemented surface area
