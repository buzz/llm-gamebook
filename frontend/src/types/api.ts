import { isObject } from './common'
import type { components } from './openapi'

type ModelRequest = components['schemas']['ModelRequest']
type ModelRequestCreate = components['schemas']['ModelRequestCreate']
type ServerMessage = components['schemas']['ServerMessage']
type Session = components['schemas']['Session']
type SessionCreate = components['schemas']['SessionCreate']
type SessionFull = components['schemas']['SessionFull']
type Sessions = components['schemas']['Sessions']

type ModelMessage = components['schemas']['ModelMessage']

type ThinkingPart = components['schemas']['ThinkingPart']

interface ApiQueryError {
  data: {
    detail: unknown
  }
  status: number
}

interface ApiValidationError extends Omit<ApiQueryError, 'data'> {
  data: components['schemas']['HTTPValidationError']
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

export type {
  ApiQueryError,
  ApiValidationError,
  ModelMessage,
  ModelRequest,
  ModelRequestCreate,
  ServerMessage,
  Session,
  SessionCreate,
  SessionFull,
  Sessions,
  ThinkingPart,
}
export { isApiQueryError, isApiValidationError }
