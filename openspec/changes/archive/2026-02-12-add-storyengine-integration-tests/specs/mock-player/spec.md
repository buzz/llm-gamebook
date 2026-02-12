## ADDED Requirements

### Requirement: MockPlayer class provides test interface
The MockPlayer class SHALL provide a simplified interface for interacting with the StoryEngine during tests, wrapping engine instantiation, action submission, and state verification.

#### Scenario: MockPlayer initializes with StoryEngine
- **WHEN** a test creates a MockPlayer instance
- **THEN** the MockPlayer instantiates a StoryEngine with a MockLLMAgent
- **AND** the story state is loaded from the test story file
- **AND** the MockPlayer maintains a reference to both the engine and LLM

#### Scenario: MockPlayer can submit player actions
- **WHEN** a test calls `mock_player.take_action("go through the door")`
- **THEN** the MockPlayer submits this action to the StoryEngine
- **AND** the StoryEngine processes it through the LLM
- **AND** the MockPlayer returns the result of the action

#### Scenario: MockPlayer resets state between tests
- **WHEN** a test creates a new MockPlayer instance
- **THEN** the story state is reset to the initial state
- **AND** any previous test state does not affect the new test

### Requirement: MockPlayer verifies story state
The MockPlayer SHALL provide assertion methods for verifying story state during and after test execution.

#### Scenario: MockPlayer verifies current location
- **WHEN** a test calls `mock_player.assert_current_location("living_room")`
- **THEN** the MockPlayer checks the story state for `locations.current_node_id`
- **AND** the assertion passes if the value equals "living_room"
- **AND** raises an `AssertionError` with a descriptive message if it differs

#### Scenario: MockPlayer can verify state before and after actions
- **WHEN** a test verifies state before an action
- **AND** then performs the action
- **AND** then verifies state after the action
- **THEN** the MockPlayer correctly reports state changes

#### Scenario: MockPlayer can verify conditional content state
- **WHEN** a test calls `mock_player.assert_content_active("leaflet_under_door")`
- **THEN** the MockPlayer checks if the content is enabled based on current state
- **AND** returns the appropriate result based on condition evaluation

### Requirement: MockPlayer supports test scenario composition
The MockPlayer SHALL support composing complex test scenarios through chained method calls and configurable expectations.

#### Scenario: MockPlayer can chain multiple actions
- **WHEN** a test chains multiple action calls
- **THEN** each action is processed in sequence
- **AND** the story state updates accordingly after each action

#### Scenario: MockPlayer can configure LLM expectations between actions
- **WHEN** a test configures expectations for multiple steps
- **AND** executes the steps in order
- **THEN** the MockLLMAgent returns the correct response for each step

#### Scenario: MockPlayer provides readable test output
- **WHEN** a test runs with the MockPlayer
- **THEN** the test output shows the action taken and result
- **AND** state verification results are clearly reported
