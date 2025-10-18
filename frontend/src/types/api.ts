import { isObject } from './common'
import type { components } from './openapi'

type ChatCreate = components['schemas']['ChatCreate']
type ChatListPublic = components['schemas']['ChatListPublic']
type ChatPublic = components['schemas']['ChatPublic']
type ChatsPublic = components['schemas']['ChatsPublic']
type ServerMessage = components['schemas']['ServerMessage']

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
  ChatCreate,
  ChatListPublic,
  ChatPublic,
  ChatsPublic,
  ServerMessage,
}
export { isApiQueryError, isApiValidationError }
