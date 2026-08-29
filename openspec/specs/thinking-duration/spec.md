# Thinking Duration Display

## Purpose

Displays the actual LLM thinking duration in the `ThinkingPart` button — "Thinking for X seconds…" while streaming and "Thought for X seconds" after streaming ends — using the backend-tracked duration instead of placeholder text.

## Requirements

### Requirement: Show thinking duration after streaming ends

The `ThinkingPart` component button MUST display the actual thinking duration in seconds, regardless of whether streaming is active.

#### Scenario: Button shows duration during streaming

- **WHEN** the component is rendering while `isStreaming` is true and `deltaSecs` has a value
- **THEN** the button label must be "Thinking for {deltaSecs} seconds…"

#### Scenario: Button shows final duration after streaming ends

- **WHEN** streaming has completed and `deltaSecs` has a value but `isStreaming` is false
- **THEN** the button label must be "Thought for {deltaSecs} seconds"
- **AND** the label must not contain "TODO"
