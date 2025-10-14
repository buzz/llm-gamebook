# LLM Gamebook Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the LLM Gamebook codebase, including its architecture, key components, real-world patterns, and areas for future consideration. It serves as a reference for AI agents and human developers working on enhancements to the system.

### Document Scope

This is a comprehensive documentation of the entire system, based on the provided codebase.

### Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| Oct 14, 2025 | 1.0 | Initial brownfield analysis | Winston |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

  * **Main Entry**: `llm_gamebook/main.py` (CLI application setup using Typer).
  * **Core Engine**: `llm_gamebook/engine/`
    * **Story Engine**: `llm_gamebook/engine/engine.py` (Contains the `StoryEngine` which manages the main game loop and LLM interface).
    * **Messages**: `llm_gamebook/engine/messages.py` (The `MessageList` class manages the current LLM context)
  * **State Management**: `llm_gamebook/story/`
    * **Story State**: `llm_gamebook/story/state.py` (The `StoryState` class, which holds the current narrative state).
    * **Story Project**: `llm_gamebook/story/project.py` (The `Project` class is the runtime representation of a gamebook project)
    * **Entity System**: `llm_gamebook/story/entity.py` and `llm_gamebook/story/traits/` (Defines the core entities and their extensible behaviors).
    * **Conditions**: `llm_gamebook/story/conditions/` (Custom grammar for conditions and evaluation logic)
    * **LLM Templates**: `llm_gamebook/story/templates/` (Jinja2 templates for LLM messages)
  * **Story Definition**: `llm_gamebook/schema/` (Pydantic models for validating story YAML files).
  * **Terminal UI**: `llm_gamebook/tui/tui_app.py` (The main Textual application class).

-----

## High Level Architecture

### Technical Summary

The `llm-gamebook` is a Python-based interactive storytelling framework. Its architecture is centered around a `StoryEngine` that orchestrates interactions between a Large Language Model (LLM), a predefined story structure, and a user interacting via a Terminal User Interface (TUI). The system uses a graph-based entity system where stories are defined in YAML files, parsed and validated by Pydantic models. The narrative flow is managed as a state machine, with the TUI providing a real-time, streaming view of the LLM's output.

A set of **Tools** is provided to the LLM, managed by `pydantic-ai`. These tools are dynamically generated from the entity definitions in the story YAML. For example, the `GraphTrait` creates a `transition` tool that the LLM can call to move the story to a new node in the graph. This is a powerful, flexible way to let the LLM interact with and change the game state.

### Actual Tech Stack (from pyproject.toml)

| Category | Technology | Version | Notes |
| :--- | :--- | :--- | :--- |
| Language | Python | \>=3.13 | |
| CLI Framework | Typer | \>=0.19.2 | Used for the main application entry point and command-line arguments. |
| TUI Framework | Textual | \>=6.3.0 | Powers the entire terminal user interface. |
| LLM Integration | pydantic-ai-slim | \>=1.0.18 | Manages LLM interactions, tool calling, and streaming. |
| Data Validation | Pydantic | \>=2.12.1 | Defines and validates the structure of story YAML files. |
| Templating | Jinja2 | \>=3.1.6 | Renders system and user prompts for the LLM. |
| Config Format | PyYAML | \>=6.0.3 | Used for defining story files. |

### Repository Structure Reality Check

  * **Type**: Monorepo
  * **Package Manager**: uv
  * **Notable**: The project is well-organized into distinct high-level packages (`engine`, `story`, `schema`, `tui`), clearly separating concerns.

-----

## Source Tree and Module Organization

### Project Structure (Actual)

```text
llm-gamebook/
├── docs/                  # Project documentation.
│   └── architecture.md
├── llm_gamebook/
│   ├── engine/            # Core story engine, manages game loop and LLM interaction.
│   ├── schema/            # Pydantic models for story file validation.
│   ├── story/             # Runtime representation of the story, entities, and state.
│   │   ├── conditions/    # Logic for evaluating boolean expressions.
│   │   ├── templates/     # Jinja2 templates for LLM prompts.
│   │   └── traits/        # Extensible behaviors for entities (e.g., described, graph).
│   └── tui/               # Textual-based Terminal User Interface components.
├── pyproject.toml         # Project dependencies and configuration.
└── README.md              # Project overview.
```

