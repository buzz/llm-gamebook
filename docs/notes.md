# LLM Gamebook

LLM narration along pre-defined story arc paths

## Ideas

- story arc graph as state machine (transitions tied to Conditions)
- Use retrieval-augmented generation (RAG) to ground the LLM in predefined story elements (e.g., NPC backstories)
- Scalability
  - Modularize gamebooks into reusable components (e.g., "combat system," "dialogue templates").

## Entity system

- story arc graph
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
- Variable time
  - Slow down/speed up time according to current narration
    - e.g. travelling may take months (one reply should describe a couple of days, maybe weeks)
    - e.g. a fight in the street (one reply should only span a few seconds)
  - keep track of time and date in global state

## Implementation

Author defines nodes, conditions, and entities in a JSON/YAML file.

### Graph-based node editor

- Graph library
  - https://github.com/retejs/rete
  - https://github.com/jagenjo/litegraph.js (used by ComfyUI)
  - https://js.cytoscape.org/
  - https://visjs.org/

## Interesting stuff/prior work

- https://chasm.run/
- https://github.com/neph1/LlamaTale
