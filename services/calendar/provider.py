from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from shared.schemas import (
    AvailabilityWindow,
    BookingRequest,
    BookingResult,
    BookingStatus,
    CancelBookingRequest,
    UpdateBookingRequest,
)


class CalendarProvider(Protocol):
    def get_availability(self, attendee_emails: list[str]) -> list[AvailabilityWindow]:
        ...

    def create_event(self, request: BookingRequest) -> BookingResult:
        ...

    def update_event(self, request: UpdateBookingRequest) -> BookingResult:
        ...

    def cancel_event(self, request: CancelBookingRequest) -> BookingResult:
        ...


class MockCalendarProvider:
    def __init__(self, availability: list[AvailabilityWindow]) -> None:
        self._availability = {item.attendee_email: item for item in availability}
        self._events_by_key: dict[str, BookingResult] = {}
        self._events_by_provider_id: dict[str, BookingResult] = {}
        self._provider_event_sequence = 0

    def get_availability(self, attendee_emails: list[str]) -> list[AvailabilityWindow]:
        return [self._availability[email] for email in attendee_emails if email in self._availability]

    def create_event(self, request: BookingRequest) -> BookingResult:
        existing = self._events_by_key.get(request.idempotency_key)
        if existing:
            return existing

        self._provider_event_sequence += 1
        result = BookingResult(
            booking_id=f"booking-{self._provider_event_sequence}",
            status=BookingStatus.CONFIRMED,
            provider_event_id=f"mock-event-{self._provider_event_sequence}",
            message=(
                f"Booked '{request.title}' from {request.slot.start.isoformat()} to {request.slot.end.isoformat()}"
            ),
            slot=request.slot,
        )
        self._events_by_key[request.idempotency_key] = result
        if result.provider_event_id:
            self._events_by_provider_id[result.provider_event_id] = result
        return result

    def update_event(self, request: UpdateBookingRequest) -> BookingResult:
        existing = self._events_by_key.get(request.idempotency_key)
        if existing:
            return existing

        current = self._events_by_provider_id.get(request.provider_event_id)
        if current is None:
            raise KeyError(f"Unknown provider event id: {request.provider_event_id}")

        updated = BookingResult(
            booking_id=request.booking_id,
            status=BookingStatus.UPDATED,
            provider_event_id=request.provider_event_id,
            message=(
                f"Updated '{request.title}' to {request.slot.start.isoformat()} - {request.slot.end.isoformat()}"
            ),
            slot=request.slot,
        )
        self._events_by_key[request.idempotency_key] = updated
        self._events_by_provider_id[request.provider_event_id] = updated
        return updated

    def cancel_event(self, request: CancelBookingRequest) -> BookingResult:
        existing = self._events_by_key.get(request.idempotency_key)
        if existing:
            return existing

        current = self._events_by_provider_id.get(request.provider_event_id)
        if current is None:
            raise KeyError(f"Unknown provider event id: {request.provider_event_id}")

        cancelled = replace(
            current,
            status=BookingStatus.CANCELLED,
            message=f"Cancelled event {request.provider_event_id}: {request.reason or 'no reason provided'}",
        )
        self._events_by_key[request.idempotency_key] = cancelled
        self._events_by_provider_id[request.provider_event_id] = cancelled
        return cancelled
