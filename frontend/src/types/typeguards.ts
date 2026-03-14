import type { ApiQueryError, ApiValidationError } from './api'
import type { WebSocketErrorMessage } from './websocket'

/** Type guard for `object`. */
function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Utility function to be used as exhaustion check. */
function assertNever(value: never): never {
  // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
  throw new Error(`This code should never be reached. Value='${value}'`)
}

function isApiQueryError(thing: unknown): thing is ApiQueryError {
  return (
    isObject(thing) &&
    typeof thing.status === 'number' &&
    isObject(thing.data) &&
    thing.data.detail !== undefined
  )
}

function isApiValidationError(thing: unknown): thing is ApiValidationError {
  return (
    isApiQueryError(thing) &&
    Array.isArray(thing.data.detail) &&
    thing.data.detail.every((d) => Array.isArray((d as { loc: unknown[] }).loc))
  )
}

function isWebsocketError(thing: unknown): thing is WebSocketErrorMessage {
  return (
    isObject(thing) &&
    thing.kind === 'error' &&
    typeof thing.name === 'string' &&
    typeof thing.message === 'string'
  )
}

export { assertNever, isApiQueryError, isApiValidationError, isObject, isWebsocketError }
