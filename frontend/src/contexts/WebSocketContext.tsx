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
  const subscribersRef = useRef<Map<string, Set<EventCallback>>>(new Map())
  const { lastJsonMessage: lastMsg } = useWebSocket<WebSocketServerMessage | null>(
    'ws://localhost:8000/api/ws',
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

  const subscribe = useCallback((sessionId: string, callback: EventCallback) => {
    if (!subscribersRef.current.has(sessionId)) {
      subscribersRef.current.set(sessionId, new Set())
    }
    subscribersRef.current.get(sessionId)?.add(callback)
  }, [])

  const unsubscribe = useCallback((sessionId: string, callback: EventCallback) => {
    const sessionSubscribers = subscribersRef.current.get(sessionId)
    if (sessionSubscribers) {
      sessionSubscribers.delete(callback)
      if (sessionSubscribers.size === 0) {
        subscribersRef.current.delete(sessionId)
      }
    }
  }, [])

  // Notify subscribers when messages arrive
  useEffect(() => {
    if (lastMsg) {
      if (lastMsg.kind !== 'pong') {
        if (lastMsg.session_id !== null) {
          const sessionSubscribers = subscribersRef.current.get(lastMsg.session_id)
          if (sessionSubscribers) {
            for (const callback of sessionSubscribers) {
              callback(lastMsg)
            }
          }
        } else if (lastMsg.kind === 'error') {
          setLastError(lastMsg)
        }
      }
    }
  }, [lastMsg])

  const contextValue = {
    error: lastError,
    subscribe,
    unsubscribe,
  }

  return <WebSocketContext value={contextValue}>{children}</WebSocketContext>
}

export { WebSocketProvider }
export default WebSocketContext
