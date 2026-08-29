import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import WebSocketContext from '@/contexts/WebSocketContext'
import type {
  WebSocketActionDispatchedMessage,
  WebSocketServerMessage,
  WebSocketStreamStatusMessage,
} from '@/types/websocket'

import { useActionDispatched } from './websocket'

type EventCallback = (message: WebSocketServerMessage) => void
type SessionSubscribe = (sessionId: string, callback: EventCallback) => void

const SESSION_A = 'session-a'
const SESSION_B = 'session-b'

function makeActionEvent(sessionId: string, actionType: string): WebSocketActionDispatchedMessage {
  return {
    kind: 'action_dispatched',
    sessionId,
    actionType,
    payload: { entity_id: 'locations', to: 'living_room' },
    timestamp: '2026-01-01T00:00:00Z',
  }
}

function makeStreamStatus(sessionId: string): WebSocketStreamStatusMessage {
  return {
    kind: 'stream_status',
    sessionId,
    status: 'started',
  }
}

describe('useActionDispatched', () => {
  // Emulates the provider's per-session fan-out: callbacks are stored per
  // session ID and only invoked for that session's messages.
  let subscribers: Map<string, Set<EventCallback>>
  let subscribe: SessionSubscribe
  let unsubscribe: SessionSubscribe

  const dispatch = (sessionId: string, message: WebSocketServerMessage) => {
    act(() => {
      const callbacks = subscribers.get(sessionId)
      if (callbacks) {
        for (const callback of callbacks) {
          callback(message)
        }
      }
    })
  }

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <WebSocketContext value={{ error: null, subscribe, unsubscribe }}>{children}</WebSocketContext>
  )

  beforeEach(() => {
    subscribers = new Map()
    subscribe = vi.fn((sessionId: string, callback: EventCallback) => {
      if (!subscribers.has(sessionId)) {
        subscribers.set(sessionId, new Set())
      }
      subscribers.get(sessionId)?.add(callback)
    })
    unsubscribe = vi.fn((sessionId: string, callback: EventCallback) => {
      subscribers.get(sessionId)?.delete(callback)
    })
  })

  it('subscribes on mount and unsubscribes on unmount', () => {
    const { unmount } = renderHook(() => useActionDispatched(SESSION_A), { wrapper })

    expect(subscribe).toHaveBeenCalledWith(SESSION_A, expect.any(Function))

    unmount()

    expect(unsubscribe).toHaveBeenCalledWith(SESSION_A, expect.any(Function))
  })

  it('exposes the latest action event for the session', () => {
    const first = makeActionEvent(SESSION_A, 'graph/transition')
    const second = makeActionEvent(SESSION_A, 'core/end-game')

    const { result } = renderHook(() => useActionDispatched(SESSION_A), { wrapper })
    expect(result.current).toBeNull()

    dispatch(SESSION_A, first)
    expect(result.current).toBe(first)

    dispatch(SESSION_A, second)
    expect(result.current).toBe(second)
  })

  it('ignores non-action messages for the session', () => {
    const event = makeActionEvent(SESSION_A, 'graph/transition')

    const { result } = renderHook(() => useActionDispatched(SESSION_A), { wrapper })

    dispatch(SESSION_A, makeStreamStatus(SESSION_A))
    expect(result.current).toBeNull()

    dispatch(SESSION_A, event)
    dispatch(SESSION_A, makeStreamStatus(SESSION_A))
    expect(result.current).toBe(event)
  })

  it("is not invoked for other sessions' events", () => {
    const { result } = renderHook(() => useActionDispatched(SESSION_A), { wrapper })

    dispatch(SESSION_B, makeActionEvent(SESSION_B, 'graph/transition'))

    expect(result.current).toBeNull()
    expect(subscribers.get(SESSION_B)).toBeUndefined()
  })
})
