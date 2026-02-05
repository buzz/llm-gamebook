import { Box, Code, ScrollArea, Stack } from '@mantine/core'
import { IconArrowForward, IconTool } from '@tabler/icons-react'
import { clsx } from 'clsx'
import { Streamdown } from 'streamdown'

import type { ModelMessage } from '@/types/api'

import classes from './Messages.module.css'
import ThinkingPart from './ThinkingPart'
import ToolPart from './ToolPart'

interface MessageProperties {
  currentStreamingPartId: string | null
  message: ModelMessage
}

function Message({ currentStreamingPartId, message }: MessageProperties) {
  const parts = message.parts.map((part) => {
    switch (part.part_kind) {
      case 'thinking': {
        return (
          <ThinkingPart
            key={part.id}
            part={part}
            isStreaming={currentStreamingPartId === part.id}
          />
        )
      }
      case 'text':
      case 'user-prompt': {
        return (
          <Streamdown className={classes.text} key={part.id}>
            {part.content}
          </Streamdown>
        )
      }
      case 'tool-call': {
        return (
          <ToolPart icon={IconTool} title="Tool call" key={part.id}>
            <Box>
              Name: <Code>{part.tool_name}</Code>
            </Box>
            <Box>
              Arguments:{' '}
              {part.args ? (
                <Code>{typeof part.args === 'string' ? part.args : JSON.stringify(part.args)}</Code>
              ) : (
                'None'
              )}
            </Box>
          </ToolPart>
        )
      }
      case 'tool-return': {
        return (
          <ToolPart icon={IconArrowForward} title="Tool return" key={part.id}>
            <Box>
              Content: <Code>{part.content}</Code>
            </Box>
          </ToolPart>
        )
      }
      default: {
        return null
      }
    }
  })

  const className = clsx(classes.message, {
    [classes.userPrompt]:
      message.kind === 'request' && message.parts.some((p) => p.part_kind === 'user-prompt'),
  })

  return <Box className={className}>{parts}</Box>
}

interface MessagesProperties {
  currentStreamingPartId: string | null
  messages: ModelMessage[]
}

function Messages({ currentStreamingPartId, messages }: MessagesProperties) {
  const content = messages.map((message) => (
    <Message key={message.id} currentStreamingPartId={currentStreamingPartId} message={message} />
  ))

  return (
    <ScrollArea flex="1 1 auto">
      <Stack gap="sm">{content}</Stack>
    </ScrollArea>
  )
}

export default Messages
