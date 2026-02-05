import { createContext, useCallback, useEffect, useRef, useState } from 'react'
import useWebSocket from 'react-use-websocket'

import type {
  WebSocketErrorMessage,
  WebSocketPingMessage,
  WebSocketServerMessage,
} from '@/types/websocket'

interface WebSocketContextValue {
  error: WebSocketErrorMessage | null
  subscribe: (sessionId: string, callback: EventCallback) => void
  unsubscribe: (sessionId: string, callback: EventCallback) => void
}

type EventCallback = (message: WebSocketServerMessage) => void

const WebSocketContext = createContext<WebSocketContextValue | undefined>(undefined)

const pingMessage = JSON.stringify({ kind: 'ping' } satisfies WebSocketPingMessage)

function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const subscribersReference = useRef<Map<string, Set<EventCallback>>>(new Map())

  const { lastJsonMessage: lastMessage } = useWebSocket<WebSocketServerMessage | null>(
    'ws://localhost:8000/ws',
    {
      heartbeat: {
        message: pingMessage,
        timeout: 60_000,
        interval: 10_000,
      },
      shouldReconnect: () => true,
    }
  )

  const [lastError, setLastError] = useState<WebSocketErrorMessage | null>(null)
  const [prevLastMessage, setPrevLastMessage] = useState(lastMessage)

  // Sync state updates
  if (lastMessage !== prevLastMessage) {
    setPrevLastMessage(lastMessage)

    // If it is an error, we update state immediately
    if (lastMessage?.kind === 'error') {
      setLastError(lastMessage)
    }
  }

  // Subscriber notification
  useEffect(() => {
    if (lastMessage && lastMessage.kind !== 'pong' && lastMessage.session_id !== null) {
      const sessionSubscribers = subscribersReference.current.get(lastMessage.session_id)

      if (sessionSubscribers) {
        for (const callback of sessionSubscribers) {
          callback(lastMessage)
        }
      }
    }
  }, [lastMessage])

  const subscribe = useCallback((sessionId: string, callback: EventCallback) => {
    if (!subscribersReference.current.has(sessionId)) {
      subscribersReference.current.set(sessionId, new Set())
    }
    subscribersReference.current.get(sessionId)?.add(callback)
  }, [])

  const unsubscribe = useCallback((sessionId: string, callback: EventCallback) => {
    const sessionSubscribers = subscribersReference.current.get(sessionId)
    if (sessionSubscribers) {
      sessionSubscribers.delete(callback)
      if (sessionSubscribers.size === 0) {
        subscribersReference.current.delete(sessionId)
      }
    }
  }, [])

  const contextValue = {
    error: lastError,
    subscribe,
    unsubscribe,
  }

  return <WebSocketContext value={contextValue}>{children}</WebSocketContext>
}

export { WebSocketProvider }
export default WebSocketContext
