## Context

With Stages 1-3 implemented (session state, action system, action-driven state), Stage 4 implements the trigger system. Triggers allow automatic action dispatch based on conditions evaluated against the current state. For example: "if player.has_visited('village'), transition to unlock_ending".

Triggers are defined in YAML on entity types, evaluated after each agent step via middleware.

## Goals / Non-Goals

**Goals:**
- Add trigger definitions to entity type schema (name, condition, args)
- Parse triggers from YAML when loading project
- Load triggers into EntityType at build time
- Implement TriggerEval middleware (replace stub from Stage 2)
- Evaluate all triggers after each agent step
- Dispatch trigger actions when conditions are true
- Integrate BoolExprEvaluator with effective field values (session + project)
- Handle dynamic field references in conditions

**Non-Goals:**
- History/undo (Stage 5)
- Complex trigger expressions beyond BoolExpr grammar
- Trigger lifecycle management (edit/delete at runtime)

## Decisions

### 1. Trigger storage: EntityType-level

**Decision:** Triggers are defined on entity types, stored in EntityType at runtime.

**Rationale:**
- Triggers are part of entity behavior, natural fit with entity type
- Loaded once at project load, evaluated each step
- Matches architecture: triggers defined in YAML on entities

**Alternatives considered:**
- Separate TriggerRegistry: Extra layer of indirection, not needed

### 2. Trigger schema: name, condition, args

**Decision:** Trigger definition includes:
- `name`: action type (e.g., `graph/transition`)
- `condition`: boolean expression (e.g., `=player.has_visited('village')`)
- `args`: dict of action payload values

**Rationale:**
- Follows architecture example exactly
- Separates condition from action (composable)
- Args allow parameterized actions

### 3. Trigger evaluation: After state changes committed

**Decision:** Triggers evaluate after all user actions have been processed and state is committed.

**Rationale:**
- Triggers should see final state of the step
- Prevents triggers firing on intermediate states
- Order: user actions → state changes → trigger evaluation

**Alternatives considered:**
- Evaluate before user actions: Would miss changes from current step
- Evaluate during: Complex to track intermediate states

### 4. BoolExprEvaluator uses effective fields

**Decision:** Trigger conditions evaluate against effective field values (session state overrides + project defaults).

**Rationale:**
- Consistent with how other code reads fields
- Session state may have overrides that affect conditions
- Example: `=player.current_node_id == 'village'` should check session value

### 5. Multiple triggers can fire

**Decision:** All triggers with true conditions fire in order defined in YAML.

**Rationale:**
- Multiple things can happen in one step
- Order is deterministic (YAML order)
- Allows chaining: trigger A enables trigger B in same step

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Infinite trigger loops | Prevent triggers dispatching same action type; max recursion depth |
| Performance with many triggers | Triggers are cheap (condition eval + optional dispatch); profile if needed |
| Invalid condition syntax | BoolExprEvaluator raises on parse/eval error |
| Triggers firing too often | Add cooldown/once-per-session options if needed |

## Migration Plan

1. **Schema update**: Add `TriggerDefinition` to entity type schema
2. **EntityType update**: Add `triggers: list[Trigger]` attribute
3. **Parse triggers**: Load from YAML in project builder
4. **TriggerEval middleware**: Implement evaluate-and-dispatch logic
5. **BoolExpr integration**: Pass effective fields to evaluator
6. **Tests**: Unit tests for trigger firing, conditions, middleware

## Open Questions

- Should triggers be entity-scoped or global?
  - Current: defined on entity types, can reference any entity
- How to prevent trigger loops?
  - Track action types dispatched by triggers, prevent re-dispatch
- Should triggers support "once only" semantics?
  - Defer to future if needed
