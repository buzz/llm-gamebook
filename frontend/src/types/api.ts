import { isObject } from './common'
import type { components } from './openapi'

type ServerMessage = components['schemas']['ServerMessage']

type ModelRequest = components['schemas']['ModelRequest']
type ModelRequestCreate = components['schemas']['ModelRequestCreate']

type Session = components['schemas']['Session']
type SessionCreate = components['schemas']['SessionCreate']
type SessionFull = components['schemas']['SessionFull']
type Sessions = components['schemas']['Sessions']
type SessionUpdate = components['schemas']['SessionUpdate']

type ModelMessage = components['schemas']['ModelMessage']
type ThinkingPart = components['schemas']['ThinkingPart']

type ModelConfigCreate = components['schemas']['ModelConfigCreate']
type ModelConfigUpdate = components['schemas']['ModelConfigUpdate']
type ModelConfig = components['schemas']['ModelConfig']
type ModelConfigs = components['schemas']['ModelConfigs']
type ModelProvider = components['schemas']['ModelProvider']
type ModelProviders = components['schemas']['ModelProviders']

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
  ModelConfig,
  ModelConfigCreate,
  ModelConfigs,
  ModelConfigUpdate,
  ModelMessage,
  ModelProvider,
  ModelProviders,
  ModelRequest,
  ModelRequestCreate,
  ServerMessage,
  Session,
  SessionCreate,
  SessionFull,
  Sessions,
  SessionUpdate,
  ThinkingPart,
}
export { isApiQueryError, isApiValidationError }