### Key Modules and Their Purpose

  * **`engine`**: The `StoryEngine` is the heart of the application. It runs an asynchronous loop that gets user input, queries the LLM via the `pydantic-ai` agent, handles streaming responses, and updates the TUI.
  * **`story`**: This package manages the runtime state of the narrative.
      * **`Project` & `StoryState`**: Loads and holds the entire story graph, including all entities and their current states.
      * **`EntityType` & `BaseEntity`**: Defines the classes for story elements like characters or locations.
      * **`traits`**: This is a key architectural pattern. Traits like `DescribedTrait` and `GraphTrait` are mixins that dynamically add fields (like `name`, `description`) and methods (like `transition`) to entities, making the system highly modular.
  * **`schema`**: This defines the "source of truth" for what a story looks like. It uses Pydantic models to enforce the structure of the YAML files that authors write, ensuring that any loaded story is valid.
  * **`tui`**: A sophisticated TUI built with Textual. It's fully asynchronous and event-driven. It's responsible for displaying the narrative, showing the LLM's "thinking" process in real-time, and capturing user input without blocking the application.

-----

## Data Models and APIs

### Data Models

The core data model is not a traditional database schema but is defined by the Pydantic models in the `llm_gamebook/schema/` directory. The top-level model is `ProjectDefinition`, which contains a list of `EntityTypeDefinition`. Each entity type defines its own entities, traits, and functions. This structure allows authors to define complex, graph-based narratives in a human-readable YAML file.

An important feature is the boolean expression parser (`llm_gamebook/story/conditions/`) which allows story files to define state transition conditions using a simple expression language (e.g., `player.has_key == true`).

### API Specifications

The project currently does not expose a traditional REST or GraphQL API. The TUI and the game engine are tightly coupled.

-----

## Technical Debt and Known Issues

### Critical Technical Debt

1.  **Limited State Management**: The current state is held in memory within the `StoryState` object. For more complex games, this could become unwieldy. A proper state management system that allows for serialization (saving/loading games) would be a significant improvement.
2.  **Hardcoded Prompt Templates**: The Jinja2 templates for system prompts are part of the application package. Allowing these to be customized within a project directory would increase flexibility.
3.  **Error Handling in TUI**: While the engine is robust, more specific error states and user feedback could be added to the TUI for cases where the LLM fails or a tool call returns an error.

### Workarounds and Gotchas

  * **LLM "Thinking" Tags**: The system relies on the LLM correctly wrapping its reasoning in `<think>`...`</think>` tags. The `_stream_printer` method in the engine is responsible for parsing this, but it's dependent on the LLM following instructions.
  * **Entity ID Uniqueness**: The application currently assumes that all entity IDs across all entity types are unique. A collision in IDs would lead to undefined behavior.

-----

## Integration Points and External Dependencies

### External Services

| Service | Purpose | Integration Type | Key Files |
| :--- | :--- | :--- | :--- |
| OpenAI (or compatible) | Narrative Generation | REST API | `llm_gamebook/main.py` (provider setup), `llm_gamebook/engine/engine.py` (agent runs) |

### Internal Integration Points

  * **Engine \<-\> TUI**: The `StoryEngine` and `TuiApp` are tightly coupled. The engine holds a reference to the TUI instance to push updates (`messages_update`, `stream_state_update`) and the TUI calls back to the engine to provide user input or trigger shutdown. This is managed through the `UserInterface` protocol.
  * **Engine \<-\> StoryState**: The engine uses `StoryState` to get the current system prompt, introduction message, and available tools for the LLM. When tools are called by the LLM, they modify the underlying entities within the `StoryState`.
  * **Story \<-\> Schema**: The `story` package's runtime objects are created directly from the definitions validated by the `schema` package. This ensures the runtime state is always consistent with the author's definition.

-----

## Development and Deployment

### Local Development Setup

1.  Requires Python 3.13+.
2.  Dependencies are installed via `pip` from `pyproject.toml`.
3.  An OpenAI-compatible API key and endpoint are required, which can be configured via environment variables (`OPENAI_API_KEY`, `BASE_URL`).
4.  The application is launched via `typer`, e.g., `python -m llm_gamebook.main tui ./path/to/project`.

### Build and Deployment Process

  * **Build Command**: Not applicable, as it's an interpreted Python project.
  * **Deployment**: The project is designed to be run locally as a standalone application. There is no formal deployment process. A `web` command for running a graphical web frontend is defined in `main.py` but is currently a `NotImplementedError`.

-----

## Testing Reality

### Current Test Coverage

The codebase does contain a number of tests under `tests/`. The test coverage is suboptimal. It currently has unit tests for loading the example project and the condition grammar. The primary method of testing is the manual execution of the TUI application.

### Running Tests

Test test suite can be executed using `uv run pytest`.
