## ADDED Requirements

### Requirement: Integration test framework for StoryEngine
The system SHALL provide a pytest-based integration test framework for the StoryEngine that enables testing complete story runs with simulated player and LLM agent behavior.

#### Scenario: Test framework initializes correctly
- **WHEN** pytest loads the `test_storyengine.py` module
- **THEN** the `story_engine`, `mock_llm_agent`, and `mock_player` fixtures are available

#### Scenario: StoryEngine can be instantiated in test context
- **WHEN** the `story_engine` fixture is used in a test
- **THEN** a StoryEngine instance is created with a mock LLM agent
- **AND** the story state is initialized to the starting node

#### Scenario: Multiple test runs maintain isolation
- **WHEN** two tests use the `story_engine` fixture
- **THEN** each test gets a fresh StoryEngine instance
- **AND** state from one test does not affect another

### Requirement: MockLLMAgent provides deterministic responses
The MockLLMAgent class SHALL return predefined tool calls for test scenarios, ensuring deterministic and repeatable test execution without requiring a real LLM.

#### Scenario: MockLLMAgent returns specified tool call
- **WHEN** a test configures MockLLMAgent with `expect_tool_call("change_location", {"target": "living_room"})`
- **AND** the StoryEngine queries the LLM for a response
- **THEN** the MockLLMAgent returns a tool call with name `change_location` and arguments `{"target": "living_room"}`

#### Scenario: MockLLMAgent validates system prompt content
- **WHEN** MockLLMAgent receives a system prompt
- **THEN** it validates that the prompt contains expected location descriptions
- **AND** raises an assertion error if expected content is missing

#### Scenario: MockLLMAgent supports multiple sequential responses
- **WHEN** a test configures multiple expected tool calls
- **AND** the StoryEngine queries the LLM multiple times
- **THEN** the MockLLMAgent returns each configured response in order

### Requirement: MockPlayer verifies state transitions
The MockPlayer class SHALL provide an interface for simulating player actions and verifying story state transitions during integration tests.

#### Scenario: MockPlayer can change locations
- **WHEN** a test calls `mock_player.change_location("living_room")`
- **AND** the MockPlayer's configured LLM response is a `change_location` tool call
- **THEN** the story engine processes the action
- **AND** the story state updates to show `locations.current_node_id == "living_room"`

#### Scenario: MockPlayer can verify location state
- **WHEN** a test calls `mock_player.verify_current_location("living_room")`
- **THEN** the assertion passes if `locations.current_node_id == "living_room"`
- **AND** raises an assertion error if the current location differs

#### Scenario: MockPlayer can execute arbitrary player actions
- **WHEN** a test provides an action description
- **AND** configures the expected LLM response
- **THEN** the MockPlayer submits the action and verifies the result

### Requirement: Test scenarios are executable
The integration test framework SHALL support defining and executing test scenarios that verify specific StoryEngine behaviors.

#### Scenario: Test scenario verifies location transition
- **WHEN** a test scenario simulates starting in "bedroom"
- **AND** the player goes through the door to "living_room"
- **THEN** the MockLLMAgent is called with a system prompt containing the bedroom description
- **AND** the MockLLMAgent returns a `change_location` tool call to "living_room"
- **AND** the subsequent system prompt contains the living room description

#### Scenario: Test scenario verifies conditional content activation
- **WHEN** a test scenario simulates the player entering the living room
- **AND** the player examines the leaflet under the door
- **THEN** the MockLLMAgent is configured to expect a tool call to examine the leaflet
- **AND** the system prompt contains the "Leaflet not found" description since `locations.current_node_id == "living_room"`

#### Scenario: Test scenario can be run with pytest
- **WHEN** `pytest tests/integration/test_storyengine.py` is executed
- **THEN** all defined test scenarios run successfully
- **AND** the test report shows passed/failed status for each scenario
