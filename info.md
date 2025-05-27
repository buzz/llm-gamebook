# LLM Gamebook

> LLM narration along pre-defined storyline paths

## Ideas

- Storyline graph as state machine (transitions tied to Conditions)
- Use retrieval-augmented generation (RAG) to ground the LLM in predefined story elements (e.g., NPC backstories)
- Scalability
  - Modularize gamebooks into reusable components (e.g., "combat system," "dialogue templates").

## Entity system

- Storyline graph
  - starting points
  - intermediate goals/checkpoints
  - negative endings (e.g. character death, some other final failure)
  - positive endings (e.g. win)
- Conditions
  - e.g. found the golden chalice
  - Location flags (Castle visited)
- Locations
- NPCs
- Players stats
- Player inventory

## Implementation

Author defines nodes, conditions, and entities in a JSON/YAML file.

### Graph-based node editor

- Graph library
  - https://github.com/jagenjo/litegraph.js (used by ComfyUI)
  - https://js.cytoscape.org/
  - https://visjs.org/
