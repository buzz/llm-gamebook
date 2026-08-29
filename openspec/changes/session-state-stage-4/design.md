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

### 6. Middleware model: onion chain

**Decision:** The Store middleware chain uses the onion model. Middleware signature is `(Store, Action, Next) -> SessionState`, where `Next` runs the remainder of the chain plus the reducers. Middleware may run code before `Next` (e.g., Logger, MessageBusPublisher) and/or after it (e.g., TriggerEval, AutoSave).

**Rationale:**
- Triggers must see the committed (post-reducer) state: "triggers see the final state of the step". A linear pre-reducer chain cannot run after the reducers.
- Onion model is the standard Redux pattern and correctly positions future middleware (MessageBusPublisher before reducers, AutoSave after).

**Alternatives considered:**
- Post-reducer hook list outside the middleware chain: would break the single-chain design (Logger, Bridge, Triggers, AutoSave) and require separate pre/post lists.

### 7. Loop prevention: cumulative action-type tracking + depth backstop

**Decision:** The Store tracks the action names dispatched in the current (possibly nested) dispatch chain (`Store.active_action_types`). Trigger evaluation skips trigger actions whose name is already in the chain. `MAX_DISPATCH_DEPTH` is raised from 2 to 10 as a recursion backstop, allowing trigger chains (A enables B) within one step.

**Rationale:**
- Per-round tracking alone would re-fire triggers skipped in an earlier round during nested dispatches.
- The depth limit alone (2) would raise on any trigger-of-trigger dispatch (depth 3), breaking chaining.
- With cumulative tracking, a dispatch chain can only dispatch each action type once via triggers, so the depth limit is a pure backstop.

### 8. Trigger condition validation at project level

**Decision:** Trigger condition syntax is validated by a `ProjectDefinition` model validator, not by a per-field validator on `TriggerDefinition`.

**Rationale:**
- Import cycle: `schemas/entity.py` cannot import the condition grammar at module level (`conditions/evaluator.py` imports `schemas/entity` for runtime `isinstance` checks). `ProjectDefinition` is the canonical load path and loads after the entity module.
- Evaluation time: invalid conditions also raise `ExpressionEvalError` defensively when a trigger is evaluated (e.g., triggers constructed programmatically).

### 9. Trigger action payloads

**Decision:** Trigger actions are dispatched with a `GenericPayload` (extra-fields-allowed payload) built from the trigger's `args` dict. Reducers re-validate the payload into their concrete payload model (existing pattern, e.g. `GraphTransitionPayload.model_validate(action.payload.model_dump())`).

**Rationale:**
- Triggers reference actions by name; a name-to-payload-model registry is extra indirection not needed while reducers already re-validate payloads.

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
  - Resolved (Stage 4): cumulative action-type tracking per dispatch chain + depth backstop (see Decision 7)
- Should triggers support "once only" semantics?
  - Defer to future if needed (triggers re-evaluate on every dispatch)
