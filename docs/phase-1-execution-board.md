# Phase 1 Execution Board

## Frozen Happy-Path Scenario

> Schedule 30 minutes with Sarah next Tuesday afternoon.

### Included Scope
- One organizer and one attendee
- Single timezone: `America/New_York`
- Single calendar provider abstraction backed by a mock provider
- One-shot meeting only
- Deterministic ranking with reason codes
- Happy-path natural language parser for one narrow request shape
- Mock booking confirmation to prove the thin vertical slice

### Explicitly Deferred
- Real Google Calendar OAuth/free-busy integration
- Multi-attendee optimization
- Recurrence, rescheduling, cancellation, and decline handling
- FastAPI service surface
- LLM-based parsing and clarification flows
- Persistent audit log storage

## Build-Now Tasks
1. Define shared contracts for scheduling and booking artifacts.
2. Add example JSON payloads that validate against the shared schemas.
3. Add a mock calendar provider with free/busy reads and idempotent event creation.
4. Build deterministic candidate-slot generation and ranking.
5. Add reason-code explanations for accepted and rejected slots.
6. Add a narrow happy-path natural language parser.
7. Add fixture-backed eval cases for scheduler behavior.
8. Create a CLI demo that parses, schedules, and books the top slot.
9. Add unit tests covering schema validation, parser output, ranking, and idempotency.
10. Update repository tracking docs (`AGENTS.md`) with the new status.

## End-of-Week Proof Point
Run:

```bash
python -m apps.cli.demo "Schedule 30 minutes with Sarah next Tuesday afternoon"
```

Expected outcome:
- Valid `SchedulingRequest` generated from natural language
- Top candidate slots ranked deterministically
- Best slot booked through the mock provider with an idempotent booking result
