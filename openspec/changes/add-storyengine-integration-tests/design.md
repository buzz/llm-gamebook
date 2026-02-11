## Context

The StoryEngine currently lacks automated integration tests. Manual testing is time-consuming and error-prone, especially for complex scenarios involving state transitions and conditional content activation. The Broken Bulb example story demonstrates key functionality that needs testing:

1. **State transitions**: The `change_location` tool updates `locations.current_node_id` correctly
2. **System prompt generation**: System prompts must include accurate location descriptions
3. **Conditional content activation**: Content like the "Leaflet under door" must only appear when conditions are met (e.g., `locations.current_node_id == "living_room"`)

Currently, developers manually run through these scenarios, making it easy to miss regressions. A testing framework would catch these issues automatically and provide confidence in StoryEngine behavior.

## Goals / Non-Goals

**Goals:**
- Create a reusable integration test framework for the StoryEngine
- Simulate LLM behavior without using a real model (MockLLMAgent)
- Simulate player actions and verify state transitions (MockPlayer)
- Test the Broken Bulb story as a complete integration scenario
- Verify that conditional rules evaluate correctly (enabled/disabled content)

**Non-Goals:**
- Unit tests for individual StoryEngine components (those belong in `tests/unit/`)
- Real LLM integration tests (those would require API keys and infrastructure)
- Performance or load testing
- Testing non-StoryEngine components (API endpoints, database, etc.)

## Decisions

### Decision 1: MockLLMAgent instead of real LLM

**Choice**: Create a `MockLLMAgent` class that returns predefined tool calls

**Rationale**: Real LLM integration tests are expensive, slow, and require API keys. A mock agent provides:
- Fast, deterministic test execution
- Complete control over LLM responses
- No external dependencies
- Easy debugging of specific scenarios

**Alternative considered**: Use a local LLM (like Ollama) for testing
- **Rejected**: Still requires infrastructure, slower execution, potential for non-deterministic results

### Decision 2: MockPlayer for state verification

**Choice**: Create a `MockPlayer` class that wraps StoryEngine interaction

**Rationale**: The MockPlayer provides:
- Clean interface for test code to interact with the engine
- Built-in assertions for state verification
- Reusable patterns for common test scenarios
- Clear separation between test logic and engine interaction

**Alternative considered**: Write tests directly against StoryEngine
- **Rejected**: Leads to boilerplate code in each test, harder to maintain

### Decision 3: Test file structure

**Choice**: Place integration tests in `backend/tests/integration/test_storyengine.py`

**Rationale**:
- Follows pytest conventions with `test_*.py` naming
- Separates integration tests from unit tests
- Easy to discover with `pytest` discovery
- Matches existing test structure in the codebase

### Decision 4: Broken Bulb as the test story

**Choice**: Use the existing Broken Bulb example story as the primary test scenario

**Rationale**:
- Story already exists, no need to create test data
- Demonstrates key features (location transitions, conditional content)
- Familiar to the team, easier to understand tests
- Can add more scenarios later if needed

### Decision 5: Use pytest fixtures for setup

**Choice**: Define pytest fixtures for `story_engine`, `mock_llm_agent`, `mock_player`

**Rationale**:
- Provides clean test setup/teardown
- Reusable across multiple tests
- Easy to customize per-test if needed
- Follows pytest best practices

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| MockLLMAgent too simplistic | May miss bugs that only occur with real LLM behavior | Start simple, add complexity as needed; complement with occasional real LLM tests |
| Test scenarios incomplete | May miss edge cases in StoryEngine behavior | Start with key scenarios (Broken Bulb), expand coverage iteratively |
| Story format changes | Tests may break if story schema changes | Use the actual story file, not hardcoded data; add schema validation |
| State reset between tests | Tests may interfere with each other | Use pytest fixtures with fresh state; consider test database isolation |
