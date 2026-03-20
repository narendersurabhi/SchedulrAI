from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from shared.schemas import (
    Attendee,
    IntentParseResult,
    ParserDisposition,
    SchedulingPreferences,
    SchedulingRequest,
    TimeRange,
)

_REQUEST_PATTERN = re.compile(
    r"schedule\s+(?P<duration>\d+)\s+minutes\s+with\s+(?P<attendee>[A-Za-z]+)\s+next\s+(?P<weekday>[A-Za-z]+)\s+(?P<period>morning|afternoon)",
    re.IGNORECASE,
)
_DURATION_PATTERN = re.compile(r"(?P<duration>\d+)\s+minutes", re.IGNORECASE)
_ATTENDEE_PATTERN = re.compile(r"with\s+(?P<attendee>[A-Za-z]+)", re.IGNORECASE)
_WEEKDAY_PATTERN = re.compile(r"next\s+(?P<weekday>[A-Za-z]+)", re.IGNORECASE)
_PERIOD_PATTERN = re.compile(r"\b(?P<period>morning|afternoon)\b", re.IGNORECASE)
_UNSUPPORTED_PERIOD_PATTERN = re.compile(r"\b(?P<period>evening|night|lunchtime|noon)\b", re.IGNORECASE)
_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

_PERIOD_WINDOWS = {
    "morning": (time(9, 0), time(12, 0)),
    "afternoon": (time(13, 0), time(17, 0)),
}


@dataclass(slots=True)
class NarrowIntentParser:
    parser_version: str = "phase3-narrow"

    def parse(self, text: str, *, organizer: Attendee, reference_dt: datetime) -> IntentParseResult:
        stripped_text = text.strip()
        exact_match = _REQUEST_PATTERN.fullmatch(stripped_text)
        if exact_match:
            request = parse_happy_path_request(stripped_text, organizer=organizer, reference_dt=reference_dt)
            return IntentParseResult(
                raw_text=text,
                disposition=ParserDisposition.PARSED,
                confidence=0.98,
                request=request,
                parser_version=self.parser_version,
                message="Parsed scheduling request into a validated SchedulingRequest.",
            )

        lowered = stripped_text.lower()
        if not lowered.startswith("schedule"):
            return IntentParseResult(
                raw_text=text,
                disposition=ParserDisposition.UNSUPPORTED,
                confidence=0.12,
                parser_version=self.parser_version,
                message="This thin-slice parser currently supports only scheduling requests that begin with 'schedule'.",
            )

        missing_fields: list[str] = []
        attendee_match = _ATTENDEE_PATTERN.search(stripped_text)
        duration_match = _DURATION_PATTERN.search(stripped_text)
        weekday_match = _WEEKDAY_PATTERN.search(stripped_text)
        period_match = _PERIOD_PATTERN.search(stripped_text)
        unsupported_period_match = _UNSUPPORTED_PERIOD_PATTERN.search(stripped_text)

        if attendee_match is None:
            missing_fields.append("attendee")
        if duration_match is None:
            missing_fields.append("duration_minutes")
        if weekday_match is None:
            missing_fields.append("day")
        elif weekday_match.group("weekday").lower() not in _WEEKDAYS:
            missing_fields.append("day")
        if period_match is None:
            missing_fields.append("time_of_day")

        if unsupported_period_match is not None:
            unsupported_period = unsupported_period_match.group("period").lower()
            return IntentParseResult(
                raw_text=text,
                disposition=ParserDisposition.NEEDS_CLARIFICATION,
                confidence=0.44,
                clarification_question=(
                    f"I currently support morning or afternoon windows, not {unsupported_period}. Should I look in the morning or afternoon?"
                ),
                missing_fields=["time_of_day"],
                parser_version=self.parser_version,
                message="The request used a time-of-day that is outside the current thin-slice parser scope.",
            )

        if missing_fields:
            return IntentParseResult(
                raw_text=text,
                disposition=ParserDisposition.NEEDS_CLARIFICATION,
                confidence=max(0.25, 0.8 - (0.15 * len(missing_fields))),
                clarification_question=_build_clarification_question(missing_fields),
                missing_fields=missing_fields,
                parser_version=self.parser_version,
                message="The request is close to the supported format, but key scheduling details are still missing.",
            )

        return IntentParseResult(
            raw_text=text,
            disposition=ParserDisposition.UNSUPPORTED,
            confidence=0.2,
            parser_version=self.parser_version,
            message=(
                "The request could not be safely mapped into the current scheduling schema. "
                "Use a format like 'Schedule 30 minutes with Sarah next Tuesday afternoon'."
            ),
        )


def parse_happy_path_request(text: str, *, organizer: Attendee, reference_dt: datetime) -> SchedulingRequest:
    match = _REQUEST_PATTERN.fullmatch(text.strip())
    if not match:
        raise ValueError(
            "This thin-slice parser currently supports requests like 'Schedule 30 minutes with Sarah next Tuesday afternoon'."
        )

    duration = int(match.group("duration"))
    attendee_name = match.group("attendee")
    weekday = match.group("weekday").lower()
    period = match.group("period").lower()
    target_date = _next_weekday(reference_dt.date(), _WEEKDAYS[weekday])
    tz = ZoneInfo(organizer.timezone)
    start_time, end_time = _PERIOD_WINDOWS[period]
    window_start = datetime.combine(target_date, start_time, tzinfo=tz)
    window_end = datetime.combine(target_date, end_time, tzinfo=tz)

    preferred_start, preferred_end = _preferred_window(period=period, target_date=target_date, timezone=tz)

    attendee_email = f"{attendee_name.lower()}@example.com"
    return SchedulingRequest(
        request_id=f"req-{target_date.isoformat()}-{attendee_name.lower()}",
        title=f"{duration}-minute sync with {attendee_name}",
        organizer=organizer,
        attendees=[Attendee(name=attendee_name, email=attendee_email, timezone=organizer.timezone)],
        duration_minutes=duration,
        timezone=organizer.timezone,
        availability_window=TimeRange(start=window_start, end=window_end),
        preferences=SchedulingPreferences(
            preferred_time_ranges=[TimeRange(start=preferred_start, end=preferred_end)],
            minimum_notice_minutes=60,
        ),
        source_text=text,
    )


def _build_clarification_question(missing_fields: list[str]) -> str:
    field_labels = {
        "attendee": "who the meeting is with",
        "duration_minutes": "how many minutes the meeting should last",
        "day": "which day to target",
        "time_of_day": "whether to search in the morning or afternoon",
    }
    details = [field_labels[field_name] for field_name in missing_fields]
    if len(details) == 1:
        return f"I can help schedule that, but I still need {details[0]}."
    if len(details) == 2:
        return f"I can help schedule that, but I still need {details[0]} and {details[1]}."
    return "I can help schedule that, but I still need " + ", ".join(details[:-1]) + f", and {details[-1]}."


def _preferred_window(*, period: str, target_date: date, timezone: ZoneInfo) -> tuple[datetime, datetime]:
    if period == "morning":
        preferred_start = datetime.combine(target_date, time(9, 30), tzinfo=timezone)
        preferred_end = datetime.combine(target_date, time(11, 0), tzinfo=timezone)
        return preferred_start, preferred_end

    preferred_start = datetime.combine(target_date, time(14, 0), tzinfo=timezone)
    preferred_end = datetime.combine(target_date, time(16, 0), tzinfo=timezone)
    return preferred_start, preferred_end


def _next_weekday(reference_date: date, target_weekday: int) -> date:
    days_ahead = (target_weekday - reference_date.weekday()) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead
    return reference_date + timedelta(days=days_ahead)
