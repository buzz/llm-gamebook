import { Button, Flex, Group, Textarea } from '@mantine/core'
import { skipToken } from '@reduxjs/toolkit/query'
import { IconSend } from '@tabler/icons-react'
import { useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import chatApi from '@/services/chat'
import { iconSizeProps } from '@/utils'
import type { ChatPublic } from '@/types/api'

import Messages from './Messages'
import classes from './Player.module.css'
import useMessages from './useMessages'

interface PlayerLoadedProps {
  chat: ChatPublic
}

function PlayerLoaded({ chat }: PlayerLoadedProps) {
  const messages = useMessages(chat)

  return (
    <Flex direction="column" gap={{ base: 'sm', sm: 'lg' }} justify="center" h="100%">
      <Messages messages={messages} />
      <Group align="stretch" gap="sm">
        <Textarea
          aria-label="Text input"
          autosize
          className={classes.textArea}
          minRows={1}
          maxRows={4}
        />
        <Button
          className={classes.sendButton}
          leftSection={<IconSend {...iconSizeProps('md')} />}
          variant="filled"
        >
          Send
        </Button>
      </Group>
    </Flex>
  )
}

function Player() {
  const { chatId } = useParams()
  const result = chatApi.useGetChatByIdQuery(chatId ?? skipToken)

  return (
    <QueryHandler
      notFoundTitle="Story chat not found"
      notFoundMessage="The story chat does not exist."
      result={result}
    >
      {(chat) => <PlayerLoaded chat={chat} />}
    </QueryHandler>
  )
}

export default Player
