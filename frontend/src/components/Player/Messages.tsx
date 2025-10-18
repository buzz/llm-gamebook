import { Button, Collapse, Paper, ScrollArea, Stack } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconBrain, IconChevronDown } from '@tabler/icons-react'
import { clsx } from 'clsx'
import { Streamdown } from 'streamdown'

import { iconSizeProps } from '@/utils'

import classes from './Player.module.css'
import type { Message } from './useMessages'

interface MessagePaperProps {
  message: Message
}

function MessagePaper({ message }: MessagePaperProps) {
  const [thinkingOpened, { toggle: toggleThinking }] = useDisclosure(false)

  return (
    <Paper bg="dark" shadow="xs" p="sm">
      <div className={classes.thinking}>
        <Button
          classNames={{ root: classes.toggleBtn, inner: classes.toggleBtnInner }}
          fullWidth
          leftSection={<IconBrain {...iconSizeProps('sm')} />}
          rightSection={
            <IconChevronDown
              className={clsx(classes.chevron, classes[thinkingOpened ? 'rot-180' : 'rot-0'])}
              {...iconSizeProps('sm')}
            />
          }
          onClick={toggleThinking}
          size="xs"
          variant="transparent"
        >
          Thinking…
        </Button>
        <Collapse in={thinkingOpened}>
          <Streamdown className={clsx(classes.thinkingText, classes.text)}>
            {message.thinking}
          </Streamdown>
        </Collapse>
      </div>
      <Streamdown isAnimating className={clsx(classes.llmText, classes.text)}>
        {message.text}
      </Streamdown>
    </Paper>
  )
}

interface MessagesProps {
  messages: Message[]
}

function Messages({ messages }: MessagesProps) {
  const content = messages.map((msg) => <MessagePaper key={msg.id} message={msg} />)

  return (
    <ScrollArea className={classes.messages}>
      <Stack gap="sm">{content}</Stack>
    </ScrollArea>
  )
}

export default Messages
