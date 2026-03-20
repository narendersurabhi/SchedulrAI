# Phase 3 Execution Board

## Frozen Scope

> Convert narrow natural-language scheduling requests into validated typed contracts, with explicit confidence and clarification behavior before any downstream scheduling or execution occurs.

### Included Scope
- Shared parser-result schema contracts for parsed, clarification-needed, and unsupported outcomes
- A narrow intent parser service that returns validated `SchedulingRequest` payloads for supported requests
- Clarification questions for missing duration, attendee, day, or morning/afternoon details
- Explicit handling for out-of-scope time periods such as evening or noon
- Parsing eval fixtures and unit coverage for supported, ambiguous, and unsupported inputs
- CLI demo output extended to show parse metadata before the scheduling flow continues

### Explicitly Deferred
- Live LLM integration or hosted model calls
- Multi-turn clarification state management
- API endpoints or chat session persistence
- Broad temporal parsing beyond `next <weekday> morning|afternoon`
- Reschedule, cancellation, or meeting-summary parsing intents

## Build-Now Tasks
1. Extend shared schemas with parser output contracts and disposition enums.
2. Add a narrow parser service wrapper that emits validated `SchedulingRequest` payloads.
3. Preserve the deterministic happy-path parser as the validated success path.
4. Add clarification rules for missing duration, attendee, day, and time-of-day fields.
5. Add explicit unsupported handling for out-of-scope wording and time periods.
6. Create a small parsing eval fixture pack with expected dispositions.
7. Add parser regression tests for supported, ambiguous, and unsupported utterances.
8. Update repository tracking docs (`AGENTS.md`) and README to reflect Phase 3 scope.

## End-of-Week Proof Point
Run:

```bash
python -m apps.cli.demo "Schedule 30 minutes with Sarah next Tuesday afternoon"
```

Expected outcome:
- Structured parse metadata emitted first with `disposition: parsed`
- Valid `SchedulingRequest` generated from natural language
- Ranked candidate slots returned deterministically
- A dry-run preview emitted before booking
- The top slot booked through the mock provider
- Audit log entries printed for both preview and real execution
