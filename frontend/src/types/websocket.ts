import type { components } from './openapi'

type WebSocketClientMessage = components['schemas']['WebSocketClientMessage']
type WebSocketErrorMessage = components['schemas']['WebSocketErrorMessage']
type WebSocketPingMessage = components['schemas']['WebSocketPingMessage']
type WebSocketServerMessage = components['schemas']['WebSocketServerMessage']
type WebSocketStreamMessageMessage = components['schemas']['WebSocketStreamMessageMessage']
type WebSocketStreamPartDeltaMessage = components['schemas']['WebSocketStreamPartDeltaMessage']
type WebSocketStreamPartMessage = components['schemas']['WebSocketStreamPartMessage']
type WebSocketStreamStatusMessage = components['schemas']['WebSocketStreamStatusMessage']

export type {
  WebSocketClientMessage,
  WebSocketErrorMessage,
  WebSocketPingMessage,
  WebSocketServerMessage,
  WebSocketStreamMessageMessage,
  WebSocketStreamPartDeltaMessage,
  WebSocketStreamPartMessage,
  WebSocketStreamStatusMessage,
}
