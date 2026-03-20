from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SchemaMixin:
    @classmethod
    def model_validate(cls, payload: dict[str, Any]):
        return cls.from_dict(payload)

    def model_dump(self, mode: str = "python") -> dict[str, Any]:
        dumped = _serialize(asdict(self), mode=mode)
        return dumped


class AttendeeRole(str, Enum):
    ORGANIZER = "organizer"
    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass(slots=True)
class Attendee(SchemaMixin):
    name: str
    email: str | None = None
    role: AttendeeRole | str = AttendeeRole.REQUIRED
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        if isinstance(self.role, str):
            self.role = AttendeeRole(self.role)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Attendee":
        return cls(**payload)


@dataclass(slots=True)
class TimeRange(SchemaMixin):
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        self.start = _parse_datetime(self.start)
        self.end = _parse_datetime(self.end)
        if self.end <= self.start:
            raise ValueError("end must be after start")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TimeRange":
        return cls(start=payload["start"], end=payload["end"])


@dataclass(slots=True)
class SchedulingPreferences(SchemaMixin):
    preferred_time_ranges: list[TimeRange] = field(default_factory=list)
    avoid_time_ranges: list[TimeRange] = field(default_factory=list)
    minimum_notice_minutes: int = 60
    buffer_before_minutes: int = 0
    buffer_after_minutes: int = 0

    def __post_init__(self) -> None:
        self.preferred_time_ranges = [_coerce_time_range(item) for item in self.preferred_time_ranges]
        self.avoid_time_ranges = [_coerce_time_range(item) for item in self.avoid_time_ranges]
        for value in (
            self.minimum_notice_minutes,
            self.buffer_before_minutes,
            self.buffer_after_minutes,
        ):
            if value < 0:
                raise ValueError("preference values must be non-negative")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SchedulingPreferences":
        return cls(**payload)


@dataclass(slots=True)
class SchedulingRequest(SchemaMixin):
    request_id: str
    title: str
    organizer: Attendee
    attendees: list[Attendee]
    duration_minutes: int
    timezone: str
    availability_window: TimeRange
    preferences: SchedulingPreferences = field(default_factory=SchedulingPreferences)
    intent: str = "schedule_meeting"
    source_text: str | None = None

    def __post_init__(self) -> None:
        self.organizer = _coerce_attendee(self.organizer)
        self.attendees = [_coerce_attendee(item) for item in self.attendees]
        self.availability_window = _coerce_time_range(self.availability_window)
        if isinstance(self.preferences, dict):
            self.preferences = SchedulingPreferences.from_dict(self.preferences)
        if self.duration_minutes <= 0 or self.duration_minutes > 8 * 60:
            raise ValueError("duration_minutes must be between 1 and 480")
        if self.intent != "schedule_meeting":
            raise ValueError("intent must be 'schedule_meeting'")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SchedulingRequest":
        return cls(**payload)


@dataclass(slots=True)
class AvailabilityWindow(SchemaMixin):
    attendee_email: str
    busy: list[TimeRange] = field(default_factory=list)
    working_hours: list[TimeRange] = field(default_factory=list)
    focus_blocks: list[TimeRange] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.busy = [_coerce_time_range(item) for item in self.busy]
        self.working_hours = [_coerce_time_range(item) for item in self.working_hours]
        self.focus_blocks = [_coerce_time_range(item) for item in self.focus_blocks]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AvailabilityWindow":
        return cls(**payload)


@dataclass(slots=True)
class CandidateSlot(SchemaMixin):
    start: datetime
    end: datetime
    score: float
    reason_codes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.start = _parse_datetime(self.start)
        self.end = _parse_datetime(self.end)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CandidateSlot":
        return cls(**payload)


@dataclass(slots=True)
class SchedulingDecision(SchemaMixin):
    request_id: str
    selected_slots: list[CandidateSlot]
    rejected_slots: list[CandidateSlot] = field(default_factory=list)
    explanation: str = ""

    def __post_init__(self) -> None:
        self.selected_slots = [_coerce_candidate_slot(item) for item in self.selected_slots]
        self.rejected_slots = [_coerce_candidate_slot(item) for item in self.rejected_slots]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SchedulingDecision":
        return cls(**payload)


@dataclass(slots=True)
class BookingRequest(SchemaMixin):
    request_id: str
    title: str
    slot: CandidateSlot
    organizer_email: str
    attendee_emails: list[str]
    idempotency_key: str

    def __post_init__(self) -> None:
        self.slot = _coerce_candidate_slot(self.slot)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BookingRequest":
        return cls(**payload)


@dataclass(slots=True)
class BookingResult(SchemaMixin):
    booking_id: str
    status: str
    provider_event_id: str | None = None
    message: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BookingResult":
        return cls(**payload)


def _parse_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _coerce_attendee(value: Attendee | dict[str, Any]) -> Attendee:
    return value if isinstance(value, Attendee) else Attendee.from_dict(value)


def _coerce_time_range(value: TimeRange | dict[str, Any]) -> TimeRange:
    return value if isinstance(value, TimeRange) else TimeRange.from_dict(value)


def _coerce_candidate_slot(value: CandidateSlot | dict[str, Any]) -> CandidateSlot:
    return value if isinstance(value, CandidateSlot) else CandidateSlot.from_dict(value)


def _serialize(value: Any, *, mode: str) -> Any:
    if isinstance(value, dict):
        return {key: _serialize(item, mode=mode) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item, mode=mode) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat() if mode == "json" else value
    return value
