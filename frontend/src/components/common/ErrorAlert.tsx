import { Alert, Center } from '@mantine/core'
import { IconBug } from '@tabler/icons-react'
import type { SerializedError } from '@reduxjs/toolkit'

import { isApiQueryError, isApiValidationError } from '@/types/api'
import { iconSizeProps, truncate } from '@/utils'
import type { ApiQueryError } from '@/types/api'

interface ErrorAlertProps {
  error: Error | ApiQueryError | SerializedError
}

function ErrorAlert({ error }: ErrorAlertProps) {
  let title = 'Unknown Error'
  let message: string | null = null
  let code: string | null = null

  if (isApiQueryError(error)) {
    if (isApiValidationError(error)) {
      title = `${error.status.toString()} Validation Error`
    } else {
      title = `${error.status.toString()} Query Error`
    }
    code = JSON.stringify(error.data.detail, undefined, 2)
  } else {
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

  code = typeof code === 'string' ? truncate(code, 200) : code

  return (
    <Center h="100%">
      <Alert
        color="red"
        icon={<IconBug {...iconSizeProps('lg')} />}
        title={title}
        variant="outline"
      >
        {message}
        {code ? <pre>{code}</pre> : null}
      </Alert>
    </Center>
  )
}

export default ErrorAlert
