import { useEffect, useState } from 'react'
import useWebSocket from 'react-use-websocket'

import type { Message } from './useMessages'

interface ServerMessage {
  event: 'llm_message'
  id: string
  created_at: string
  thinking: string | null
  text: string | null
}

function useStreaming(chatId: string) {
  const { lastJsonMessage } = useWebSocket<ServerMessage | null>(
    `ws://localhost:8000/api/ws/${chatId}`
  )
  const [lastServerMessage, setLastServerMessage] = useState<Message | null>(null)

  useEffect(() => {
    if (lastJsonMessage !== null) {
      setLastServerMessage({
        id: lastJsonMessage.id,
        createdAt: new Date(lastJsonMessage.created_at),
        sender: 'llm',
        thinking: lastJsonMessage.thinking,
        text: lastJsonMessage.text ?? '',
      })
    }
  }, [lastJsonMessage, setLastServerMessage])

  return lastServerMessage
}

export default useStreaming
