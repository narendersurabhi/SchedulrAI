# Repository Agent Notes

## Current Status
- Repository now contains the first implementation scaffold for the SchedulrAI thin vertical slice.
- Primary code artifacts added for this slice:
  - `shared/schemas/scheduling.py` for shared scheduling and booking contracts
  - `services/calendar/provider.py` for the provider interface and mock calendar implementation
  - `services/scheduler/core.py` for deterministic candidate generation and ranking
  - `services/intent_parser/happy_path.py` for the narrow happy-path natural language parser
  - `apps/cli/demo.py` for an end-to-end CLI demo that parses, ranks, and books the top slot
- Supporting fixtures, evals, tests, and execution-board documentation were added to anchor Phase 1 execution.

## Change Log
- 2026-03-19: Added `docs/implementation-roadmap.md`, a phase-by-phase implementation plan covering milestones, repo issue backlog, module boundaries, evaluation gates, and week-by-week deliverables.
- 2026-03-19: Added `docs/system-design.md`, a full system design document covering requirements, architecture, components, lifecycle flows, sequence diagrams, data model, APIs, deployment architecture, security, observability, risks, and future enhancements.
- 2026-03-19: Created this root `AGENTS.md` file to track repository state and provide context for future agents, per user instruction.
- 2026-03-19: Added `pyproject.toml` to establish the initial Python project scaffold and `pytest` support.
- 2026-03-19: Added shared scheduling/booking contracts in `shared/schemas/scheduling.py` and re-exported them via `shared/schemas/__init__.py`.
- 2026-03-19: Added `services/calendar/provider.py` with the `CalendarProvider` protocol and an idempotent `MockCalendarProvider` for fixture-backed availability and booking.
- 2026-03-19: Added `services/scheduler/core.py` with deterministic slot generation, hard-constraint filtering, soft scoring, and reason-code explanations.
- 2026-03-19: Added `services/intent_parser/happy_path.py` with a narrow regex-based parser for the first frozen scenario: “Schedule 30 minutes with Sarah next Tuesday afternoon.”
- 2026-03-19: Added `apps/cli/demo.py` for a demoable parse → schedule → book flow using the mock provider.
- 2026-03-19: Added fixture payloads under `tests/fixtures/`, unit tests under `tests/unit/`, scheduling evals under `evals/scheduling/`, and `docs/phase-1-execution-board.md` to freeze the first implementation milestone.

## Guidance for Future Agents
- Read this file before making changes.
- Keep this file updated whenever repository contents or project status changes.
- Treat `docs/system-design.md` as the canonical high-level architecture reference until implementation files are added.
- Treat `docs/implementation-roadmap.md` as the canonical execution plan for milestones, issue slicing, and weekly delivery sequencing.
- Treat `docs/phase-1-execution-board.md` as the canonical scope freeze for the current happy-path implementation slice.
- Prefer extending the shared contracts and fixtures before adding new integrations or orchestration layers.
- Keep the current slice narrow until the mocked demo path and tests remain stable.
