import { use, useEffect, useState } from 'react'

import WebSocketContext from '@/contexts/WebSocketContext'
import { assertNever } from '@/types/common'
import type {
  WebSocketErrorMessage,
  WebSocketServerMessage,
  WebSocketStatusMessage,
  WebSocketStreamMessage,
} from '@/types/websocket'

function useWebSocketConnection(sessionId: string) {
  const context = use(WebSocketContext)
  const [lastErrorMessage, setLastErrorMessage] = useState<WebSocketErrorMessage | null>(null)
  const [lastMessage, setLastMessage] = useState<
    WebSocketStatusMessage | WebSocketStreamMessage | null
  >(null)

  useEffect(() => {
    if (!context) {
      return
    }

    const handleMessage = (message: WebSocketServerMessage) => {
      switch (message.kind) {
        case 'error':
          setLastErrorMessage(message)
          break
        case 'pong':
          break
        case 'status':
        case 'stream':
          setLastMessage(message)
          break
        default:
          assertNever(message)
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
