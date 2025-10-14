## Architecture

The system consists of several key components:

### 1. Story Engine ([`llm_gamebook/engine/engine.py`](llm_gamebook/engine/engine.py:29))
- Manages the narrative flow and LLM interactions
- Handles streaming responses
- Maintains conversation history and state
- Integrates with the TUI for user interaction

### 2. Entity System ([`llm_gamebook/story/`](llm_gamebook/story/))
- **Entity types**: Characters, locations, and other story elements with defined states
- **Traits**: Modular components that give entities specific behaviors
- **Conditions**: Triggers that determine when story transitions occur
- **Graph-based story structure**: Stories are represented as state machines with nodes and transitions

### 3. Schema Definition ([`llm_gamebook/schema/`](llm_gamebook/schema/))
- Stories are defined in YAML files with entity types, nodes, and transitions
- Uses Pydantic models for data validation
- Supports complex nested structures for character relationships

### 4. Terminal UI ([`llm_gamebook/tui/tui_app.py`](llm_gamebook/tui/tui_app.py:28))
- Built with Textual framework
- Provides real-time interaction with the story
- Shows thinking processes and generated responses
- Includes keyboard shortcuts for navigation
