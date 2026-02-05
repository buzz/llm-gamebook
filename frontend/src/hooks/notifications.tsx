import { Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconCheck, IconX } from '@tabler/icons-react'
import { useCallback } from 'react'

import { isApiQueryError, isApiValidationError } from '@/types/api'
import { isWebsocketError } from '@/types/websocket'
import { iconSizeProps } from '@/utils'

function useShowError() {
  return useCallback((message: string, error: unknown) => {
    let errorMessage = 'UnknownError'

    if (isApiQueryError(error)) {
      if (isApiValidationError(error) && Array.isArray(error.data.detail)) {
        const validationErrors = error.data.detail
          .map((err) => {
            const field = Array.isArray(err.loc) ? err.loc.join('.') : 'unknown field'
            return `${field}: ${err.msg || 'validation error'}`
          })
          .join(', ')
        errorMessage = `Validation error: ${validationErrors}`
      } else if (typeof error.data.detail === 'string') {
        errorMessage = String(error.status) + ' - ' + error.data.detail
      } else {
        errorMessage = String(error.status)
      }
    } else if (error instanceof Error || isWebsocketError(error)) {
      errorMessage = error.message
    }

    notifications.show({
      title: 'Error',
      message: (
        <>
          <Text fz="sm" fw="bold">
            {message}
          </Text>
          <Text fz="sm" lineClamp={5}>
            {errorMessage}
          </Text>
        </>
      ),
      autoClose: 30_000,
      color: 'red',
      icon: <IconX {...iconSizeProps('lg')} />,
    })
  }, [])
}

function useShowSuccess() {
  return useCallback((message: string) => {
    notifications.show({
      title: 'Success',
      message: (
        <Text fz="sm" fw="bold">
          {message}
        </Text>
      ),
      autoClose: 5000,
      color: 'teal',
      icon: <IconCheck {...iconSizeProps('lg')} />,
    })
  }, [])
}

export { useShowError, useShowSuccess }
