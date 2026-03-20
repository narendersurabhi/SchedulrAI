from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from shared.schemas import Attendee, SchedulingPreferences, SchedulingRequest, TimeRange

_REQUEST_PATTERN = re.compile(
    r"schedule\s+(?P<duration>\d+)\s+minutes\s+with\s+(?P<attendee>[A-Za-z]+)\s+next\s+(?P<weekday>[A-Za-z]+)\s+(?P<period>morning|afternoon)",
    re.IGNORECASE,
)
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

    preferred_start = datetime.combine(target_date, time(14, 0), tzinfo=tz)
    preferred_end = datetime.combine(target_date, time(16, 0), tzinfo=tz)

    attendee_email = f"{attendee_name.lower()}@example.com"
    return SchedulingRequest(
        request_id=f"req-{target_date.isoformat()}-{attendee_name.lower()}",
        title=f"30-minute sync with {attendee_name}",
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


def _next_weekday(reference_date, target_weekday: int):
    days_ahead = (target_weekday - reference_date.weekday()) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead
    return reference_date + timedelta(days=days_ahead)
