import { useEffect, useMemo, useState } from 'react'

import { useShowErrorModal } from '@/hooks/modals'
import useWebSocketConnection from '@/hooks/useWebSocketConnection'
import sessionApi from '@/services/session'
import { assertNever } from '@/types/common'
import type { ModelMessage, SessionFull } from '@/types/api'
import type { WebSocketStatusMessage, WebSocketStreamMessage } from '@/types/websocket'

type WebSocketMessage = WebSocketStatusMessage | WebSocketStreamMessage

function useMessages(session: SessionFull) {
  const { refetch } = sessionApi.useGetSessionByIdQuery(session.id)
  const { error, lastMessage } = useWebSocketConnection(session.id)
  const showErrorModal = useShowErrorModal()

  const [streamingResponse, setStreamingResponse] = useState<ModelMessage | null>(null)
  const [streamStatus, setStreamStatus] = useState<WebSocketStatusMessage['status']>('stopped')

  // We track the previous values to detect changes during render
  const [prevSessionMessages, setPrevSessionMessages] = useState(session.messages)
  const [prevLastMessage, setPrevLastMessage] = useState<WebSocketMessage | null>(null)

  // Pattern: Reset local state when parent data changes
  // This runs *during* render. React detects the state update and immediately
  // restarts the render with the new values, preventing a double-paint.
  if (session.messages !== prevSessionMessages) {
    setPrevSessionMessages(session.messages)
    setStreamingResponse(null)
  }

  // Pattern: Mirror prop updates to local state
  if (lastMessage && lastMessage !== prevLastMessage) {
    setPrevLastMessage(lastMessage)

    switch (lastMessage.kind) {
      case 'status': {
        setStreamStatus(lastMessage.status)
        break
      }
      case 'stream': {
        setStreamingResponse(lastMessage.response)
        break
      }
      default: {
        assertNever(lastMessage)
      }
    }
  }

  // Handle refetching
  useEffect(() => {
    if (lastMessage?.kind === 'status' && lastMessage.status === 'stopped') {
      void refetch()
    }
  }, [lastMessage, refetch])

  // Handle errors
  useEffect(() => {
    if (error) {
      showErrorModal(error)
    }
  }, [error, showErrorModal])

  const { messages, currentStreamingPartId } = useMemo(() => {
    if (streamingResponse) {
      // Streaming updates
      const lastSessionMessage = session.messages.at(-1)
      // Check if we are updating the existing last message or appending a new one
      const isUpdatingLastMessage = lastSessionMessage?.id === streamingResponse.id

      const mergedMessages = isUpdatingLastMessage
        ? [...session.messages.slice(0, -1), streamingResponse]
        : [...session.messages, streamingResponse]

      const currentPart = streamingResponse.parts.at(-1)

      return {
        messages: mergedMessages,
        currentStreamingPartId: streamStatus === 'stopped' ? null : (currentPart?.id ?? null),
      }
    }

    // If no stream is active/buffered, server data is authorative
    return {
      messages: session.messages,
      currentStreamingPartId: null,
    }
  }, [session.messages, streamingResponse, streamStatus])

  return {
    currentStreamingPartId,
    messages,
    streamStatus,
  }
}

export default useMessages
