import { useEffect, useState } from 'react'
import useWebSocket from 'react-use-websocket'

import type { Message } from './useMessages'

interface MessageUpdate {
  event: 'llm_message'
  finish_reason: 'stop' | null
  message: {
    id: string
    created_at: string
    thinking: string | null
    text: string | null
  }
}

function useStreaming(chatId: string) {
  const { lastJsonMessage } = useWebSocket<MessageUpdate | null>(
    `ws://localhost:8000/api/ws/${chatId}`
  )
  const [lastServerMessage, setLastServerMessage] = useState<Message | null>(null)

  useEffect(() => {
    if (lastJsonMessage !== null) {
      setLastServerMessage({
        id: lastJsonMessage.message.id,
        createdAt: new Date(lastJsonMessage.message.created_at),
        sender: 'llm',
        thinking: lastJsonMessage.message.thinking,
        text: lastJsonMessage.message.text ?? '',
      })
    }
  }, [lastJsonMessage, setLastServerMessage])

  return lastServerMessage
}

export default useStreaming
