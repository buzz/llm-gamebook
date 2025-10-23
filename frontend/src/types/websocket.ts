import { isObject } from './common'
import type { components } from './openapi'

type WebSocketErrorMessage = components['schemas']['WebSocketErrorMessage']
type WebSocketStatusMessage = components['schemas']['WebSocketStatusMessage']
type WebSocketStreamMessage = components['schemas']['WebSocketStreamMessage']
type WebSocketServerMessage = components['schemas']['WebSocketServerMessage']

type WebSocketPingMessage = components['schemas']['WebSocketPingMessage']
type WebSocketClientMessage = components['schemas']['WebSocketClientMessage']

function isWebsocketError(thing: unknown): thing is WebSocketErrorMessage {
  return (
    isObject(thing) &&
    thing.kind === 'error' &&
    typeof thing.name === 'string' &&
    typeof thing.message === 'string'
  )
}

export type {
  WebSocketClientMessage,
  WebSocketErrorMessage,
  WebSocketPingMessage,
  WebSocketServerMessage,
  WebSocketStatusMessage,
  WebSocketStreamMessage,
}
export { isWebsocketError }
