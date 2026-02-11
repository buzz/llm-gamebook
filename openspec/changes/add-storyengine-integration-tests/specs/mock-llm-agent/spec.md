## ADDED Requirements

### Requirement: MockLLMAgent class provides tool call responses
The MockLLMAgent class SHALL implement an interface for providing deterministic LLM responses during StoryEngine testing, supporting tool call returns and system prompt validation.

#### Scenario: MockLLMAgent initializes with default expectations
- **WHEN** a test creates a MockLLMAgent instance
- **THEN** the agent has an empty queue of expected responses
- **AND** the agent tracks whether system prompts have been validated

#### Scenario: MockLLMAgent can queue expected responses
- **WHEN** a test calls `mock_llm.expect_tool_call("change_location", {"target": "living_room"})`
- **THEN** the MockLLMAgent adds this expectation to its queue
- **AND** subsequent LLM queries will return this response

#### Scenario: MockLLMAgent returns tool call when queried
- **WHEN** the StoryEngine queries the LLM for a response
- **AND** the MockLLMAgent has an expected tool call in its queue
- **THEN** the MockLLMAgent returns a structured tool call response
- **AND** the tool call name and arguments match the expectation

#### Scenario: MockLLMAgent raises error on unexpected query
- **WHEN** the StoryEngine queries the LLM
- **AND** the MockLLMAgent queue is empty
- **THEN** the MockLLMAgent raises a `ValueError` indicating no expectation was configured

### Requirement: MockLLMAgent validates system prompts
The MockLLMAgent SHALL validate that system prompts contain expected content when queried, ensuring the StoryEngine generates correct context descriptions.

#### Scenario: MockLLMAgent validates location description presence
- **WHEN** MockLLMAgent receives a system prompt for a location change to "living_room"
- **AND** the test has configured an expectation that the system prompt contains "living room"
- **THEN** the validation passes if the description is found
- **AND** the MockLLMAgent proceeds to return the tool call response

#### Scenario: MockLLMAgent reports missing content
- **WHEN** MockLLMAgent receives a system prompt
- **AND** the test expects certain content that is not present
- **THEN** the MockLLMAgent raises an `AssertionError` with details about missing content

#### Scenario: MockLLMAgent can validate multiple content requirements
- **WHEN** a test configures multiple validation expectations
- **THEN** the MockLLMAgent checks that ALL expected content is present
- **AND** only proceeds if all validations pass

### Requirement: MockLLMAgent supports async interface
The MockLLMAgent SHALL implement the async interface expected by StoryEngine, supporting coroutine-based queries and responses.

#### Scenario: MockLLMAgent handles async queries
- **WHEN** the StoryEngine calls `await mock_llm.get_response(system_prompt)`
- **THEN** the MockLLMAgent returns an awaitable response
- **AND** the response contains the expected tool call or validation error

#### Scenario: MockLLMAgent maintains response order
- **WHEN** multiple responses are queued
- **AND** queries are made in sequence
- **THEN** each query returns the next response in the queue
- **AND** responses are consumed in FIFO order
