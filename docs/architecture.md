# LLM Gamebook Architecture Document

## Introduction

This document captures the CURRENT STATE of the LLM Gamebook codebase, including its architecture, key components, and real-world patterns. It serves as a reference for AI agents and human developers working on enhancements to the system.

> **Design authority for session state:** The target design for session state, actions, triggers, and history lives in
> [`docs/session-state/architecture.md`](session-state/architecture.md). That document is the **authoritative design going forward**;
> this document describes what is actually implemented today.
> [`docs/session-state/steps-overview.md`](session-state/steps-overview.md) maps that design to implementation stages and the
> corresponding OpenSpec changes (see `openspec/changes/`).

### Document Scope

Comprehensive documentation of the entire system, based on the current codebase.

### Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| Oct 14, 2025 | 1.0 | Initial brownfield analysis | Winston |
| Aug 29, 2026 | 2.0 | Rewritten after monorepo split: FastAPI backend, React frontend, SQLModel persistence, engine manager, web API | — |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

* **Main Entry**: `backend/llm_gamebook/main.py` (Typer CLI; `web` command runs the FastAPI app via uvicorn, `tui` command is currently disabled).
* **Web Layer**: `backend/llm_gamebook/web/`
    * **App**: `web/app.py` (`create_app`; lifespan wires up DB engine, `MessageBus`, `EngineManager`, `ProjectManager`).
    * **REST API**: `web/api/` (routers for projects, sessions, model configs, user settings, mounted under `/api`).
    * **WebSocket**: `web/websocket/` (`WebSocketHandler` streams engine events to the frontend, mounted under `/ws`).
    * **API Schemas**: `web/schemas/` (Pydantic request/response models, incl. WebSocket message types).
* **Database**: `backend/llm_gamebook/db/`
    * **Models**: `db/models/` (SQLModel tables: `Session`, `Message` (incl. `state` JSON field), `Part`, `ModelConfig`, `Usage`, `UserSettings`).
    * **CRUD**: `db/crud/` (async CRUD functions per model).
    * **Engine**: `db/db_engine.py` (`create_async_db_engine`, aiosqlite-backed).
* **Core Engine**: `backend/llm_gamebook/engine/`
    * **Story Engine**: `engine/engine.py` (`StoryEngine` runs the pydantic-ai agent, streaming responses to the message bus).
    * **Engine Manager**: `engine/manager.py` (`EngineManager` pools active engines per session with idle eviction).
    * **Session Adapter**: `engine/session_adapter.py` (DB access: message history, state load/save, user requests).
    * **Streaming**: `engine/_runner.py` (`StreamRunner` / `_ModelRequestHandler` publish debounced stream deltas).
    * **Bus Messages**: `engine/message.py` (engine lifecycle and stream events).
* **State Management**: `backend/llm_gamebook/story/`
    * **Context**: `story/context.py` (`StoryContext` combines project definition + `SessionState` + `Store`, exposes tools and prompts).
    * **Project**: `story/project_manager.py` (loads and validates YAML story definitions from disk).
    * **Entity System**: `story/traits/` (`DescribedTrait`, `GraphTrait`, `GraphNodeTrait`) and `story/types.py`.
    * **Conditions**: `story/conditions/` (Boolean expression grammar, pyparsing-based, with dot-path resolution).
    * **Session State**: `story/state/` (`SessionState`, `Store`, `Action`, middleware chain — see below).
    * **LLM Templates**: `story/templates/` (Jinja2 templates for system prompt, intro message, and trait fragments).
    * **Story Schemas**: `story/schemas/` (Pydantic models for validating story YAML files).
* **Message Bus**: `backend/llm_gamebook/message_bus/` (`MessageBus` pub/sub, `BusSubscriber` base class).
* **Terminal UI**: `backend/llm_gamebook/tui/` (Textual app; **currently disabled** — the web frontend is the primary UI).
* **Frontend**: `frontend/src/` (React 19 + TypeScript + Vite; Mantine v8 UI, Redux Toolkit + RTK Query services, wouter routing, WebSocket client, `streamdown` markdown rendering).

-----

## High Level Architecture

### Technical Summary

`llm-gamebook` is a Python/TypeScript interactive storytelling framework. The backend is a FastAPI application that exposes a REST API and a WebSocket endpoint; the frontend is a React SPA. Storytelling is driven by a `StoryEngine` that orchestrates a pydantic-ai `Agent` between a user, a predefined story structure (YAML), and the LLM.

Key runtime pieces:

