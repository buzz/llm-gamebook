import { use, useEffect, useState } from 'react'

import WebSocketContext from '@/contexts/WebSocketContext'
import { assertNever } from '@/types/typeguards'
import type {
  WebSocketActionDispatchedMessage,
  WebSocketErrorMessage,
  WebSocketServerMessage,
  WebSocketStreamMessageMessage,
  WebSocketStreamPartDeltaMessage,
  WebSocketStreamPartMessage,
  WebSocketStreamStatusMessage,
} from '@/types/websocket'

type WebSocketMessage =
  | WebSocketStreamMessageMessage
  | WebSocketStreamPartDeltaMessage
  | WebSocketStreamPartMessage
  | WebSocketStreamStatusMessage
  | null

function useWebSocketConnection(sessionId: string) {
  const context = use(WebSocketContext)
  const [lastErrorMessage, setLastErrorMessage] = useState<WebSocketErrorMessage | null>(null)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage>(null)

  useEffect(() => {
    if (!context) {
      return
    }

    const handleMessage = (message: WebSocketServerMessage) => {
      switch (message.kind) {
        case 'error': {
          setLastErrorMessage(message)
          break
        }
        case 'pong': {
          break
        }
        case 'stream_status':
        case 'stream_message':
        case 'stream_part':
        case 'stream_part_delta': {
          setLastMessage(message)
          break
        }
        case 'action_dispatched': {
          // Delivered to consumers through useActionDispatched
          break
        }
        default: {
          assertNever(message)
        }
      }
    }

    context.subscribe(sessionId, handleMessage)
    return () => {
      context.unsubscribe(sessionId, handleMessage)
    }
  }, [sessionId, context])

  return {
    error: lastErrorMessage,
    lastMessage,
  }
}

/**
 * Subscribe to dispatched story action events for a session.
 *
 * Exposes the most recently received `action_dispatched` message for the
 * given session (latest-only, no buffer), or `null` before the first event.
 * Events for other sessions are not delivered.
 */
function useActionDispatched(sessionId: string) {
  const context = use(WebSocketContext)
  const [lastEvent, setLastEvent] = useState<WebSocketActionDispatchedMessage | null>(null)

  useEffect(() => {
    if (!context) {
      return
    }

    const handleMessage = (message: WebSocketServerMessage) => {
      if (message.kind === 'action_dispatched') {
        setLastEvent(message)
      }
    }

    context.subscribe(sessionId, handleMessage)
    return () => {
      context.unsubscribe(sessionId, handleMessage)
    }
  }, [sessionId, context])

  return lastEvent
}

export { useActionDispatched }
export default useWebSocketConnection
