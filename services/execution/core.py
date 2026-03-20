from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from shared.schemas import (
    BookingRequest,
    BookingResult,
    BookingStatus,
    CancelBookingRequest,
    ExecutionAuditEntry,
    ExecutionOutcome,
    UpdateBookingRequest,
)

from services.calendar.provider import CalendarProvider


class ExecutionAuditLog:
    def record(self, entry: ExecutionAuditEntry) -> ExecutionAuditEntry:
        raise NotImplementedError

    def list_entries(self) -> list[ExecutionAuditEntry]:
        raise NotImplementedError


class InMemoryExecutionAuditLog(ExecutionAuditLog):
    def __init__(self) -> None:
        self._entries: list[ExecutionAuditEntry] = []

    def record(self, entry: ExecutionAuditEntry) -> ExecutionAuditEntry:
        self._entries.append(entry)
        return entry

    def list_entries(self) -> list[ExecutionAuditEntry]:
        return list(self._entries)


@dataclass(slots=True)
class BookingExecutor:
    provider: CalendarProvider
    audit_log: ExecutionAuditLog

    def preview_create(self, request: BookingRequest) -> ExecutionOutcome:
        result = BookingResult(
            booking_id=f"preview-{request.request_id}",
            status=BookingStatus.PREVIEW,
            provider_event_id=None,
            message=(
                f"Dry-run preview for '{request.title}' from {request.slot.start.isoformat()} to {request.slot.end.isoformat()}"
            ),
            slot=request.slot,
        )
        return self._record_outcome(
            action="create_preview",
            request_id=request.request_id,
            idempotency_key=request.idempotency_key,
            result=result,
            dry_run=True,
        )

    def create_booking(self, request: BookingRequest, *, dry_run: bool = False) -> ExecutionOutcome:
        if dry_run:
            return self.preview_create(request)
        result = self.provider.create_event(request)
        return self._record_outcome(
            action="create_booking",
            request_id=request.request_id,
            idempotency_key=request.idempotency_key,
            result=result,
            dry_run=False,
        )

    def update_booking(self, request: UpdateBookingRequest, *, dry_run: bool = False) -> ExecutionOutcome:
        if dry_run:
            result = BookingResult(
                booking_id=request.booking_id,
                status=BookingStatus.PREVIEW,
                provider_event_id=request.provider_event_id,
                message=(
                    f"Dry-run update preview for '{request.title}' to {request.slot.start.isoformat()} - {request.slot.end.isoformat()}"
                ),
                slot=request.slot,
            )
        else:
            result = self.provider.update_event(request)
        return self._record_outcome(
            action="update_booking",
            request_id=request.request_id,
            idempotency_key=request.idempotency_key,
            result=result,
            dry_run=dry_run,
        )

    def cancel_booking(self, request: CancelBookingRequest, *, dry_run: bool = False) -> ExecutionOutcome:
        if dry_run:
            result = BookingResult(
                booking_id=request.booking_id,
                status=BookingStatus.PREVIEW,
                provider_event_id=request.provider_event_id,
                message=f"Dry-run cancellation preview for {request.provider_event_id}",
                slot=None,
            )
        else:
            result = self.provider.cancel_event(request)
        return self._record_outcome(
            action="cancel_booking",
            request_id=request.request_id,
            idempotency_key=request.idempotency_key,
            result=result,
            dry_run=dry_run,
        )

    def _record_outcome(
        self,
        *,
        action: str,
        request_id: str,
        idempotency_key: str,
        result: BookingResult,
        dry_run: bool,
    ) -> ExecutionOutcome:
        entry = ExecutionAuditEntry(
            audit_id=build_idempotency_key(request_id=request_id, action=action, unique_value=idempotency_key),
            request_id=request_id,
            action=action,
            idempotency_key=idempotency_key,
            status=result.status,
            dry_run=dry_run,
            created_at=datetime.now(timezone.utc),
            provider_event_id=result.provider_event_id,
            booking_id=result.booking_id,
            message=result.message,
        )
        audit_entry = self.audit_log.record(entry)
        return ExecutionOutcome(action=action, result=result, audit_entry=audit_entry)


def build_idempotency_key(*, request_id: str, action: str, unique_value: str) -> str:
    payload = f"{request_id}:{action}:{unique_value}".encode()
    return sha256(payload).hexdigest()[:16]