- **`EngineManager`** keeps one `StoryEngine` per active session (lazy creation, idle eviction) and reacts to bus events (session deletion, model config changes).
- **`StoryEngine`** runs the agent loop: it builds the system prompt and tools from the `StoryContext`, streams model output as `StreamPart*` messages onto the **`MessageBus`**, and persists user/model messages (and session state) via the **`SessionAdapter`** into the SQLite database.
- **`WebSocketHandler`** subscribes to the bus and forwards stream/response events to the connected frontend, which renders them live.
- A set of **Tools** is provided to the LLM, generated from the story YAML (entity functions). Tools dispatch **actions** through the session **`Store`** (Redux-inspired: action → middleware → reducer → new state), so state changes are the only way story state mutates. See [`docs/session-state/architecture.md`](session-state/architecture.md) for the full design.

### Actual Tech Stack

Backend (`backend/pyproject.toml`, Python >= 3.13, managed with **uv**):

| Category | Technology | Version | Notes |
| :--- | :--- | :--- | :--- |
| Language | Python | >=3.13 | |
| Web Framework | FastAPI | >=0.128.1 | REST API + WebSocket, OpenAPI schema. |
| CLI Framework | Typer | >=0.21.1 | Application entry point (`web` command). |
| LLM Integration | pydantic-ai-slim | >=1.54.0 | Agent, tool calling, streaming (anthropic/openai/google/mistral/xai providers). |
| Data Validation | Pydantic | >=2.12.5 | Story YAML validation, API schemas, actions/payloads. |
| ORM / DB | SQLModel + aiosqlite | >=0.0.32 / >=0.22.1 | Async SQLite persistence, JSON columns for state. |
| Templating | Jinja2 | >=3.1.6 | System prompt / intro message templates. |
| Config Format | PyYAML | >=6.0.3 | Story project files. |
| Expression Parsing | pyparsing | >=3.3.2 | Condition/condition-expression grammar. |
| TUI Framework | Textual | >=7.5.0 | Terminal UI, currently disabled. |
| Data Locations | platformdirs | >=4.5.1 | User data dir (database, projects). |

Frontend (`frontend/package.json`, managed with **pnpm**):

| Category | Technology | Version | Notes |
| :--- | :--- | :--- | :--- |
| Language | TypeScript (strict) | ~5.9 | |
| UI Library | React | ^19.2.4 | |
| Build Tool | Vite | ^7.x | Dev server + production build. |
| Component Library | Mantine | ^8.3.14 | UI components, form, notifications, modals. |
| State Management | Redux Toolkit + RTK Query | ^2.11.2 | Global store; RTK Query for API clients. |
| Routing | wouter | ^3.9.0 | Lightweight router with type-safe routes. |
| WebSocket | react-use-websocket | ^4.13.0 | Live streaming of engine events. |
| Markdown | streamdown | ^2.3.0 | Streaming markdown rendering. |
| Testing | Vitest + Testing Library | ^4.0.1 | Component and unit tests. |

### Repository Structure

* **Type**: Monorepo (`backend/` + `frontend/`)
* **Package Managers**: uv (Python), pnpm (Node.js)
* **Notable**: The backend package is well organized into distinct high-level modules (`web`, `db`, `engine`, `story`, `message_bus`, `tui`), separating transport, persistence, LLM orchestration, and domain logic.

-----

## Source Tree and Module Organization

### Project Structure (Actual)

```text
llm-gamebook/
├── backend/
│   ├── llm_gamebook/
│   │   ├── main.py          # Typer CLI entry point (web / tui commands).
│   │   ├── constants.py     # Project name, user-data and project paths.
│   │   ├── providers.py     # LLM provider/model configuration.
│   │   ├── web/             # FastAPI app, REST API, WebSocket, API schemas.
│   │   │   ├── api/         #   REST routers: project, session, model_config, settings.
│   │   │   ├── websocket/   #   WebSocket router and event-forwarding handler.
│   │   │   └── schemas/     #   Pydantic API + WebSocket message models.
│   │   ├── db/              # SQLModel persistence layer.
│   │   │   ├── models/      #   Session, Message, Part, ModelConfig, Usage, UserSettings.
│   │   │   └── crud/        #   Async CRUD functions per model.
│   │   ├── engine/          # StoryEngine, EngineManager, streaming, session adapter.
│   │   ├── message_bus/     # Async pub/sub message bus + subscriber base class.
│   │   ├── story/           # Domain: project loading, context, state, traits, schemas.
│   │   │   ├── state/       #   SessionState, Store, Actions, middleware chain.
│   │   │   ├── traits/      #   DescribedTrait, GraphTrait, GraphNodeTrait.
│   │   │   ├── conditions/  #   Boolean expression grammar + evaluator.
│   │   │   ├── schemas/     #   Pydantic models for story YAML.
│   │   │   └── templates/   #   Jinja2 LLM prompt templates.
│   │   └── tui/             # Textual TUI (disabled).
│   └── tests/               # Python tests, mirroring the package tree.
├── frontend/
│   └── src/
│       ├── components/      # UI components (page / app / common).
│       ├── routes/          # wouter route definitions (type-safe).
│       ├── services/        # RTK Query API clients (project, session, model-config, settings).
│       ├── store.ts         # Redux Toolkit store.
│       ├── types/           # Types, incl. generated OpenAPI types.
│       └── hooks/           # Shared React hooks.
├── docs/                    # Project documentation.
├── examples/                # Example story projects (e.g., broken-bulb).
├── openspec/                # OpenSpec specs and changes.
├── AGENTS.md                # Agent guidelines.
└── README.md                # Project overview.
```

