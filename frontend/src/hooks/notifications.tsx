import { Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconX } from '@tabler/icons-react'
import { useCallback } from 'react'

import { isApiQueryError } from '@/types/api'
import { iconSizeProps } from '@/utils'

function useShowError() {
  return useCallback((msg: string, error: unknown) => {
    let errorMsg = 'UnknownError'

    if (isApiQueryError(error)) {
      errorMsg = error.status.toString()
      if (typeof error.data.detail === 'string') {
        errorMsg += ` - ${error.data.detail}`
      }
    } else if (error instanceof Error) {
      errorMsg = error.message
    }

    notifications.show({
      title: 'Error',
      message: (
        <>
          {msg}
          <br />
          <Text fz="sm">{errorMsg}</Text>
        </>
      ),
      autoClose: false,
      color: 'red',
      icon: <IconX {...iconSizeProps('lg')} />,
    })
  }, [])
}

export { useShowError }
