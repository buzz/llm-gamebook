# Visual Editor Architecture

## Overview

The LLM Gamebook visual editor provides a graphical interface for creating and editing interactive stories. It abstracts the declarative YAML structure into an intuitive visual experience while maintaining full parity with the underlying data model.

### Core Metaphor

The editor is built on OOP-like concepts adapted for non-programmers:

- **Entity Types** (Classes): Define the structure and capabilities of entities
- **Entities** (Objects): Concrete instances within a story
- **Traits** (Mixins): Modular capabilities that can be attached to entity types

### Design Principles

1. **Non-programmer friendly**: Visual metaphors, clear labels, no technical jargon
2. **Full parity**: Every visual action maps to the YAML definition
3. **Live state**: Editor reflects current story state; seamless switch to player
4. **Extensible**: Custom traits and Python integration for advanced users
5. **Preview-driven**: Always show how content appears to LLM and in runtime

---

## UI Layout

### Main Structure

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                [Editor ▼] │
├────────────────┬───────────────────────────┬──────────────────────────────┤
│                │                           │                              │
│   Left Panel   │   Main Panel              │   Right Panel                │
│   (Navigation) │   (Editor)                │   (Details/Preview)          │
│                │                           │                              │
│                │   - List/Table of item    │  Context-sensitive forms:    │
│                │   - Graph Editor          │  - Entity Type details       │
│                │   - ...                   │  - Entity details            │
│                │                           │  - Trait definition          │
│                │                           │  - Preview (LLM/State)       │
│                │                           │  - LLM-assisted editing      │
│                │                           │                              │
└────────────────┴───────────────────────────┴──────────────────────────────┘
```

### Navigation Tabs (editor)

| Tab | Purpose | Shows |
|-----|---------|-------|
| Entities | Manage entity types and entities | Top area: Table of entity types / Bottom area: All entities of the chosen type |
| Traits | Configure capabilities | Built-in (core), custom, and external (library) traits |

### Panel Behavior

- **Left Panel**: The global app navigation menu (the same for editor/player mode)
- **Main Panel**: The main editor view (shows dedicated editor views for entity, traits; traits may provide special editor views, e.g. graph editor)
  - Shows a table for entity editor (top: entity types, bottom: entities). Selection updates right panel.
  - GraphTrait: shows a node-based editor canvas
  - Other traits may show special edit UIs here...
- **Right Panel**: Context-sensitive based on selection and mode:
  - Default: Edit form for selected item
  - Preview modes:
    - LLM text (what the LLM "sees")
    - Current entity state
  - LLM-assisted editing (LLM conversation)

---

## Entity Editor

Shows a vertical split view
- Top: Entity type table
- Bottom: Entities

### List View (Main Panel)

Top pane displays all entity types with key information:

| Column | Description |
|--------|-------------|
| ID | PascalCase identifier |
| Name | Human-readable name |
| Traits | Badge list of attached traits |
| Entities | Count of instances |

Bottom pane shows all entities for the selected entity type:

| Column | Description |
|--------|-------------|
| ID | snake_case identifier |
| Type | Entity type (PascalCase) |
| Traits | Badge list of traits (inherited from type) |

### Filtering

Filter entities by:
- Entity type
- Trait presence
- Text search (matches ID or name from DescribedTrait)

### Entity Type Details View (Right Panel)

When an entity type is selected:

```
┌────────────────────────────────────────────────────────────┐
│ Entity Type: StoryScene                                    │
│ ─────────────────────────────────────────────────────────  │
│                                                            │
│  Basic Info                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ id:            [StoryScene                     ]    │   │
│  │ name:          [Story Scene                    ]    │   │
│  │ instructions:  [You are a story scene in a...  ]    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Traits                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [graph ✓] [described ✓]  [+ Add Trait]             │   │
│  │                                                     │   │
│  │ Graph Options                                       │   │
│  │ node_type_id: [GraphNode                       ▼]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Entities (3)                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [start    ] [middle  ] [end      ]  [+ New Entity]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Entity Details View (Right Panel)

When an entity is selected:

