import { isObject } from './common'
import type { components } from './openapi'

type ChatPublic = components['schemas']['ChatPublic']
type ChatsPublic = components['schemas']['ChatsPublic']
type ChatListPublic = components['schemas']['ChatListPublic']

interface ServerError {
  detail: string
}

function isServerError(thing: unknown): thing is ServerError {
  return isObject(thing) && typeof thing.detail === 'string'
}

export type { ChatListPublic, ChatPublic, ChatsPublic }
export { isServerError }
