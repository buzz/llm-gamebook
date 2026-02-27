## 1. Backend - Message Types

- [ ] 1.1 Add `ToolCallStartedMessage` to `engine/message.py` (session_id, tool_name, tool_call_id, args)
- [ ] 1.2 Add `ToolResultMessage` to `engine/message.py` (session_id, tool_call_id, content)

## 2. Backend - StreamRunner Changes

- [ ] 2.1 Import new message types in `_runner.py`
- [ ] 2.2 Publish `ToolCallStartedMessage` when receiving `FunctionToolCallEvent` in `_handle_call_tools_node`
- [ ] 2.3 Publish `ToolResultMessage` when receiving `FunctionToolResultEvent` in `_handle_call_tools_node`

## 3. Frontend - WebSocket Types

- [ ] 3.1 Add `ToolCallStartedMessage` type to `frontend/src/types/websocket.ts`
- [ ] 3.2 Add `ToolResultMessage` type to `frontend/src/types/websocket.ts`
- [ ] 3.3 Add "tool_call_started" and "tool_result" to WebSocket message kind union

## 4. Frontend - WebSocket Handling

- [ ] 4.1 Update `WebSocketContext.tsx` to handle new message kinds
- [ ] 4.2 Update `useWebSocketConnection` hook to pass through tool messages

## 5. Frontend - State Management

- [ ] 5.1 Add tool call state tracking in `use-messages.ts` (pending tool calls map keyed by tool_call_id)
- [ ] 5.2 Handle tool_call_started messages to add pending tool calls
- [ ] 5.3 Handle tool_result messages to update pending tool calls with results

## 6. Frontend - UI Rendering

- [ ] 6.1 Update `ToolPart.tsx` component to support "pending" state
- [ ] 6.2 Update `Messages.tsx` to render pending tool calls from state
- [ ] 6.3 Ensure tool calls are displayed in correct position relative to other message parts

## 7. Testing

- [ ] 7.1 Test backend publishes tool events correctly (manual or integration test)
- [ ] 7.2 Test frontend receives and displays tool events
- [ ] 7.3 Run backend lint/typecheck
- [ ] 7.4 Run frontend lint/typecheck