### Key Modules and Their Purpose

* **`web`**: The transport layer. `create_app` wires lifespan dependencies (DB engine, `MessageBus`, `EngineManager`, `ProjectManager`). The REST API under `/api` handles projects, sessions, model configs, and user settings. The WebSocket endpoint under `/ws` bridges the message bus to the browser (introduction message, response lifecycle, debounced stream deltas).
* **`db`**: Async SQLModel persistence. `Message` rows store a `state` JSON blob (session state snapshot when a change occurred), enabling history/undo per the session-state design.
* **`engine`**: `StoryEngine` is the heart of the application. It runs the pydantic-ai agent against the current session, streams model responses (text, thinking, tool calls) as bus messages, and persists everything via `SessionAdapter`. `EngineManager` owns the engine lifecycle: lazy creation from project + model config, idle eviction, teardown on session deletion.
* **`story`**: Domain logic.
    * **`ProjectManager` & schemas**: Loads and validates the YAML project definition ("source of truth" for the static story structure).
    * **`StoryContext`**: Per-session runtime view: project definition + `SessionState` + `Store`. Provides effective field values (state overrides over defaults), tools for the LLM, and rendered prompts.
    * **Traits**: Reusable mixins (`DescribedTrait`, `GraphTrait`, `GraphNodeTrait`) that add fields and LLM tools to entities. `GraphTrait` exposes a `transition` tool which dispatches a `graph/transition` action rather than mutating state directly.
    * **`state`**: The Redux-inspired action system: `Store.dispatch(action)` runs the middleware chain (logging, message-bus publisher, trigger evaluation, auto-save — the latter three are stubs), then composed reducers produce the new `SessionState`.
    * **`conditions`**: Boolean expression grammar (pyparsing) with dot-path resolution into entity fields.
* **`message_bus`**: Application-wide async pub/sub. Engine events, session lifecycle events, and (planned) action-bridged events flow through it; `WebSocketHandler` and `EngineManager` are subscribers.
* **`tui`**: Textual-based terminal UI. Present in the codebase but disabled; the web frontend is the primary interface.
* **`frontend`**: React SPA. Redux Toolkit store with RTK Query API services (typed from the backend OpenAPI schema), wouter routes (project list/details/form, player, editor, model config, settings), and a WebSocket connection that live-renders streamed model output.

-----

## Data Models and APIs

### Database Models (SQLModel)

* **`Session`**: A conversation/game session tied to a project.
* **`Message`**: One user/model message in a session; model messages may carry a `state` JSON snapshot (session state after that step).
* **`Part`**: Fine-grained message content (`user-prompt`, `text`, `thinking`, `tool-call`, `tool-return`, `retry-prompt`).
* **`ModelConfig`**: LLM provider/model configurations available for sessions.
* **`Usage`**: Token usage accounting.
* **`UserSettings`**: Per-user UI preferences.

### Story Definition Schemas (Pydantic)

The static project definition is validated by the Pydantic models in `story/schemas/`: a project contains entity type definitions; each entity type defines entities, traits, and functions (LLM tool mappings). The boolean expression parser (`story/conditions/`) allows conditions using a simple expression language with dot-path resolution.

### Session State (implemented subset)

`SessionState` is a dict of entity field overrides over project defaults, held in `StoryContext` and owned by the `Store`. Actions (`Action` subclasses with namespaced `namespace/action` names) are the only way to change state; reducers (registered by traits, e.g. `GraphTrait.graph_transition_reducer`) are pure `(state, action) → state` functions. State is serialized as JSON onto `Message` rows after agent steps.

The full design — dynamic `=expression` fields, triggers, history/undo, state migration, and the message bus bridge — is specified in [`docs/session-state/architecture.md`](session-state/architecture.md). See "Technical Debt" for what is still a stub.

### API

