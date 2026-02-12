## Why

When defining multiple story arc entities (e.g., Main, The Meeting) with transition capabilities, Pydantic AI throws a consistency error because it rejects multiple tools with the same name. The current architecture places the `functions` field at the `EntityTypeDefinition` level, meaning ALL entities of that type share the same function definitions. This prevents per-entity function definitions needed for independent story arc transitions.

## What Changes

- Move `functions` field from `EntityTypeDefinition` to `EntityDefinition` in the schema
- Update `GraphTrait.get_tools()` to access `self.functions` instead of `self.entity_type.functions`
- Update YAML configuration examples to use per-entity function definitions under `entities`
- Allow each story arc entity to define its own unique transition function

## Capabilities

### New Capabilities
- `entity-level-functions`: Allow entities to define their own Pydantic AI tool functions, enabling per-entity behavior and avoiding tool name collisions across entities of the same type

### Modified Capabilities
- None - this is an infrastructure change that enables the existing `story-arc` capability to work correctly with multiple story arc entities

## Impact

- **Schema**: `backend/llm_gamebook/schema/entity.py` - move `functions` from `EntityTypeDefinition` to `EntityDefinition`
- **Graph Trait**: `backend/llm_gamebook/story/traits/graph.py` - update `get_tools()` to access entity-level functions
- **Configuration**: YAML examples in `examples/broken-bulb/llm-gamebook.yaml` need to move `functions` from entity type to individual entities
- **Tests**: `backend/tests/broken_bulb/test_story_flow.py` - add third step testing story arc transition