```
┌────────────────────────────────────────────────────────────┐
│ Entity: start                                              │
│ ─────────────────────────────────────────────────────────  │
│                                                            │
│  Basic Info                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ id:  [start                                      ]  │   │
│  │ type: [StoryScene                               ▼]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Trait Properties (from DescribedTrait)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ name:        [The Beginning                     ]   │   │
│  │ description: [You stand at the entrance of a... ]   │   │
│  │ enabled:     [✓ true                            ]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Trait Properties (from GraphNodeTrait)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ edges:  [middle                                  ]  │   │
│  │         [+ Add edge]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Functions (LLM-accessible)                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [transition(to: str)]  [Edit] [Delete]              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Trait Validation

When adding traits, the UI enforces constraints:
- If adding `graph` trait: requires a `node_type_id` (must reference existing entity type that has `graph_node` trait)
- If adding `graph_node` trait: warns if no `graph` trait exists in any entity type (required for the graph system to work)

---

## Trait Editor

### List View (Main Panel)

| Badge | Description |
|-------|-------------|
| graph | Graph navigation trait |
| described | LLM-facing description trait |
| custom_trait | User-defined trait |

#### Categories (small colored badges)

- **Global Traits** (built-in, read-only)
  - graph, described
- **External Traits** (imported from libraries, read-only)
- **Local Traits** (custom, editable)

### Add Custom Trait

Opens a dialog to create a new local trait:

```
┌─────────────────────────────────────────────────────────────┐
│  New Trait                                                  │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  id:     [my_custom_trait                                ]  │
│  name:   [My Custom Trait                                ]  │
│                                                             │
│  State Fields                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ + Add Field                                         │    │
│  │ field_name      field_type          required        │    │
│  │ ─────────────────────────────────────────────────── │    │
│  │ health          integer             ✓               │    │
│  │ inventory       list[string]         ☐              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Dynamic Fields (Expression)                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ + Add Field                                         │    │
│  │ field_name      expression              required    │    │
│  │ ─────────────────────────────────────────────────── │    │
│  │ is_alive        health > 0             ✓            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Triggers/Events                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ + Add Trigger                                       │    │
│  │ event           condition    action                 │    │
│  │ ─────────────────────────────────────────────────── │    │
│  │ on_enter        always       log("entered")         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Python Integration (Advanced)                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [ ] Link Python class                               │    │
│  │ module_path:  [mymodule.MyTrait                  ]  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│                                          [Cancel] [Create]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Details View

Shows trait definition with:
- All added fields, dynamic fields, triggers
- List of entity types using this trait
- Edit/Delete for local traits
- View Source for global traits (shows Python module path)

### Trait-specific Editor UI

Traits may have a custom editor view implementation:
- custom meta fields (e.g. node X/Y coordinates on the editor canvas)
- meta fields are attached to API endpoint types
- corresponding React component

---

## GraphTrait Canvas Editor

The Canvas Editor is a custom editor view implementation for the GraphTrait. It's so common that it's part of the core.

### Entering Graph Mode

When editing an entity that has the `graph` trait:
1. Select the entity in the Entity list
2. Click "Open Graph Editor" in the details panel
3. Canvas opens in the right panel (replaces form)

### Canvas Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  Graph Editor: StoryGraph                          [Zoom: 100%] [⚙]   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│       ┌────────┐                         ┌────────┐                    │
│       │ start  │───────────────────────▶│ middle │                    │
│       │  ●─────┤        "middle"         │  ●─────┼───────┐            │
│       └────────┘                         └────────┘       │            │
│                                                           │            │
│                                                           ▼            │
│                                                       ┌────────┐       │
│                                                       │  end   │       │
│                                                       │        │       │
│                                                       └────────┘       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Node Interaction

| Action | Behavior |
|--------|----------|
| Click node | Selects node |
| Double-click node | Opens full entity editor in modal |
| Drag node | Repositions node on canvas |
| Click + drag from node edge | Creates new connection |
| Right-click node | Context menu (delete, duplicate) |
| Select + Delete | Removes node from graph |

### Edge Interaction

| Action | Behavior |
|--------|----------|
| Click edge | Selects, shows connection details |
| Click edge + Delete | Removes connection |
| Drag edge endpoint | Re-routes connection |

### Toolbar

- **Zoom controls**: In/Out/Reset/Fit
- **Layout**: Auto-arrange nodes (hierarchical, force-directed)
- **Add node**: Opens entity creation dialog
- **Settings**: Canvas preferences (grid, snap)

### Implementation

Using `@xyflow/react` (or Rete.js) for the node-based editor:
- Each graph node is an entity from the `node_type_id` entity type
- Edges visualize the `edge_ids` relationships
- Dragging updates the entity positions (stored separately for layout)
- All changes sync back to entity data

---

## Preview Modes

### Preview Toggle

| Mode | Shows |
|------|-------|
| Editor | Standard edit form (default) |
| LLM | What the LLM sees (DescribedTrait content) |
| State | Runtime state of the entity |

### LLM Preview

Shows the content rendered from `DescribedTrait`:

