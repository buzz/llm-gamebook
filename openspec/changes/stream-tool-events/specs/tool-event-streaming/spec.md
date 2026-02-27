## ADDED Requirements

### Requirement: Tool call started events are streamed to frontend

When the LLM agent calls a tool during agent execution, the backend SHALL publish a `ToolCallStartedMessage` containing the tool name, tool call ID, and arguments to the message bus, which SHALL be sent to the frontend via WebSocket.

#### Scenario: Tool call initiated during agent run
- **WHEN** the LLM agent calls a tool via FunctionToolCallEvent during agent execution
- **THEN** the backend publishes a ToolCallStartedMessage with session_id, tool_name, tool_call_id, and args
- **AND** the WebSocket connection sends a message with kind "tool_call_started" to the frontend

#### Scenario: Multiple tools called sequentially
- **WHEN** the LLM agent calls multiple tools in sequence
- **THEN** each tool call publishes a separate ToolCallStartedMessage
- **AND** messages are delivered to the frontend in the order tools were called

### Requirement: Tool result events are streamed to frontend

When a tool execution completes, the backend SHALL publish a `ToolResultMessage` containing the tool call ID and result content to the message bus, which SHALL be sent to the frontend via WebSocket.

#### Scenario: Tool execution completes
- **WHEN** a tool function completes execution and returns a result
- **THEN** the backend publishes a ToolResultMessage with session_id, tool_call_id matching the original call, and content
- **AND** the WebSocket connection sends a message with kind "tool_result" to the frontend

#### Scenario: Tool result correlates with started event
- **WHEN** the frontend receives a ToolResultMessage
- **THEN** it SHALL use tool_call_id to correlate with the corresponding ToolCallStartedMessage
- **AND** update the displayed tool call to show the result

### Requirement: Frontend renders tool events during streaming

The frontend SHALL render tool call events in real-time, showing pending tool calls during execution and updating with results when available.

#### Scenario: Display pending tool call
- **WHEN** the frontend receives a tool_call_started message
- **THEN** it SHALL display the tool name and arguments
- **AND** indicate that the tool is pending (e.g., loading spinner or "Calling..." text)

#### Scenario: Update tool call with result
- **WHEN** the frontend receives a tool_result message
- **THEN** it SHALL find the corresponding pending tool call by tool_call_id
- **AND** replace the pending display with the result content

#### Scenario: Multiple concurrent tool calls
- **WHEN** the frontend receives multiple tool_call_started messages before their results
- **THEN** it SHALL track each tool call separately by tool_call_id
- **AND** update each independently when their respective results arrive
