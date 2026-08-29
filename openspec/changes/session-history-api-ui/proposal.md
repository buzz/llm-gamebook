# Session History API & UI

## Why

Stage 5 delivered a complete engine-level state-history feature set (restore, fork, end-game, reset, previous-state traversal, snapshot cleanup), but none of it is reachable: `StoryEngine.execute_core_action` has no callers, there are no REST endpoints, no surface to list a session's stored states, and the frontend has no undo/fork concept. Players currently cannot use any of the save-game/branching features the session-state design promises.

## What Changes

**Backend**

- New REST endpoints under `/sessions/{session_id}`:
  - `POST .../restore` — restore the session to the state at a given step (`{"step": n}`, `step: -1` = latest)
  - `POST .../fork` — branch a new independent session from the state at a given step; response carries the new session
  - `POST .../end-game` — mark the session as ended (optional reason payload)
  - `POST .../reset` — clear session state back to project defaults
  - `GET .../states` — list stored state snapshots (step number, timestamp, message reference) so clients can offer "go back to step N"
- `EngineManager` passthrough so the web layer can execute core actions against a session's engine (incl. behavior for idle/evicted sessions — see design)
- HTTP error mapping for the existing core-action error types (`InvalidStepError`, `NoStateError`, `CoreActionError`)
- New web schemas for the request/response payloads (incl. the state-history listing entry)

**Frontend** (built after the backend lands in the same worktree; API types regenerated via `pnpm generate-api-types`)

- Game (player) view: undo (restore to previous state), a history picker to restore to an earlier step, fork action (creates a session and navigates to it), end-game display (session locked/ended state), and reset with a confirmation dialog
- Settings: expose the existing `max_state_history` user setting (currently API-only) in the settings form

**Out of scope**

- Delivering `ActionDispatched` over WebSocket (tracked separately as `stream-action-dispatched`); end-game awareness in the UI comes from REST results and existing stream events, not new WS events
- LLM-initiated core actions (tools/triggers dispatching `core/*`) — engine-side only

No breaking changes: all API surface is additive; existing endpoints and the synced `state-history` engine requirements are untouched.

## Capabilities

### New Capabilities

- `session-history-ui`: Frontend capability covering state-history browsing, undo, restore-to-step, fork, and end-game/reset interactions in the player view and settings.

### Modified Capabilities

- `state-history`: Additive API-layer requirements — core actions (restore, fork, end-game, reset) exposed via REST with defined success/error semantics, and a state-history listing requirement. Engine-level behavior (existing 7 requirements) unchanged.

## Impact

- **Backend code**: `web/api/session_router.py` (new endpoints), `web/schemas/` (new session/history schemas), `engine/manager.py` (core-action execution path)
- **Backend tests**: endpoint tests (success + error mapping), engine-manager integration tests for core actions on idle sessions
- **Frontend code**: `frontend/src/components/page/player/` (controls/toolbar/history UI), `frontend/src/services/session.ts`, `frontend/src/components/page/SettingsForm.tsx`, generated API types
- **Frontend tests**: component tests for undo/fork/end-game/reset flows (Vitest + React Testing Library)
- **Docs**: brief note in `docs/session-state/steps-overview.md` once merged (stage table) — kept minimal, no design-doc changes
- **Dependencies**: none new; builds entirely on Stage 5 code already in main
