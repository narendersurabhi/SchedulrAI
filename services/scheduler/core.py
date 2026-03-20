from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from shared.schemas import CandidateSlot, SchedulingDecision, SchedulingRequest, TimeRange

from services.calendar.provider import CalendarProvider


@dataclass(slots=True)
class SchedulerConfig:
    slot_increment_minutes: int = 30
    top_k: int = 3


class DeterministicScheduler:
    def __init__(self, provider: CalendarProvider, config: SchedulerConfig | None = None) -> None:
        self.provider = provider
        self.config = config or SchedulerConfig()

    def recommend_slots(self, request: SchedulingRequest) -> SchedulingDecision:
        attendee_emails = [request.organizer.email] + [att.email for att in request.attendees if att.email]
        availability = self.provider.get_availability([email for email in attendee_emails if email])

        accepted: list[CandidateSlot] = []
        rejected: list[CandidateSlot] = []
        current_start = request.availability_window.start
        step = timedelta(minutes=self.config.slot_increment_minutes)
        duration = timedelta(minutes=request.duration_minutes)
        latest_start = request.availability_window.end - duration

        while current_start <= latest_start:
            slot = TimeRange(start=current_start, end=current_start + duration)
            slot_candidate = self._evaluate_slot(request, slot, availability)
            if slot_candidate.score >= 0:
                accepted.append(slot_candidate)
            else:
                rejected.append(slot_candidate)
            current_start += step

        ranked = sorted(accepted, key=lambda candidate: (-candidate.score, candidate.start))[: self.config.top_k]
        explanation = (
            f"Generated {len(accepted)} valid slots and ranked the top {len(ranked)} using working-hours, "
            "focus-block, and preference heuristics."
        )
        return SchedulingDecision(
            request_id=request.request_id,
            selected_slots=ranked,
            rejected_slots=rejected,
            explanation=explanation,
        )

    def _evaluate_slot(self, request: SchedulingRequest, slot: TimeRange, availability: list) -> CandidateSlot:
        score = 100.0
        reason_codes: list[str] = ["works_for_all_attendees"]

        notice_cutoff = datetime.now(tz=request.availability_window.start.tzinfo) + timedelta(
            minutes=request.preferences.minimum_notice_minutes
        )
        if slot.start < notice_cutoff:
            return CandidateSlot(start=slot.start, end=slot.end, score=-1, reason_codes=["insufficient_notice"])

        for window in availability:
            if not self._within_any(slot, window.working_hours):
                return CandidateSlot(start=slot.start, end=slot.end, score=-1, reason_codes=["outside_working_hours"])
            if self._overlaps_any(slot, window.busy):
                return CandidateSlot(start=slot.start, end=slot.end, score=-1, reason_codes=["conflicts_with_existing_event"])
            if self._overlaps_any(slot, window.focus_blocks):
                score -= 25
                reason_codes.append("overlaps_focus_block_penalty")

        if self._within_any(slot, request.preferences.preferred_time_ranges):
            score += 15
            reason_codes.append("preferred_time_window_bonus")
        elif request.preferences.preferred_time_ranges:
            score -= 10
            reason_codes.append("outside_preferred_window_penalty")

        if self._overlaps_any(slot, request.preferences.avoid_time_ranges):
            score -= 20
            reason_codes.append("avoid_window_penalty")

        return CandidateSlot(start=slot.start, end=slot.end, score=score, reason_codes=reason_codes)

    @staticmethod
    def _overlaps_any(candidate: TimeRange, ranges: list[TimeRange]) -> bool:
        return any(candidate.start < other.end and candidate.end > other.start for other in ranges)

    @staticmethod
    def _within_any(candidate: TimeRange, ranges: list[TimeRange]) -> bool:
        if not ranges:
            return True
        return any(candidate.start >= other.start and candidate.end <= other.end for other in ranges)
