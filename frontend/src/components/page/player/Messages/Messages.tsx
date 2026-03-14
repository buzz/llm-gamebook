import { Code, ScrollArea, Stack } from '@mantine/core'
import { IconArrowForward, IconTool } from '@tabler/icons-react'
import cx from 'clsx'
import { Streamdown } from 'streamdown'

import type { ModelMessage } from '@/types/api'

import classes from './Messages.module.css'
import ThinkingPart from './ThinkingPart'
import ToolPart from './ToolPart'

interface MessageProps {
  currentPartId: string | null
  message: ModelMessage
}

function Message({ currentPartId, message }: MessageProps) {
  const parts = message.parts.map((part) => {
    const isStreaming = currentPartId === part.id

    switch (part.kind) {
      case 'thinking': {
        return <ThinkingPart key={part.id} isStreaming={isStreaming} part={part} />
      }
      case 'text': {
        return (
          <Streamdown
            animated
            className={cx(classes.text, classes.responseText)}
            isAnimating={isStreaming}
            key={part.id}
            mode={isStreaming ? 'streaming' : 'static'}
          >
            {part.content}
          </Streamdown>
        )
      }
      case 'user-prompt': {
        return (
          <Streamdown className={classes.text} key={part.id} mode="static">
            {part.content}
          </Streamdown>
        )
      }
      case 'tool-call': {
        return (
          <ToolPart icon={IconTool} title="Tool call" key={part.id}>
            <div>
              Name: <Code>{part.tool_name}</Code>
            </div>
            <div>Arguments: {part.args ? <Code>{part.args}</Code> : 'None'}</div>
          </ToolPart>
        )
      }
      case 'tool-return': {
        return (
          <ToolPart icon={IconArrowForward} title="Tool return" key={part.id}>
            <div>
              Content: <Code>{part.content}</Code>
            </div>
          </ToolPart>
        )
      }
      default: {
        return null
      }
    }
  })

  const className = cx(classes.message, {
    [classes.userPrompt]:
      message.kind === 'request' && message.parts.some((p) => p.kind === 'user-prompt'),
  })

  return <div className={className}>{parts}</div>
}

interface MessagesProps {
  /** Currently streaming part ID. */
  currentPartId: string | null

  /** Map of messages by ID. */
  messages: readonly Readonly<ModelMessage>[]
}

function Messages({ currentPartId, messages }: MessagesProps) {
  const content = messages.map((message) => (
    <Message key={message.id} currentPartId={currentPartId} message={message} />
  ))

  return (
    <ScrollArea flex="1 1 auto">
      <Stack gap="sm">{content}</Stack>
    </ScrollArea>
  )
}

export default Messages
