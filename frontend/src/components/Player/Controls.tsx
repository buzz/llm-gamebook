import { Button, Group, Textarea } from '@mantine/core'
import { isNotEmpty, useForm } from '@mantine/form'
import { IconSend } from '@tabler/icons-react'

import { useShowError } from '@/hooks/notifications'
import sessionApi from '@/services/session'
import { iconSizeProps } from '@/utils'

import classes from './Controls.module.css'

interface ControlsProps {
  isGenerating: boolean
  sessionId: string
}

interface FormValues {
  content: string
}

function Controls({ isGenerating, sessionId }: ControlsProps) {
  const form = useForm<FormValues>({
    mode: 'controlled',
    initialValues: { content: '' },
    validate: {
      content: isNotEmpty('Must not be empty'),
    },
  })
  const [createRequest, { isLoading }] = sessionApi.useCreateRequestMutation()
  const showError = useShowError()

  const send = async ({ content }: FormValues) => {
    try {
      await createRequest({
        sessionId,
        request: {
          kind: 'request',
          parts: [
            {
              part_kind: 'user-prompt',
              content,
              timestamp: null,
            },
          ],
        },
      }).unwrap()
    } catch (error) {
      showError('Failed to send message!', error)
    }
  }

  return (
    <form onSubmit={form.onSubmit((values) => void send(values))}>
      <Group align="stretch" gap="sm" mt="md">
        <Textarea
          key={form.key('content')}
          {...form.getInputProps('content')}
          aria-label="User message"
          autosize
          className={classes.textArea}
          disabled={isLoading || isGenerating}
          maxRows={4}
          minRows={1}
        />
        <Button
          className={classes.sendButton}
          leftSection={<IconSend {...iconSizeProps('md')} />}
          loading={isLoading || isGenerating}
          type="submit"
          variant="filled"
        >
          Send
        </Button>
      </Group>
    </form>
  )
}

export default Controls
