# Design — Session History API & UI

## Context

Stage 5 (merged) implemented the engine layer of state history:

- `CoreActionExecutor` (`engine/core_actions.py`) executes `core/restore`, `core/fork`, `core/end-game`, `core/reset-game` — DB side effects coordinated, in-memory store updated via `set_state`/reducers. Exposed only as `StoryEngine.execute_core_action(db_session, action)` — **no callers**.
- `db/crud/message.py::find_previous_state` (0-based message-index steps, `-1` = latest, gap-tolerant) and `cleanup_state_history` (cap via `UserSettings.max_state_history`, default 50).
- `db/crud/session.py`: `create_fork_session` (copies state only, not messages; `title=None`, same project/config), `mark_session_ended`, `reset_session` (clears state **and** sets `ended_at=None`), `update_session_state`.
- `Session.ended_at` blocks further agent runs in `StoryEngine`.

Web layer today: `session_router` endpoints use annotated deps (`DbSessionDep`, `StoryEngineDep`); `StoryEngineDep` = `EngineManager.get_or_create(session_id, db_session, project_manager)`, which lazily creates an engine for idle/evicted sessions and loads the latest state from the DB (`session.state`, falling back to `get_latest_message_with_state`). The web `Session`/`SessionFull` schemas do **not** expose `ended_at`.

Frontend today: RTK Query `sessionApi` (`services/session.ts`) with tag-based invalidation; player view = `Player.tsx` + `PlayerToolbar.tsx` (Mantine `Toolbar`/`ToolbarGroup`); `SettingsForm.tsx` has per-control components (e.g. `ChatViewControl`); API types generated from OpenAPI.

Restores are **soft time-travel**: `_restore` sets the in-memory store state and `session.state` to the target snapshot but does **not** truncate later messages. New play after a restore appends new snapshots on top. This design inherits that behavior (it is the synced `state-history` contract) and makes the UI honest about it.

## Goals / Non-Goals

**Goals:**
- REST endpoints for all four core actions + a state-history listing, with clear success/error semantics, using the existing engine dependency (no EngineManager changes).
- Player-view UI: history menu, undo, fork (navigate to the new session), end-game (banner + trigger), reset (confirmation).
- Expose `ended_at` in the session API and `max_state_history` in the settings form.
- Full backend + frontend test coverage per repo conventions.

**Non-Goals:**
- `ActionDispatched` over WebSocket (separate `stream-action-dispatched` change). End-game awareness uses REST results + existing stream events.
- LLM-initiated core actions (tools/triggers dispatching `core/*`).
- Changing Stage-5 engine semantics (no message truncation on restore, no new DB schema).
- Redo (forward traversal) — restore to `-1`/latest is the only "forward" operation.

## Decisions

### D1: Core-action endpoints reuse `StoryEngineDep`; no `EngineManager` changes

`StoryEngineDep` already resolves a live engine for any existing session — creating one on demand and loading the latest state from the DB for idle/evicted sessions. Endpoints take `(engine: StoryEngineDep, db_session: DbSessionDep)` and call `engine.execute_core_action(db_session, action)`.

- *Alternative rejected: new `EngineManager` passthrough* — duplicates what the dep already does; the manager has no session-scoped action API and adding one for four endpoints is surface area for no benefit.
- *Alternative rejected: refactor `CoreActionExecutor` to run without a `StoryContext`* — the reset reducer and in-memory `set_state` need the store; a DB-only executor would desynchronize a live engine.
- Consequence: a core action on an idle session creates an engine (pool slot) — same as `read_session`/`create_model_request` today; idle eviction (600 s) applies. A session whose project no longer loads fails in engine creation (404 via the dep), consistent with existing behavior.

### D2: One endpoint per action, not a generic dispatcher

`POST /sessions/{id}/restore` (`{"step": int}`), `POST /sessions/{id}/fork` (`{"step": int}` → 201 + new `SessionFull`), `POST /sessions/{id}/end-game` (`{"reason": str | None}` optional body), `POST /sessions/{id}/reset` (no body), `GET /sessions/{id}/states`.

- *Alternative rejected: single `POST /core-actions` with a discriminated-union body* — worse OpenAPI docs, weaker typed clients, inconsistent with the router's resource style.

### D3: Step semantics inherited from Stage 5

`step` is a 0-based index into the session's message list; `-1` = latest. The web layer enforces the same bounds the engine does (`step >= -1`, `step <= message_count - 1`) so clients get a 422 with a clear detail instead of a mapped 409/500.

### D4: `GET /states` via a new CRUD helper, thin endpoint

New `db/crud/message.py::get_state_snapshots(db_session, session_id)` returning per snapshot: `step` (message index), `timestamp` (message `created_at`), `field_count` (size of the state dict — a cheap, project-agnostic preview). Endpoint maps to a `StateHistory` schema.

- *Alternative rejected: filter messages inline in the endpoint* — CRUD keeps the router thin and the query testable; avoids leaking ORM objects into the endpoint.
- v1 has no human-readable preview (e.g. "current node"); `field_count` is enough to disambiguate entries, richer previews can ride on top later.

