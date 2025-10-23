import { Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconX } from '@tabler/icons-react'
import { useCallback } from 'react'

import { isApiQueryError } from '@/types/api'
import { isWebsocketError } from '@/types/websocket'
import { iconSizeProps } from '@/utils'

function useShowError() {
  return useCallback((msg: string, error: unknown) => {
    let errorMsg = 'UnknownError'

    if (isApiQueryError(error)) {
      errorMsg = error.status.toString()
      if (typeof error.data.detail === 'string') {
        errorMsg += ` - ${error.data.detail}`
      }
    } else if (error instanceof Error || isWebsocketError(error)) {
      errorMsg = error.message
    }

    notifications.show({
      title: 'Error',
      message: (
        <>
          <Text fz="sm" fw="bold">
            {msg}
          </Text>
          <Text fz="sm" lineClamp={5}>
            {errorMsg}
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
