> **Ordering note:** Backend (1–4) must land before frontend (5–7) because frontend API types are generated from the running backend.

## 1. Backend: State Snapshot CRUD

- [ ] 1.1 Add `get_state_snapshots(db_session, session_id)` to `db/crud/message.py` returning snapshots in ascending order as `(step, created_at, field_count)` (step = 0-based message index, `field_count` = size of the state dict)
- [ ] 1.2 Unit test: snapshots ordered, gaps skipped, empty for stateless session

## 2. Backend: Web Schemas

- [ ] 2.1 Add `ended_at: datetime | None = None` to the web `Session` schema (`web/schemas/session/session.py`) so `Session`/`SessionFull` responses include `endedAt`
- [ ] 2.2 Add request/response schemas (camelCase via `CamelCasedBaseModel`): `StepRequest` (`step: int`, `ge=-1`), `EndGameRequest` (`reason: str | None = None`, body optional), `StateEntry` (`step`, `timestamp`, `field_count`), `StateHistory` (`data: list[StateEntry]`)

## 3. Backend: Core-Action Endpoints

- [ ] 3.1 Add router-local error mapping helper: `InvalidStepError` → 422, `NoStateError` → 409, `CoreActionError` → 409 (missing session already 404 via `StoryEngineDep`)
- [ ] 3.2 Add `POST /sessions/{session_id}/restore` — validate step bounds, execute via `engine.execute_core_action`, return 200
- [ ] 3.3 Add `POST /sessions/{session_id}/fork` — execute, return 201 with the new `SessionFull` (fetch the forked session after the call)
- [ ] 3.4 Add `POST /sessions/{session_id}/end-game` — optional `EndGameRequest` body, return 200
- [ ] 3.5 Add `POST /sessions/{session_id}/reset` — no body, return 200
- [ ] 3.6 Add `GET /sessions/{session_id}/states` — map `get_state_snapshots` to `StateHistory`

## 4. Backend Tests

- [ ] 4.1 Restore endpoint tests: specific step with gaps, `-1` latest, no snapshots → empty state, invalid step → 422, nonexistent session → 404, ended session restores but stays ended
- [ ] 4.2 Fork endpoint tests: 201 with new session (same project, target state, no messages), source unchanged, no state → 409, invalid step → 422
- [ ] 4.3 End-game endpoint tests: ends active session, idempotent on ended session, optional reason accepted
- [ ] 4.4 Reset endpoint tests: state cleared to defaults, message history preserved, ended session un-ended and playable
- [ ] 4.5 `GET /states` tests: ascending order with step/timestamp/field count, empty listing, 404
- [ ] 4.6 Session schema test: `endedAt` present (`null` active / timestamp ended)

## 5. Frontend: API Types and Service

- [ ] 5.1 Regenerate API types with the backend running (`pnpm generate-api-types`)
- [ ] 5.2 Extend `sessionApi` (`services/session.ts`): `restoreState`, `forkState`, `endGame`, `resetSession`, `getStates` (lazy query) with `Session`/list tag invalidation

## 6. Frontend: Player and Settings UI

- [ ] 6.1 Add "Game" `ToolbarGroup` to `PlayerToolbar` (or `Player`): Undo, History menu, Fork, End game, Reset (Mantine confirm modal) with the spec's disabled states (no snapshots → undo/history/fork disabled; ended → end game disabled)
- [ ] 6.2 Implement the state history menu: ascending snapshot list with step + timestamp, "continue from here" semantics, restore on selection and refresh the view
- [ ] 6.3 Implement Undo as restore to the second-newest snapshot
- [ ] 6.4 Implement fork: on 201 navigate the player view to the new session (wouter)
- [ ] 6.5 Implement ended display: banner + disabled input/send when `endedAt` is set
- [ ] 6.6 Add a `maxStateHistory` control to `SettingsForm` (default 50, persisted via the settings API), modeled on `ChatViewControl`

## 7. Frontend Tests

- [ ] 7.1 Game toolbar tests: controls render; disabled states (no snapshots, already ended); reset confirmation flow (confirm sends, cancel does not)
- [ ] 7.2 History menu tests: listing renders; selection sends restore and refreshes; undo targets second-newest snapshot; empty state indication
- [ ] 7.3 Fork test: success navigates to the new session
- [ ] 7.4 Ended display tests: banner + disabled input when `endedAt` set; nothing shown when active

## 8. Verification

- [ ] 8.1 `ruff check backend/`, `ruff format --check backend/`, `mypy backend/`
- [ ] 8.2 `pytest backend/` full suite green
- [ ] 8.3 `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`
- [ ] 8.4 Manual smoke (broken-bulb): play a few turns → undo → fork → play in the fork → end game in one session → reset in the other; verify history listing and cleanup limit (`maxStateHistory`) behavior
