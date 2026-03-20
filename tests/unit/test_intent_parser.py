from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from shared.schemas import Attendee, ParserDisposition
from services.intent_parser.happy_path import NarrowIntentParser, parse_happy_path_request

EVAL_FIXTURE_PATH = Path("evals/parsing/seed_requests.json")


def build_organizer() -> Attendee:
    return Attendee(name="Alex", email="alex@example.com", role="organizer", timezone="America/New_York")


def build_reference_dt() -> datetime:
    return datetime.fromisoformat("2026-03-19T09:00:00-04:00")


def test_happy_path_parser_creates_expected_request() -> None:
    request = parse_happy_path_request(
        "Schedule 30 minutes with Sarah next Tuesday afternoon",
        organizer=build_organizer(),
        reference_dt=build_reference_dt(),
    )

    assert request.title == "30-minute sync with Sarah"
    assert request.attendees[0].email == "sarah@example.com"
    assert request.availability_window.start.isoformat() == "2026-03-24T13:00:00-04:00"
    assert request.preferences.preferred_time_ranges[0].start.isoformat() == "2026-03-24T14:00:00-04:00"


def test_narrow_intent_parser_returns_structured_parse_for_supported_request() -> None:
    result = NarrowIntentParser().parse(
        "Schedule 45 minutes with Priya next Wednesday morning",
        organizer=build_organizer(),
        reference_dt=build_reference_dt(),
    )

    assert result.disposition is ParserDisposition.PARSED
    assert result.confidence >= 0.9
    assert result.request is not None
    assert result.request.duration_minutes == 45
    assert result.request.availability_window.start.isoformat() == "2026-03-25T09:00:00-04:00"
    assert result.request.preferences.preferred_time_ranges[0].start.isoformat() == "2026-03-25T09:30:00-04:00"


def test_narrow_intent_parser_requests_clarification_for_missing_fields() -> None:
    result = NarrowIntentParser().parse(
        "Schedule with Sarah next Tuesday",
        organizer=build_organizer(),
        reference_dt=build_reference_dt(),
    )

    assert result.disposition is ParserDisposition.NEEDS_CLARIFICATION
    assert result.request is None
    assert result.missing_fields == ["duration_minutes", "time_of_day"]
    assert "how many minutes" in (result.clarification_question or "")
    assert "morning or afternoon" in (result.clarification_question or "")


def test_narrow_intent_parser_flags_unsupported_time_period() -> None:
    result = NarrowIntentParser().parse(
        "Schedule 30 minutes with Sarah next Tuesday evening",
        organizer=build_organizer(),
        reference_dt=build_reference_dt(),
    )

    assert result.disposition is ParserDisposition.NEEDS_CLARIFICATION
    assert result.missing_fields == ["time_of_day"]
    assert "morning or afternoon" in (result.clarification_question or "")


def test_parsing_eval_fixture_matches_expected_dispositions() -> None:
    parser = NarrowIntentParser()
    payload = json.loads(EVAL_FIXTURE_PATH.read_text())

    for case in payload:
        result = parser.parse(case["text"], organizer=build_organizer(), reference_dt=build_reference_dt())
        assert result.disposition.value == case["expected_disposition"]
        assert result.missing_fields == case.get("expected_missing_fields", [])
