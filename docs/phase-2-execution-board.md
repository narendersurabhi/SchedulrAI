# Phase 2 Execution Board

## Frozen Scope

> Safely convert approved slots into provider-backed calendar events with retry-safe writes and an inspectable audit trail.

### Included Scope
- Create, update, and cancel executor flows backed by the mock calendar provider
- Deterministic idempotency-key generation for write actions
- Dry-run previews before provider writes
- In-memory audit log entries for every execution attempt
- CLI demo output extended to show preview and audit records
- Unit coverage for preview, create, update, cancel, and retry safety

### Explicitly Deferred
- Persistent database-backed audit storage
- Real Google Calendar or Outlook write integrations
- Webhook-driven async workflow handling
- Multi-attendee reschedule negotiation
- API endpoints or UI-based confirmation flows

## Build-Now Tasks
1. Extend shared schemas for execution requests, results, and audit entries.
2. Expand the calendar provider contract to support update and cancel operations.
3. Add an execution service that wraps provider writes and records audit entries.
4. Introduce dry-run previews for create, update, and cancel actions.
5. Reuse deterministic idempotency keys to protect retry behavior.
6. Update the CLI demo to expose preview, execution, and audit output.
7. Add unit tests for create/update/cancel flows and retry safety.
8. Update repository tracking docs (`AGENTS.md`) and README to reflect Phase 2 scope.

## End-of-Week Proof Point
Run:

```bash
python -m apps.cli.demo "Schedule 30 minutes with Sarah next Tuesday afternoon"
```

Expected outcome:
- Valid `SchedulingRequest` generated from natural language
- Ranked candidate slots returned deterministically
- A dry-run preview emitted before booking
- The top slot booked through the mock provider
- Audit log entries printed for both preview and real execution
