import { use, useEffect, useState } from 'react'

import WebSocketContext from '@/contexts/WebSocketContext'
import { assertNever } from '@/types/common'
import type {
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

export default useWebSocketConnection
