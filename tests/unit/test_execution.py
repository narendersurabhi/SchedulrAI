from __future__ import annotations

import json
from pathlib import Path

from shared.schemas import (
    AvailabilityWindow,
    BookingRequest,
    BookingStatus,
    CancelBookingRequest,
    CandidateSlot,
    UpdateBookingRequest,
)
from services.calendar.provider import MockCalendarProvider
from services.execution.core import BookingExecutor, InMemoryExecutionAuditLog, build_idempotency_key

FIXTURE_DIR = Path("tests/fixtures")


def load_availability() -> list[AvailabilityWindow]:
    payload = json.loads((FIXTURE_DIR / "mock_availability.json").read_text())
    return [AvailabilityWindow.model_validate(item) for item in payload]


def build_slot(start: str, end: str) -> CandidateSlot:
    return CandidateSlot(start=start, end=end, score=115.0, reason_codes=["works_for_all_attendees"])


def test_preview_does_not_create_provider_event() -> None:
    provider = MockCalendarProvider(load_availability())
    executor = BookingExecutor(provider=provider, audit_log=InMemoryExecutionAuditLog())
    request = BookingRequest(
        request_id="req-preview",
        title="30-minute sync with Sarah",
        slot=build_slot("2026-03-24T14:00:00-04:00", "2026-03-24T14:30:00-04:00"),
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key=build_idempotency_key(
            request_id="req-preview",
            action="create_booking",
            unique_value="2026-03-24T14:00:00-04:00",
        ),
    )

    outcome = executor.preview_create(request)

    assert outcome.result.status is BookingStatus.PREVIEW
    assert outcome.result.provider_event_id is None
    assert outcome.audit_entry.dry_run is True


def test_create_update_and_cancel_flows_are_audited() -> None:
    provider = MockCalendarProvider(load_availability())
    audit_log = InMemoryExecutionAuditLog()
    executor = BookingExecutor(provider=provider, audit_log=audit_log)
    create_request = BookingRequest(
        request_id="req-2",
        title="30-minute sync with Sarah",
        slot=build_slot("2026-03-24T14:00:00-04:00", "2026-03-24T14:30:00-04:00"),
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key=build_idempotency_key(
            request_id="req-2",
            action="create_booking",
            unique_value="2026-03-24T14:00:00-04:00",
        ),
    )

    created = executor.create_booking(create_request)
    update_request = UpdateBookingRequest(
        request_id="req-2",
        booking_id=created.result.booking_id,
        provider_event_id=created.result.provider_event_id or "",
        title="30-minute sync with Sarah",
        slot=build_slot("2026-03-24T15:30:00-04:00", "2026-03-24T16:00:00-04:00"),
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key=build_idempotency_key(
            request_id="req-2",
            action="update_booking",
            unique_value="2026-03-24T15:30:00-04:00",
        ),
    )
    updated = executor.update_booking(update_request)
    cancel_request = CancelBookingRequest(
        request_id="req-2",
        booking_id=updated.result.booking_id,
        provider_event_id=updated.result.provider_event_id or "",
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key=build_idempotency_key(
            request_id="req-2",
            action="cancel_booking",
            unique_value=updated.result.provider_event_id or "",
        ),
        reason="Requester cancelled",
    )
    cancelled = executor.cancel_booking(cancel_request)

    assert created.result.status is BookingStatus.CONFIRMED
    assert updated.result.status is BookingStatus.UPDATED
    assert cancelled.result.status is BookingStatus.CANCELLED
    assert [entry.action for entry in audit_log.list_entries()] == [
        "create_booking",
        "update_booking",
        "cancel_booking",
    ]


def test_retrying_same_idempotency_key_does_not_duplicate_event() -> None:
    provider = MockCalendarProvider(load_availability())
    executor = BookingExecutor(provider=provider, audit_log=InMemoryExecutionAuditLog())
    request = BookingRequest(
        request_id="req-3",
        title="30-minute sync with Sarah",
        slot=build_slot("2026-03-24T14:00:00-04:00", "2026-03-24T14:30:00-04:00"),
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key=build_idempotency_key(
            request_id="req-3",
            action="create_booking",
            unique_value="2026-03-24T14:00:00-04:00",
        ),
    )

    first = executor.create_booking(request)
    second = executor.create_booking(request)

    assert first.result.booking_id == second.result.booking_id
    assert first.result.provider_event_id == second.result.provider_event_id
