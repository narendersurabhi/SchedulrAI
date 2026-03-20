from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from shared.schemas import Attendee, AvailabilityWindow, BookingRequest
from services.calendar.provider import MockCalendarProvider
from services.execution.core import BookingExecutor, InMemoryExecutionAuditLog, build_idempotency_key
from services.intent_parser.happy_path import parse_happy_path_request
from services.scheduler.core import DeterministicScheduler

FIXTURE_PATH = Path("tests/fixtures/mock_availability.json")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m apps.cli.demo \"Schedule 30 minutes with Sarah next Tuesday afternoon\"")
        return 1

    request_text = sys.argv[1]
    organizer = Attendee(name="Alex", email="alex@example.com", role="organizer", timezone="America/New_York")
    reference_dt = datetime.fromisoformat("2026-03-19T09:00:00-04:00")
    provider = MockCalendarProvider(_load_availability())
    executor = BookingExecutor(provider=provider, audit_log=InMemoryExecutionAuditLog())

    request = parse_happy_path_request(request_text, organizer=organizer, reference_dt=reference_dt)
    scheduler = DeterministicScheduler(provider)
    decision = scheduler.recommend_slots(request)

    slot = decision.selected_slots[0]
    booking_request = BookingRequest(
        request_id=request.request_id,
        title=request.title,
        slot=slot,
        organizer_email=request.organizer.email or "",
        attendee_emails=[att.email or "" for att in request.attendees],
        idempotency_key=build_idempotency_key(
            request_id=request.request_id,
            action="create_booking",
            unique_value=slot.start.isoformat(),
        ),
        description="Thin-slice demo booking",
    )
    preview = executor.preview_create(booking_request)
    booking_outcome = executor.create_booking(booking_request)

    output = {
        "request": request.model_dump(mode="json"),
        "decision": decision.model_dump(mode="json"),
        "preview": preview.model_dump(mode="json"),
        "booking_outcome": booking_outcome.model_dump(mode="json"),
        "audit_log": [entry.model_dump(mode="json") for entry in executor.audit_log.list_entries()],
    }
    print(json.dumps(output, indent=2))
    return 0


def _load_availability() -> list[AvailabilityWindow]:
    payload = json.loads(FIXTURE_PATH.read_text())
    return [AvailabilityWindow.model_validate(item) for item in payload]


if __name__ == "__main__":
    raise SystemExit(main())
