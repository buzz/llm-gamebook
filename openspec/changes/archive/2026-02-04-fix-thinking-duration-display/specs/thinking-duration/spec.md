# Thinking Duration Display

## ADDED Requirements

### Requirement: Show thinking duration after streaming ends

The `ThinkingPart` component button must display the actual thinking duration in seconds, regardless of whether streaming is active.

#### Scenario: Button shows duration during streaming

- **WHEN** the component is rendering while `isStreaming` is true and `deltaSecs` has a value
- **THEN** the button label must be "Thinking for {deltaSecs} seconds…"

#### Scenario: Button shows final duration after streaming ends

- **WHEN** streaming has completed and `deltaSecs` has a value but `isStreaming` is false
- **THEN** the button label must be "Thought for {deltaSecs} seconds"
- **AND** the label must not contain "TODO"
