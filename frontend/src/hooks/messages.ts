import { produce } from 'immer'
import { useEffect, useMemo, useReducer } from 'react'
import type { ReadonlyDeep, WritableDeep } from 'type-fest'

import { useShowErrorModal } from '@/hooks/modals'
import useWebSocketConnection from '@/hooks/websocket'
import sessionApi from '@/services/session'
import { assertNever } from '@/types/common'
import type { Delta, ModelMessage, ModelResponsePart, SessionFull } from '@/types/api'
import type { WebSocketStreamStatusMessage } from '@/types/websocket'

type StreamStatus = WebSocketStreamStatusMessage['status']

interface MessageState {
  messages: Map<string, ModelMessage>
  currentPartId: string | null
  streamStatus: StreamStatus
}

const SYNC_SESSION = Symbol('SYNC_SESSION')
const UPDATE_STATUS = Symbol('UPDATE_STATUS')
const INSERT_MESSAGE = Symbol('INSERT_MESSAGE')
const INSERT_PART = Symbol('INSERT_PART')
const APPLY_DELTA = Symbol('APPLY_DELTA')

type MessageAction =
  | { type: typeof SYNC_SESSION; messages: ReadonlyDeep<ModelMessage[]> }
  | { type: typeof UPDATE_STATUS; status: StreamStatus }
  | { type: typeof INSERT_MESSAGE; message: ModelMessage }
  | { type: typeof INSERT_PART; messageId: string; part: ModelResponsePart }
  | { type: typeof APPLY_DELTA; messageId: string; partId: string; delta: Delta }

const messageReducer = produce((draft: WritableDeep<MessageState>, action: MessageAction) => {
  switch (action.type) {
    case SYNC_SESSION: {
      const newMessages = new Map(action.messages.map((m) => [m.id, m]))
      draft.streamStatus = 'stopped'
      draft.messages = newMessages as WritableDeep<Map<string, ModelMessage>>
      break
    }

    case UPDATE_STATUS: {
      draft.streamStatus = action.status
      draft.currentPartId = null
      break
    }

    case INSERT_MESSAGE: {
      draft.messages.set(action.message.id, action.message as WritableDeep<ModelMessage>)
      const part = action.message.parts.at(0)
      draft.currentPartId = part?.id ?? null
      draft.streamStatus = 'started'
      break
    }

    case INSERT_PART: {
      const message = draft.messages.get(action.messageId)

      // Streaming only for ModelResponse
      if (message?.kind !== 'response') {
        break
      }

      const existingPartIndex = message.parts.findIndex((p) => p.id === action.part.id)

      if (existingPartIndex === -1) {
        // New part: directly push to the array
        message.parts.push(action.part)
      } else {
        // Existing part: directly overwrite at index (happens during dev/double render)
        message.parts[existingPartIndex] = action.part
      }

      draft.currentPartId = action.part.id
      draft.streamStatus = 'started'
      break
    }

    case APPLY_DELTA: {
      const message = draft.messages.get(action.messageId)

      // Streaming only for ModelResponse
      if (message?.kind !== 'response') {
        break
      }

      const partIndex = message.parts.findIndex((p) => p.id === action.partId)
      if (partIndex === -1) {
        break
      }

      const updatedPart = message.parts[partIndex]
      const { delta } = action

      switch (delta.kind) {
        case 'content': {
          if (updatedPart.kind === 'text' || updatedPart.kind === 'thinking') {
            updatedPart.content += delta.content
          }
          break
        }

        case 'tool_args': {
          if (updatedPart.kind === 'tool-call') {
            updatedPart.args =
              updatedPart.args === null ? delta.args : updatedPart.args + delta.args
          }
          break
        }

        case 'tool_name': {
          if (updatedPart.kind === 'tool-call') {
            updatedPart.tool_name += delta.tool_name
          }
          break
        }

        default: {
          assertNever(delta)
        }
      }

      draft.currentPartId = action.partId
      draft.streamStatus = 'started'
      break
    }

    default: {
      assertNever(action)
    }
  }
})

function useMessages(session: SessionFull) {
  const { refetch } = sessionApi.useGetSessionByIdQuery(session.id)
  const { error, lastMessage } = useWebSocketConnection(session.id)
  const showErrorModal = useShowErrorModal()

  const [state, dispatch] = useReducer(messageReducer, {
    messages: new Map(session.messages.map((m) => [m.id, m])),
    currentPartId: null,
    streamStatus: 'started',
  })

  // Sync state if the server-side session messages change (initial load or after refetch)
  useEffect(() => {
    dispatch({ type: SYNC_SESSION, messages: session.messages })
  }, [session.messages])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) {
      return
    }

    switch (lastMessage.kind) {
      case 'stream_status': {
        dispatch({ type: UPDATE_STATUS, status: lastMessage.status })

        // Refetch API message once streaming stopped
        if (lastMessage.status === 'stopped') {
          void refetch()
        }

        break
      }

      case 'stream_message': {
        dispatch({ type: INSERT_MESSAGE, message: lastMessage.message })
        break
      }

      case 'stream_part': {
        dispatch({
          type: INSERT_PART,
          messageId: lastMessage.message_id,
          part: lastMessage.part,
        })
        break
      }

      case 'stream_part_delta': {
        dispatch({
          type: APPLY_DELTA,
          messageId: lastMessage.message_id,
          partId: lastMessage.part_id,
          delta: lastMessage.delta,
        })
        break
      }

      default: {
        assertNever(lastMessage)
      }
    }
  }, [lastMessage, refetch])

  // Handle Errors
  useEffect(() => {
    if (error) showErrorModal(error)
  }, [error, showErrorModal])

  return useMemo(
    () => ({
      currentPartId: state.currentPartId,
      messages: [...state.messages.values()],
      streamStatus: state.streamStatus,
    }),
    [state]
  )
}

export default useMessages
