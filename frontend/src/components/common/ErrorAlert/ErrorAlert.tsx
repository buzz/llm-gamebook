import { Alert, Box, Button, Code, Stack } from '@mantine/core'
import { IconBug, IconRefresh } from '@tabler/icons-react'

import { isApiQueryError, isApiValidationError } from '@/types/api'
import { isWebsocketError } from '@/types/websocket'
import { iconSizeProps } from '@/utils'

import classes from './ErrorAlert.module.css'

interface ErrorAlertProps {
  error: unknown
  resetErrorBoundary?: (...args: unknown[]) => void
}

function ErrorAlert({ error, resetErrorBoundary }: ErrorAlertProps) {
  let title = 'Unknown Error'
  let message: string | null = null
  let code: string | null = null

  if (isApiQueryError(error)) {
    title = isApiValidationError(error)
      ? `${error.status.toString()} Validation Error`
      : `${error.status.toString()} Query Error`
    code = JSON.stringify(error.data.detail, undefined, 2)
  } else if (isWebsocketError(error)) {
    title = error.name
    message = error.message
  } else if (error instanceof Error) {
    if (error.name) {
      title = error.name
    }
    if (error.message) {
      message = error.message
    }
    if (error.stack) {
      code = error.stack
    }
  }

  return (
    <Alert
      classNames={{ body: classes.body, title: classes.title }}
      color="red"
      icon={<IconBug {...iconSizeProps('lg')} />}
      title={title}
      variant="outline"
    >
      <Stack>
        <Box className={classes.message}>
          {message ?? 'Some unknown error occured. Please check the console for details.'}
        </Box>
        {code ? (
          <Box className={classes.codeWrap}>
            <Code block>{code}</Code>
          </Box>
        ) : null}
        {resetErrorBoundary === undefined ? null : (
          <Button
            leftSection={<IconRefresh {...iconSizeProps('md')} />}
            onClick={resetErrorBoundary}
            variant="default"
          >
            Retry
          </Button>
        )}
      </Stack>
    </Alert>
  )
}

export default ErrorAlert
