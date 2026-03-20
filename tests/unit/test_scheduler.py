from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from shared.schemas import Attendee, AvailabilityWindow, BookingRequest, SchedulingRequest
from services.calendar.provider import MockCalendarProvider
from services.intent_parser.happy_path import parse_happy_path_request
from services.scheduler.core import DeterministicScheduler

FIXTURE_DIR = Path("tests/fixtures")


def load_availability() -> list[AvailabilityWindow]:
    payload = json.loads((FIXTURE_DIR / "mock_availability.json").read_text())
    return [AvailabilityWindow.model_validate(item) for item in payload]


def load_request() -> SchedulingRequest:
    payload = json.loads((FIXTURE_DIR / "scheduling_request.json").read_text())
    return SchedulingRequest.model_validate(payload)


def test_schema_fixture_is_valid() -> None:
    request = load_request()
    assert request.duration_minutes == 30
    assert request.attendees[0].email == "sarah@example.com"


def test_happy_path_parser_creates_expected_request() -> None:
    organizer = Attendee(name="Alex", email="alex@example.com", role="organizer", timezone="America/New_York")
    reference_dt = datetime.fromisoformat("2026-03-19T09:00:00-04:00")

    request = parse_happy_path_request(
        "Schedule 30 minutes with Sarah next Tuesday afternoon",
        organizer=organizer,
        reference_dt=reference_dt,
    )

    assert request.attendees[0].email == "sarah@example.com"
    assert request.availability_window.start.isoformat() == "2026-03-24T13:00:00-04:00"
    assert request.preferences.preferred_time_ranges[0].start.isoformat() == "2026-03-24T14:00:00-04:00"


def test_scheduler_ranks_expected_top_slot() -> None:
    provider = MockCalendarProvider(load_availability())
    scheduler = DeterministicScheduler(provider)
    decision = scheduler.recommend_slots(load_request())

    assert len(decision.selected_slots) == 3
    assert decision.selected_slots[0].start.isoformat() == "2026-03-24T14:00:00-04:00"
    assert "preferred_time_window_bonus" in decision.selected_slots[0].reason_codes
    rejected_codes = {code for slot in decision.rejected_slots for code in slot.reason_codes}
    assert "conflicts_with_existing_event" in rejected_codes


def test_mock_provider_create_event_is_idempotent() -> None:
    provider = MockCalendarProvider(load_availability())
    slot = DeterministicScheduler(provider).recommend_slots(load_request()).selected_slots[0]
    booking_request = BookingRequest(
        request_id="req-1",
        title="30-minute sync with Sarah",
        slot=slot,
        organizer_email="alex@example.com",
        attendee_emails=["sarah@example.com"],
        idempotency_key="req-1:2026-03-24T14:00:00-04:00",
    )

    first = provider.create_event(booking_request)
    second = provider.create_event(booking_request)

    assert first.booking_id == second.booking_id
    assert first.provider_event_id == second.provider_event_id
