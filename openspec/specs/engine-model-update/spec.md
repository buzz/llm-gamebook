## ADDED Requirements

### Requirement: StoryEngine can update its model at runtime without recreation

The StoryEngine SHALL provide a method to replace its underlying Model instance without destroying and recreating the entire engine. This allows the engine to continue using its existing state and session history while switching to a different model configuration.

#### Scenario: Update model on running engine

- **WHEN** `StoryEngine.set_model(new_model)` is called on an active engine
- **THEN** Engine replaces its internal Model instance with `new_model`
- **AND** Engine continues to use existing StoryState
- **AND** Engine continues to use existing session message history
- **AND** Subsequent agent runs use the new model

#### Scenario: Model update preserves agent configuration

- **WHEN** model is updated via `set_model()`
- **THEN** Agent's tool definitions remain unchanged
- **AND** Agent's model settings (temperature, seed) remain unchanged
- **AND** Agent's prepare_tools callback remains unchanged
- **AND** Agent's output type remains unchanged

#### Scenario: Model update is thread-safe

- **WHEN** `set_model()` is called while engine is processing a request
- **THEN** Model replacement is atomic
- **AND** Current in-progress request uses original model
- **AND** Subsequent requests use new model