```
┌────────────────────────────────────────────────────────────┐
│  LLM Preview: start                                        │
│  ────────────────────────────────────────────────────────  │
│                                                            │
│  The LLM sees this content when this entity is active:     │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  Name: The Beginning                                │   │
│  │                                                     │   │
│  │  Description:                                       │   │
│  │  You stand at the entrance of a dark cave.          │   │
│  │  The air is cool and damp. A faint light filters    │   │
│  │  from behind a bend in the passage ahead.           │   │
│  │                                                     │   │
│  │  Available actions:                                 │   │
│  │  - transition(to: "middle") → Go deeper into        │   │
│  │    the cave                                         │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### State Preview

Shows the current runtime state of the entity (useful during playback):

```
┌────────────────────────────────────────────────────────────┐
│  State Preview: start                                      │
│  ────────────────────────────────────────────────────────  │
│                                                            │
│  Current values:                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Property        Value              Type             │   │
│  │ ────────────────────────────────────────────────    │   │
│  │ id              "start"            string           │   │
│  │ name            "The Beginning"    string           │   │
│  │ description     "You stand..."     string           │   │
│  │ edges           ["middle"]         list             │   │
│  │ current_node_id "start"            string           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  Inherited from GraphTrait:                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ node_ids          ["start","middle","end"]  list    │   │
│  │ current_node_id   "start"                 string    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Expression Grammar

### Overview

The expression grammar defines simple conditions and dynamic fields using a custom syntax:

```python
# Examples
health > 0
"sword" in inventory
locations.cave.visited_count >= 3
```

### Editor Integration

Autocomplete is available in any field that accepts expressions:

---

## Custom Traits & Python Integration

### Trait Capabilities

Traits can be defined at two levels:

**Declarative Only**
- Add state fields (name, type, default)
- Define dynamic fields (computed from expressions)
- Add triggers/events (on_enter, on_exit, on_action)
- No Python code required

**Declarative + Python**
- Everything above, plus:
- Link a Python class for custom behavior
- Advanced state management
- Custom LLM tools/functions
- Event handlers with complex logic
- Custom editor view

### Linking Python Class

For advanced traits, users can link a Python class:

```
┌─────────────────────────────────────────────────────────────┐
│  Python Integration                                         │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  This trait uses a custom Python class:                     │
│                                                             │
│  Module: python/combat_trait.py                             │
│  Class:  CombatTrait                                        │
│                                                             │
│  [View Source]                                              │
│                                                             │
│  This enables:                                              │
│  • Custom state management                                  │
│  • Advanced LLM tools                                       │
│  • Event handlers                                           │
│  • Integration with external systems                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Trait Discovery

When creating a custom trait, the Python class is discovered from:
1. **Local project**: `python/` directory in the gamebook
2. **Imported libraries**: Traits from library dependencies
3. **Built-in**: Core traits like `graph`, `described`

---

## Editor-Player Integration

### Seamless Switching

At any time, users can switch between:
- **Editor Mode**: Modify story structure and content
- **Player Mode**: Play through the story

### Live State Sync

- When switching to player, current entity state is preserved
- Changes in player (transitions, state updates) reflect in editor
- Editor shows "live" indicator when connected to active session

### Snapshots

- Save current story state at any point
- Load previous snapshots
- Useful for:
  - Save games
  - Testing different paths
  - Recovering from errors

---

## LLM-assisted Editing / Introspection

- The system is introspective: all mutations and state of the gamebook are exposed through tool calls.
- An LLM conversation can be opened in the right sidebar to interactively edit and adapt the story.

Use cases:
- "Explain what is the difference between Entity types and entities."
- "Create a new entity XY."
- ...

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save changes |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Delete` | Delete selected |
| `Escape` | Close modal/deselect |
| `Ctrl+G` | Open graph editor (when entity with graph trait selected) |
| `Tab` | Navigate between panels |
| `?` | Show keyboard shortcuts |

---

## Implementation Notes

### Frontend Stack
- React with TypeScript
- Mantine v8 for UI components
- `@xyflow/react` for node-based graph editor
- Redux Toolkit for state management
- `wouter` for routing

### Data Flow
```
User Action → React Component → Redux Action → API Call → Backend
                     ↑                              │
                     └────────── Response ──────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `EditorLayout` | Main layout with tabs and panels |
| `EntityList` | Main panel for entity types and entities |
| `TraitList` | Main panel for traits |
| `EntityTypeDetails` | Right panel for entity type form |
| `EntityDetails` | Right panel for entity form |
| `TraitDetails` | Right panel for trait form |
| `GraphCanvas` | Node-based graph editor |
| `PreviewPanel` | LLM/State preview renderer |
| `ExpressionField` | Input with autocomplete |

### API Integration

The editor communicates with the backend via:
- REST API for CRUD operations
