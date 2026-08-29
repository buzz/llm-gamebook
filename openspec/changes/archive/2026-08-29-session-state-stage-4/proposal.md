## Why

With Stages 1-3 implemented (session state, action system, action-driven state changes), the game needs a way to automatically trigger actions based on conditions. Stage 4 implements the trigger system, enabling condition-based action dispatch after agent steps (e.g., "if player has visited village, unlock ending").

## What Changes

- Add trigger support to entity type definitions in schema
- Parse trigger definitions from YAML (condition → action mapping)
- Load triggers when building entity types
- Implement trigger evaluation middleware (replace stub from Stage 2)
- Evaluate all triggers after each agent step
- Dispatch trigger actions when conditions are true
- Integrate BoolExprEvaluator with current state (effective fields)
- Handle dynamic field references (=expressions) in conditions

## Capabilities

### New Capabilities

- `trigger-system`: Condition-based automatic action dispatch after agent steps

### Modified Capabilities

- `action-system`: TriggerEval middleware now functional (was stub)

## Impact

- **Schema**: New trigger definitions in entity type YAML
- **Entity types**: Load and store triggers
- **Middleware**: TriggerEval middleware evaluates conditions
- **Conditions**: BoolExprEvaluator integrated with session state
