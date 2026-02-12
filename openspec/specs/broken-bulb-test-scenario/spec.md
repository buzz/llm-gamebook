## ADDED Requirements

### Requirement: Broken Bulb test scenario verifies location transition
The Broken Bulb integration test scenario SHALL verify that the StoryEngine correctly handles location transitions from bedroom to living room, including proper system prompt generation and state updates.

#### Scenario: Initial state is bedroom
- **WHEN** the test scenario initializes
- **THEN** the story state shows `locations.current_node_id == "bedroom"`
- **AND** the initial system prompt contains the bedroom description

#### Scenario: Going through the door triggers change_location
- **WHEN** the player action "go through the door" is submitted
- **AND** the MockLLMAgent returns a `change_location` tool call with `{"target": "living_room"}`
- **THEN** the story state updates to `locations.current_node_id == "living_room"`
- **AND** the subsequent system prompt contains the living room description

#### Scenario: System prompt includes location description after transition
- **WHEN** the location changes from bedroom to living_room
- **THEN** the system prompt passed to the LLM includes "living room" description
- **AND** the description matches the content defined in the story file for the living_room node

### Requirement: Broken Bulb test scenario verifies conditional content
The Broken Bulb integration test scenario SHALL verify that conditional content (leaflet under door) is correctly enabled/disabled based on the player's location.

#### Scenario: Leaflet is enabled when player is in living_room
- **WHEN** the player is in the living room (`locations.current_node_id == "living_room"`)
- **AND** the player examines the area under the door
- **THEN** the system prompt contains the "Leaflet not found" description
- **AND** the MockLLMAgent is configured to expect this content in the system prompt

#### Scenario: Leaflet content is not available when player is elsewhere
- **WHEN** the player is not in the living room
- **AND** the story queries for content under the door
- **THEN** the content is not included in the system prompt
- **AND** the MockLLMAgent validation does not expect the leaflet description

#### Scenario: Conditional evaluation matches enabled rule
- **WHEN** the test scenario evaluates the leaflet condition
- **THEN** the evaluation correctly matches `locations.current_node_id == "living_room"`
- **AND** the content is only activated when this condition is true

### Requirement: Broken Bulb test scenario provides complete story run
The Broken Bulb integration test scenario SHALL exercise a complete story run, testing multiple interactions and state changes to verify StoryEngine behavior end-to-end.

#### Scenario: Complete story run with multiple interactions
- **WHEN** the test executes the full Broken Bulb scenario
- **THEN** the following interactions are tested:
  1. Initial location (bedroom) state verification
  2. Door interaction leading to living_room
  3. Living room description validation
  4. Leaflet examination with conditional content
  5. State consistency throughout interactions

#### Scenario: Test can be run independently
- **WHEN** `pytest tests/integration/test_storyengine.py::test_broken_bulb_complete_run` is executed
- **THEN** the test runs in isolation
- **AND** uses fresh story state
- **AND** completes without side effects on other tests

#### Scenario: Test reports clear pass/fail status
- **WHEN** the Broken Bulb test scenario completes
- **THEN** the pytest report shows the test as passed
- **AND** if any assertion fails, the error message identifies which specific check failed
