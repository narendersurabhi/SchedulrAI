from __future__ import annotations

from typing import Protocol

from shared.schemas import AvailabilityWindow, BookingRequest, BookingResult, CandidateSlot


class CalendarProvider(Protocol):
    def get_availability(self, attendee_emails: list[str]) -> list[AvailabilityWindow]:
        ...

    def create_event(self, request: BookingRequest) -> BookingResult:
        ...


class MockCalendarProvider:
    def __init__(self, availability: list[AvailabilityWindow]) -> None:
        self._availability = {item.attendee_email: item for item in availability}
        self._events_by_key: dict[str, BookingResult] = {}

    def get_availability(self, attendee_emails: list[str]) -> list[AvailabilityWindow]:
        return [self._availability[email] for email in attendee_emails if email in self._availability]

    def create_event(self, request: BookingRequest) -> BookingResult:
        existing = self._events_by_key.get(request.idempotency_key)
        if existing:
            return existing

        result = BookingResult(
            booking_id=f"booking-{len(self._events_by_key) + 1}",
            status="confirmed",
            provider_event_id=f"mock-event-{len(self._events_by_key) + 1}",
            message=(
                f"Booked '{request.title}' from {request.slot.start.isoformat()} to {request.slot.end.isoformat()}"
            ),
        )
        self._events_by_key[request.idempotency_key] = result
        return result
