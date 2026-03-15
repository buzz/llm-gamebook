## Context

The `StreamRunner` class in `_runner.py` handles streaming LLM responses to the frontend via WebSocket. Currently, `ModelRequestNode` streams partial response tokens, but `CallToolsNode` only logs `FunctionToolCallEvent` and `FunctionToolResultEvent` - they are not published to the message bus. The frontend only sees tool calls after the entire agent run completes.

The WebSocket protocol uses JSON messages with `kind` field (`status` | `stream`). Stream updates currently carry a `ModelResponse` object. The frontend renders `ToolCallPart` and `ToolReturnPart` components.

## Goals / Non-Goals

**Goals:**
- Stream tool call events to frontend in real-time during agent execution
- Show tool name and arguments when a tool is called
- Show tool results when they become available

**Non-Goals:**
- Change tool execution logic (tools still execute the same way)
- Add tool cancellation or retry capabilities
- Modify the REST API or final message format

## Decisions

### 1. New message types vs extending ResponseStreamUpdateMessage

**Decision:** Create new message types (`ToolCallStartedMessage`, `ToolResultMessage`)

**Rationale:** Tool events are distinct from model response streaming - they have different semantics (started/completed vs streaming tokens). Separate message types keep the concerns clean and make frontend handling clearer. The alternative of adding optional tool fields to ResponseStreamUpdateMessage would make that class more complex.

### 2. Message structure

**ToolCallStartedMessage:**
- `session_id: UUID`
- `tool_name: str`
- `tool_call_id: str`
- `args: dict` (tool arguments)

**ToolResultMessage:**
- `session_id: UUID`
- `tool_call_id: str`
- `content: str` (result content)

**Rationale:** These map directly to the Pydantic AI events (`FunctionToolCallEvent`, `FunctionToolResultEvent`). Using the same `tool_call_id` allows the frontend to correlate start and result.

### 3. WebSocket message format

The existing WebSocket already handles different message kinds. Add a new `kind: "tool_call_started"` and `kind: "tool_result"` variant to the stream message type in the frontend.

**Alternative considered:** Keep using `kind: "stream"` with a union type for the payload. Rejected because tool events aren't really "stream" updates - they're separate event types.

### 4. Frontend handling

The frontend will:
1. Subscribe to new message types in the WebSocket context
2. Store active tool calls in state (keyed by `tool_call_id`)
3. Render a pending tool call indicator during execution
4. Replace pending call with result when received

The existing `ToolPart` component can be reused with a "pending" state.

## Risks / Trade-offs

- [Risk] Tool events may come very fast for quick tools → Impact is minimal - they'll just appear in quick succession. No mitigation needed.
- [Risk] If tool events arrive between model response chunks, ordering may be slightly jumbled → Acceptable - tool execution order doesn't need to be strictly preserved relative to text streaming.
- [Risk] Multiple tools may run concurrently → The frontend should handle multiple pending tool calls by tracking them in a map keyed by `tool_call_id`.
