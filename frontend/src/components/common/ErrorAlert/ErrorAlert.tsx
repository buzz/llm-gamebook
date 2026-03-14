import { Alert, Box, Button, Code, Stack } from '@mantine/core'
import { IconBug, IconRefresh } from '@tabler/icons-react'

import { iconSizeProps, standardizeErrorMessage } from '@/utils'

import classes from './ErrorAlert.module.css'

interface ErrorAlertProps {
  error: unknown
  resetErrorBoundary?: (...args: unknown[]) => void
}

function ErrorAlert({ error, resetErrorBoundary }: ErrorAlertProps) {
  const errDisp = standardizeErrorMessage(error)

  return (
    <Alert
      classNames={{ body: classes.body, title: classes.title }}
      color="red"
      icon={<IconBug {...iconSizeProps('lg')} />}
      title={errDisp.name}
      variant="outline"
    >
      <Stack>
        <Box className={classes.message}>
          {errDisp.message ?? 'Some unknown error occured. Please check the console for details.'}
        </Box>
        {errDisp.details ? (
          <div>
            <Code block>{errDisp.details}</Code>
          </div>
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