### D5: Error mapping

| Engine error | HTTP | Rationale |
|---|---|---|
| Session not found (via `StoryEngineDep` `ValueError`) | 404 | existing dep behavior |
| `InvalidStepError` | 422 | client supplied an out-of-range step (pre-validated in D3; engine check is the backstop) |
| `NoStateError` (fork with no snapshot) | 409 | resource state conflict — nothing to fork from |
| `CoreActionError` | 409 | generic core-action failure (e.g. session vanished mid-flight) |

Mapping lives in a small helper in `session_router` (or a router-local exception handler) so every endpoint maps identically.

### D6: Session-lifecycle semantics (documented, not changed)

- **Restore/fork are allowed on ended sessions.** Fork is the recovery path for a premature end-game. The original stays ended (engine guard blocks new agent runs).
- **End-game is idempotent** on an already-ended session (existing executor behavior) → 200.
- **Reset un-ends**: `reset_session` sets `ended_at=None` (existing CRUD). Intended: reset = start over in the same session.
- Web `Session` schema gains `ended_at: datetime | None` (additive) so clients can render the ended state.

### D7: Frontend — RTK Query + Mantine, following existing patterns

- `sessionApi` gains endpoints: `restoreState`, `forkState` (201, invalidates `Session` list tags + provides the new session), `endGame`, `resetSession`, `getStates` (lazy query). Tags follow the existing `Session`/`SessionList` invalidation pattern.
- `PlayerToolbar` gains a **"Game"** `ToolbarGroup`: Undo button, "History" menu (snapshots from `getStates`, "Continue from step N — <timestamp>" entries), "Fork from here", "End game", "Reset" (Mantine confirm modal).
- Undo v1 = restore to the **second-newest snapshot** (immediately before the latest). History menu covers all snapshots; after a restore-and-continue flow the menu remains the source of truth. (See Open Q1.)
- Fork: on 201, navigate the player view to the new session (wouter route change).
- Ended state: `Player` shows an "ended" banner, disables the input area and request action when `session.ended_at` is set (data from `readSession`/`SessionFull`).
- `SettingsForm` gains a `max_state_history` control modeled on `ChatViewControl` (slider/number, default 50).
- API types: `pnpm generate-api-types` after the backend lands.

### D8: Tests

- Backend: endpoint tests for each action (success + 422/409/404 mapping), `get_state_snapshots` CRUD unit test, fork independence assertion, end-game idempotency, restore-then-read roundtrip. Use existing session/engine fixtures.
- Frontend: RTL tests for the Game toolbar group (undo/history/fork/end/reset flows) with mocked `sessionApi` hooks, and the ended-banner state, following existing component-test patterns.

## Risks / Trade-offs

- **[Engine created as side effect of core actions]** idle-session restore/fork materializes an engine → *mitigation*: identical to existing `read_session`/`create_model_request` behavior; idle eviction bounds the pool.
- **[Restore is not truncation — user expectation gap]** players may expect "undo" to erase the branch they're leaving; snapshots beyond the restore point remain in the message list. → *Mitigation*: UI wording ("Continue from step N"), history menu instead of an "Undo/Redo" pair; documented in D4/spec text.
- **[Undo after restore-then-continue is approximate]** the second-newest-snapshot rule drifts from "true" previous position once a restored timeline continues (old, superseded snapshots stay listed). → *Mitigation*: acceptable v1; Open Q1 tracks a restore-point marker if it proves confusing.
- **[Forked session has `title=None`]** appears as an untitled session in the list. → *Mitigation*: acceptable v1 (Open Q2); UI navigates directly to it on fork.
- **[Project deleted → core action 404s]** engine creation requires a loadable project. → *Mitigation*: consistent with `create_model_request`; error message is clear.
- **[Unbounded message growth]** state snapshots are capped by `max_state_history`, but messages are not (pre-existing). Out of scope; noted for a future change.
- **[Race: two concurrent core actions]** last commit wins. Single-user app; accepted, no locking.

## Migration Plan

- No DB migrations: `Session.state`, `Session.ended_at`, `Message.state` all exist since Stages 1/5.
- Backend + frontend ship together from this worktree (frontend depends on the new OpenAPI types). API is purely additive → an old frontend keeps working against the new backend.
- Rollback: revert the merge; no data was migrated or reshaped.

## Open Questions

1. **Restore-point tracking** — should `Session` gain a `restored_at_step` (or the UI persist "current position" client-side) so Undo/history can mark the active snapshot after a restore-then-continue flow? Deferred to v1.1 if user testing shows the current model is confusing.
2. **Fork titles** — server-side auto-title (`"Fork of <parent> @ step N"`) vs. client-side rename after 201? Leaning server-side, small CRUD change.
3. **Snapshot previews** — `field_count` only in v1; a project-aware preview (e.g. current graph node) would need access to the project definition in the endpoint.
