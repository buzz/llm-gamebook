## Context

The current architecture places the `functions` field at the `EntityTypeDefinition` level (backend/llm_gamebook/schema/entity.py). This means all entities of a given type share the same function definitions. When multiple story arc entities (e.g., Main, The Meeting) define transition functions with the same name, Pydantic AI rejects them due to tool name uniqueness requirements.

The `GraphTrait` class (backend/llm_gamebook/story/traits/graph.py) accesses functions via `self.entity_type.functions` to generate tools. This works for single-entity types like `LocationGraph`, but breaks when multiple entities need independent transition functions.

## Goals / Non-Goals

**Goals:**
- Allow each entity to define its own Pydantic AI tool functions
- Enable multiple story arc entities to have transition functions without name collisions
- Maintain backward compatibility with existing single-entity configurations
- Provide per-entity function definitions in YAML configuration

**Non-Goals:**
- Change the GraphTrait's transition logic or behavior
- Modify how Pydantic AI tools are registered or called
- Alter the YAML schema structure beyond moving the `functions` field

## Decisions

### 1. Move `functions` from EntityTypeDefinition to EntityDefinition

**Decision**: Relocate the `functions` field from `EntityTypeDefinition` to `EntityDefinition` in the schema.

**Rationale**:
- Follows the existing pattern where entity-specific data lives with entities
- Allows per-entity function definitions without collisions
- Aligns with how `current_node_id` and `node_ids` are already entity-specific

**Alternative Considered**: Keep `functions` at entity type level but allow per-entity overrides. Rejected because it adds complexity and doesn't solve the core issue of shared tool names.

### 2. Update GraphTrait.get_tools() to access entity-level functions

**Decision**: Modify `GraphTrait.get_tools()` to use `self.functions` (inherited from BaseEntity) instead of `self.entity_type.functions`.

**Rationale**:
- Maintains the same tool generation logic
- Each entity instance gets its own tools
- Simple change with minimal risk

**Alternative Considered**: Create a separate method for entity-level tools. Rejected because it duplicates existing infrastructure.

### 3. Update YAML configuration examples

**Decision**: Move `functions` from under entity types (like `LocationGraph`) to individual entities (like `locations`).

**Rationale**:
- Demonstrates the new capability in examples
- Provides clear migration guidance for users
- Shows the correct pattern for multi-entity story arcs

### 4. No backward compatibility layer

**Decision**: Remove `functions` from `EntityTypeDefinition` entirely rather than supporting both locations.

**Rationale**:
- Simpler code without conditional logic
- Forces consistent configuration
- YAML examples will be updated to the new structure

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing YAML configs break | High - backward incompatible | Update all examples, document migration path |
| Tool name collisions still possible | Medium - if entities use same function names | Document that function names must be unique per entity |
| Testing gaps | Medium - new patterns need coverage | Add test case for story arc transition |

## Migration Plan

1. **Schema change**: Move `functions` field in entity.py
2. **Update GraphTrait**: Change `self.entity_type.functions` to `self.functions`
3. **Update YAML examples**: Move `functions` from entity types to entities
4. **Add test case**: Extend `test_story_flow` with third step
5. **Run linters and tests**: Verify no regressions

## Open Questions

1. Should function names be auto-generated to avoid collisions (e.g., `main_transition`, `the_meeting_transition`)?

Currently the design expects users to provide unique names. Auto-generation could be added later if needed.
