import { Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconX } from '@tabler/icons-react'
import { useCallback } from 'react'

import { isApiQueryError } from '@/types/api'
import { isWebsocketError } from '@/types/websocket'
import { iconSizeProps } from '@/utils'

function useShowError() {
  return useCallback((message: string, error: unknown) => {
    let errorMessage = 'UnknownError'

    if (isApiQueryError(error)) {
      errorMessage = error.status.toString()
      if (typeof error.data.detail === 'string') {
        errorMessage += ` - ${error.data.detail}`
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

export { useShowError }
