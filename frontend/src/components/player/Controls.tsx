import { Button, Group, Textarea } from '@mantine/core'
import { isNotEmpty, useForm } from '@mantine/form'
import { getHotkeyHandler } from '@mantine/hooks'
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
    validate: { content: isNotEmpty('Must not be empty') },
  })
  const [createRequest, { isLoading }] = sessionApi.useCreateRequestMutation()
  const showError = useShowError()

  const send = async ({ content }: FormValues) => {
    try {
      await createRequest({
        sessionId,
        request: {
          kind: 'request',
          parts: [{ kind: 'user-prompt', content }],
        },
      }).unwrap()
    } catch (error) {
      showError('Failed to send message!', error)
    }
  }

  const handleSubmit = (values: FormValues) => {
    void send(values)
    form.reset()
  }

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
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
          placeholder="Type a message…"
          onKeyUp={getHotkeyHandler([['mod+Enter', form.onSubmit(handleSubmit)]])}
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
