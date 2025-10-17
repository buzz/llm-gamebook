import { Button, Flex, Group, Textarea } from '@mantine/core'
import { IconSend } from '@tabler/icons-react'

import type { ChatPublic } from '@/types/api'

import Messages from './Messages'
import classes from './Player.module.css'
import useMessages from './useMessages'

interface PlayerProps {
  chat: ChatPublic
}

function Player({ chat }: PlayerProps) {
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
        <Button className={classes.sendButton} leftSection={<IconSend />} variant="filled">
          Send
        </Button>
      </Group>
    </Flex>
  )
}

export default Player