* **REST** (`/api`): Projects (CRUD/discovery), sessions (CRUD + messages), model configs (CRUD), user settings. OpenAPI schema at `/openapi.json`; the frontend generates its API types from it (`pnpm generate-api-types`).
* **WebSocket** (`/ws`): One connection per session. The server sends introduction data and, per response, lifecycle events and debounced stream part deltas (text/thinking/tool-call parts); the client sends user requests.

-----

## Technical Debt and Known Issues

### In-Flight / Stubs (see `docs/session-state/steps-overview.md` and `openspec/changes/`)

1. **Trigger system (Stage 4)**: `trigger_eval_middleware` is a stub; condition-based action dispatch after agent steps is not implemented yet (OpenSpec change `session-state-stage-4` in progress).
2. **History and undo (Stage 5)**: State snapshots are stored on messages, but traversal/restore/fork and `core/reset-game` are not implemented yet (OpenSpec change `session-state-stage-5` in progress). `core/end-game` exists as an action.
3. **Message bus bridge (Stage 6)**: `message_bus_publisher_middleware` is a stub; `ActionDispatched` messages are not yet published.
4. **Auto-save middleware**: Stub (persistence currently happens around agent steps via the engine, not per-action).

### Other Known Issues

* **TUI disabled**: The Textual TUI and the `tui` CLI command are commented out; only the web app is supported.
* **Hardcoded prompt templates**: Jinja2 templates for system prompts ship inside the application package. Allowing per-project customization would increase flexibility.
* **Entity ID Uniqueness**: The application assumes entity IDs are unique across all entity types; a collision leads to undefined behavior.
* **State migration**: The session-state design specifies migration when the project definition changes (new fields get defaults, removed fields dropped, type changes cast); this is not implemented yet.

-----

## Integration Points and External Dependencies

### External Services

| Service | Purpose | Integration Type | Key Files |
| :--- | :--- | :--- | :--- |
| OpenAI (or compatible: Anthropic, Google, Mistral, xAI) | Narrative Generation | REST API | `llm_gamebook/providers.py`, `llm_gamebook/engine/_model_factory.py` |

### Internal Integration Points

* **Frontend <-> Web API**: RTK Query services call the REST API; the WebSocket handler pushes live stream events to the SPA.
* **Web <-> EngineManager**: The WebSocket handler requests engines via `EngineManager.get_or_create` (lazy engine initialization) and forwards user input to `StoryEngine.generate_response`.
* **Engine <-> MessageBus**: The engine publishes lifecycle and stream events; `EngineManager` and `WebSocketHandler` subscribe. The message bus is the decoupling point between engine and transport.
* **Engine <-> DB**: `SessionAdapter` persists user/model messages and session state, and reconstructs agent history on engine (re)creation.
* **Story <-> State**: LLM tools dispatch actions through the `Store`; reducers update `SessionState`; `StoryContext` exposes effective values (defaults + overrides) to prompts, tools, and conditions.
* **Story <-> Schemas**: Runtime objects (project, entity types, traits) are built from the YAML definitions validated by `story/schemas`.

-----

## Development and Deployment

### Local Development Setup

Backend (requires Python 3.13+, uv):

1. `cd backend && uv sync`
2. `uv run llm-gamebook web --dev` (FastAPI on `127.0.0.1:8000`, auto-reload; `--dev` is resource-intensive)
3. Configure model providers via the web UI (model configs) or environment variables.

Frontend (requires Node.js, pnpm):

1. `cd frontend && pnpm install`
2. `pnpm dev` (Vite dev server)

The user database and project storage live in the platform user-data directory (see `constants.py`); example projects are under `examples/`.

### Build and Deployment Process

* **Backend**: Python package (`uv build`); run via the `llm-gamebook` CLI (`web` command). No formal deployment process; designed to run locally.
* **Frontend**: `pnpm build` produces a static Vite build (`frontend/dist`).
* **OpenAPI types**: After backend API changes, regenerate frontend types with `pnpm generate-api-types` (requires the backend running at `localhost:8000`).

-----

## Testing Reality

### Current Test Coverage

Python tests live under `backend/tests/`, mirroring the package tree (`tests/llm_gamebook/...`), plus integration scenarios under `backend/tests/broken_bulb/` (mock player + mock model exercising the full story flow). Coverage includes the web API routers and WebSocket handler, engine manager/adapter/runner, DB layer, condition grammar, and API schemas. An architecture test (`tests/test_architecture.py`) enforces module boundaries. The frontend has Vitest + React Testing Library tests under `frontend/src/`.

### Running Tests

* Backend: `pytest backend/` (pytest-asyncio auto mode)
* Frontend: `pnpm test`
