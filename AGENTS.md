# Repository Agent Notes

## Current Status
- Repository now contains the first three implementation slices for SchedulrAI: deterministic scheduling, safe mock execution, and a narrow typed intent-parsing service.
- Primary code artifacts added for the current scope:
  - `shared/schemas/scheduling.py` for shared scheduling, parsing, booking, execution, and audit contracts
  - `services/calendar/provider.py` for the provider interface and mock calendar implementation with create/update/cancel support
  - `services/scheduler/core.py` for deterministic candidate generation and ranking
  - `services/intent_parser/happy_path.py` for the narrow parser service, validated happy path, confidence scoring, and clarification handling
  - `services/execution/core.py` for dry-run previews, idempotent execution, and audit logging
  - `apps/cli/demo.py` for an end-to-end CLI demo that parses, ranks, previews, and books the top slot
- Supporting fixtures, evals, tests, and execution-board documentation now anchor Phase 1, Phase 2, and Phase 3 delivery milestones.
- The root `README.md` documents the repository purpose, current thin-slice scope, setup, demo flow, project layout, and supporting docs.

## Change Log
- 2026-03-19: Added `docs/implementation-roadmap.md`, a phase-by-phase implementation plan covering milestones, repo issue backlog, module boundaries, evaluation gates, and week-by-week deliverables.
- 2026-03-19: Added `docs/system-design.md`, a full system design document covering requirements, architecture, components, lifecycle flows, sequence diagrams, data model, APIs, deployment architecture, security, observability, risks, and future enhancements.
- 2026-03-19: Created this root `AGENTS.md` file to track repository state and provide context for future agents, per user instruction.
- 2026-03-19: Added `pyproject.toml` to establish the initial Python project scaffold and `pytest` support.
- 2026-03-19: Added shared scheduling/booking contracts in `shared/schemas/scheduling.py` and re-exported them via `shared/schemas/__init__.py`.
- 2026-03-19: Added `services/calendar/provider.py` with the `CalendarProvider` protocol and an idempotent `MockCalendarProvider` for fixture-backed availability and booking.
- 2026-03-19: Added `services/scheduler/core.py` with deterministic slot generation, hard-constraint filtering, soft scoring, and reason-code explanations.
- 2026-03-19: Added `services/intent_parser/happy_path.py` with a narrow regex-based parser for the first frozen scenario: “Schedule 30 minutes with Sarah next Tuesday afternoon.”
- 2026-03-19: Added `apps/cli/demo.py` for a demoable parse → schedule → book flow using the mock provider.
- 2026-03-19: Added fixture payloads under `tests/fixtures/`, unit tests under `tests/unit/`, scheduling evals under `evals/scheduling/`, and `docs/phase-1-execution-board.md` to freeze the first implementation milestone.
- 2026-03-20: Added `README.md` with a repository overview, current-scope summary, quick-start steps, architecture-oriented module guide, and links to the canonical planning/design docs.
- 2026-03-20: Expanded `shared/schemas/scheduling.py` and `shared/schemas/__init__.py` with Phase 2 execution contracts for booking updates, cancellations, statuses, and audit entries.
- 2026-03-20: Expanded `services/calendar/provider.py` so the mock provider supports idempotent create, update, and cancel flows in addition to free/busy reads.
- 2026-03-20: Added `services/execution/core.py` with the booking executor, deterministic idempotency-key helper, and in-memory audit log.
- 2026-03-20: Updated `apps/cli/demo.py` to emit a dry-run preview, execute the booking through the executor, and print audit-log output.
- 2026-03-20: Added `tests/unit/test_execution.py` to cover preview behavior, audited create/update/cancel flows, and retry-safe idempotent writes.
- 2026-03-20: Added `docs/phase-2-execution-board.md` and refreshed `README.md` to document the new safe-execution slice.
- 2026-03-20: Expanded `shared/schemas/scheduling.py` and `shared/schemas/__init__.py` with parser-result contracts for parsed, clarification-needed, and unsupported outcomes.
- 2026-03-20: Upgraded `services/intent_parser/happy_path.py` into a narrow parser service that adds confidence scores, clarification handling, and validated structured output while preserving the original happy path.
- 2026-03-20: Updated `apps/cli/demo.py` to emit parser-result metadata before continuing into scheduling and execution.
- 2026-03-20: Added parsing eval fixtures under `evals/parsing/`, parser regression tests in `tests/unit/test_intent_parser.py`, `docs/phase-3-execution-board.md`, and refreshed `README.md` to document the Phase 3 parser slice.

## Guidance for Future Agents
- Read this file before making changes.
- Keep this file updated whenever repository contents or project status changes.
- Treat `docs/system-design.md` as the canonical high-level architecture reference until implementation files are added.
- Treat `docs/implementation-roadmap.md` as the canonical execution plan for milestones, issue slicing, and weekly delivery sequencing.
- Treat `docs/phase-1-execution-board.md` as the canonical scope freeze for the initial deterministic scheduling slice.
- Treat `docs/phase-2-execution-board.md` as the canonical scope freeze for the safe mock execution slice.
- Treat `docs/phase-3-execution-board.md` as the canonical scope freeze for the parser-confidence and clarification slice.
- Prefer extending the shared contracts and fixtures before adding new integrations or orchestration layers.
- Keep the current slice narrow until the mocked demo path and tests remain stable.


## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.
### Available skills
- skill-creator: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. (file: /opt/codex/skills/.system/skill-creator/SKILL.md)
- skill-installer: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). (file: /opt/codex/skills/.system/skill-installer/SKILL.md)
### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) When `SKILL.md` references relative paths (e.g., `scripts/foo.py`), resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless you're blocked.
  - When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
