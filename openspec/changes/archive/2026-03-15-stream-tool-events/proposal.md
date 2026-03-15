## Why

Currently, tool calls (FunctionToolCallEvent and FunctionToolResultEvent) are only logged and not streamed to the frontend. The complete tool calls only appear after the entire agent run finishes when the final messages are refetched. Streaming tool events in real-time would improve UX by showing users when a tool is being called and its result as soon as it's available, especially for longer-running tools.

## What Changes

- Extend `ResponseStreamUpdateMessage` or create new message types to carry tool events
- Publish tool call and result events from `_handle_call_tools_node` in `StreamRunner`
- Add new WebSocket message handling in the frontend
- Render tool events in the UI during streaming (e.g., "Calling tool: search_wikipedia..." while executing)

## Capabilities

### New Capabilities

- `tool-event-streaming`: Stream tool call and result events to the frontend in real-time during agent execution

### Modified Capabilities

- None. This is a new capability.

## Impact

- Backend: `llm_gamebook/engine/_runner.py`, `llm_gamebook/engine/message.py`
- Frontend: WebSocket handling (`websocket.ts`, `WebSocketContext.tsx`), message rendering (`use-messages.ts`, `Messages.tsx`)
- No new dependencies required
