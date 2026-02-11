## Why

The StoryEngine lacks automated integration tests, forcing developers to manually verify complete story runs. This leads to undetected regressions, especially for complex scenarios involving state transitions (like `change_location`) and conditional content activation (like the leaflet in the living room). Without simulated player and LLM agent testing, we cannot reliably verify that system prompts include correct descriptions or that conditional rules evaluate properly.

## What Changes

- Add a new integration test framework for StoryEngine
- Create a `MockLLMAgent` class to simulate LLM responses and tool calls
- Create a `MockPlayer` class to simulate player actions and verify state
- Implement test scenarios that verify:
  - Location transitions update story state correctly
  - System prompts contain expected location descriptions
  - Conditional content (like leaflets) activates based on conditions
- Add a complete test run using the Broken Bulb example story

## Capabilities

### New Capabilities
- `storyengine-integration-testing`: Core framework for integration testing the StoryEngine, including mock LLM agent, mock player, and test scenario definitions
- `mock-llm-agent`: Simulates LLM behavior by returning predefined tool calls and validating system prompts
- `mock-player`: Simulates player actions and verifies story state transitions
- `broken-bulb-test-scenario`: Integration test scenario that verifies location changes and conditional content activation in the Broken Bulb story

### Modified Capabilities
- (none)

## Impact

- **New Code**: `backend/tests/integration/` directory with test modules
- **Dependencies**: Pytest fixtures, possibly `pytest-asyncio` for async tests
- **StoryEngine**: The StoryEngine will be instantiated in tests with a mock LLM agent
- **Test Stories**: The Broken Bulb example story will be used as the test scenario
