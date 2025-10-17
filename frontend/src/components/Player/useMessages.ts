import { useEffect, useState } from 'react'

import type { ChatPublic } from '@/types/api'

import useStreaming from './useStreaming'

interface Message {
  id: string
  createdAt: Date
  sender: 'human' | 'llm'
  thinking: string | null
  text: string
}

function createMessages(loadedMessages: ChatPublic['messages']) {
  return loadedMessages.map<Message>((msg) => ({
    ...msg,
    createdAt: new Date(msg.created_at),
  }))
}

function useMessages(chat: ChatPublic) {
  const [messages, setMessages] = useState<Message[]>([])
  const lastStreamingMessage = useStreaming(chat.id)

  useEffect(() => {
    setMessages(createMessages(chat.messages))
  }, [chat.messages])

  useEffect(() => {
    if (lastStreamingMessage !== null) {
      setMessages((prev) => prev.concat(lastStreamingMessage))
    }
  }, [lastStreamingMessage, setMessages])

  return messages
}

export type { Message }
export default useMessages
