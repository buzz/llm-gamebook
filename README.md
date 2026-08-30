# LLM Gamebook

An **interactive storytelling framework** using Large Language Models (LLMs) to generate dynamic narratives along predefined graph-based story paths.

## Architecture

Monorepo with FastAPI backend and React frontend:

```
llm-gamebook/
├── backend/           # Python FastAPI backend
│   ├── llm_gamebook/
│   │   ├── db/        # SQLModel database models and CRUD
│   │   ├── engine/    # StoryEngine, EngineManager, session runner
│   │   ├── message_bus/  # Async message bus for inter-component communication
│   │   ├── story/     # Story context, schemas, state management, traits
│   │   ├── web/       # FastAPI routes, WebSocket handlers, schemas
│   │   └── tui/       # Textual TUI (disabled)
│   └── tests/
└── frontend/          # React + TypeScript + Vite
    └── src/
        ├── components/
        ├── hooks/
        ├── routes/
        ├── services/  # RTK Query API clients
        └── store.ts   # Redux Toolkit store
```

## Core Components

- **StoryEngine**: Manages LLM agent interaction, message history, and response generation
- **EngineManager**: Pool of active StoryEngine instances with idle eviction
- **StoryContext**: Holds project definition, session state, and entity traits
- **MessageBus**: Async pub/sub for engine lifecycle and session events
- **ProjectManager**: Loads YAML story definitions from disk
- **SessionState**: Tracks entity positions, field values, and graph node transitions

## Story Definition

Stories are defined in YAML files with:
- **Entity types**: Graph-based story arcs, locations, characters
- **Entities**: Nodes with descriptions, edges, and conditional enablement
- **Traits**: Reusable mixins (described, graph, graph_node)
- **Functions**: Tool definitions exposed to the LLM for state transitions

See `examples/llm-gamebook/broken-bulb/llm-gamebook.yaml` for a complete example.

## Technology Stack

**Backend**
- FastAPI with async SQLModel (aiosqlite)
- Pydantic AI for LLM tool calling
- Jinja2 async templates for system prompts
- WebSockets for streaming responses

**Frontend**
- React 19 + TypeScript
- Redux Toolkit + RTK Query
- Mantine UI v8
- wouter for routing
- Vitest for testing

## Development

Start backend:
```bash
cd backend
uv run python -m llm_gamebook.main web --dev
```

Start frontend:
```bash
cd frontend
pnpm dev
```
