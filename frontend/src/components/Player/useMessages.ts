import { useEffect, useState } from 'react'

import { useShowError } from '@/hooks/notifications'
import useWebSocketConnection from '@/hooks/useWebSocketConnection'
import sessionApi from '@/services/session'
import { assertNever } from '@/types/common'
import type { ModelMessage, SessionFull } from '@/types/api'
import type { WebSocketStatusMessage, WebSocketStreamMessage } from '@/types/websocket'

function useMessages(session: SessionFull) {
  const { refetch } = sessionApi.useGetSessionByIdQuery(session.id)
  const [messages, setMessages] = useState<ModelMessage[]>([])
  const [currentStreamingPartId, setCurrentStreamingPartId] = useState<string | null>(null)
  const { error, lastMessage } = useWebSocketConnection(session.id)
  const showError = useShowError()
  const [lastStreamMessage, setLastStreamMessage] = useState<WebSocketStreamMessage | null>(null)
  const [streamStatus, setStreamStatus] = useState<WebSocketStatusMessage['status']>('stopped')

  // Copy REST API messages into current state
  useEffect(() => {
    setMessages([...session.messages])
  }, [session.messages])

  // Merge streaming message into current state
  useEffect(() => {
    if (lastStreamMessage) {
      setMessages((prev) => {
        const last = prev.at(-1)
        if (last?.id === lastStreamMessage.response.id) {
          // Replace the last message
          return [...prev.slice(0, -1), lastStreamMessage.response]
        }
        // Append new message
        return [...prev, lastStreamMessage.response]
      })

      // Set current streaming part ID
      const currentPart = lastStreamMessage.response.parts.at(-1)
      setCurrentStreamingPartId(currentPart?.id ?? null)
    } else {
      setCurrentStreamingPartId(null)
    }
  }, [lastStreamMessage])

  // Handle stream error
  useEffect(() => {
    if (error !== null) {
      showError(error.name, error)
    }
  }, [error, showError])

  // Handle stream messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.kind) {
        case 'status':
          setStreamStatus(lastMessage.status)
          if (streamStatus === 'stopped') {
            setCurrentStreamingPartId(null)
            void refetch()
          }
          break
        case 'stream':
          setLastStreamMessage(lastMessage)
          break
        default:
          assertNever(lastMessage)
      }
    }
  }, [lastMessage, refetch, streamStatus])

  return {
    currentStreamingPartId,
    messages,
    streamStatus,
  }
}

export default useMessages
