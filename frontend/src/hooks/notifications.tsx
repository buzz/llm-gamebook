import { Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { IconCheck, IconX } from '@tabler/icons-react'
import { useCallback } from 'react'

import { iconSizeProps, standardizeErrorMessage } from '@/utils'

function useShowError() {
  return useCallback((message: string, error: unknown) => {
    const errDisp = standardizeErrorMessage(error)

    notifications.show({
      title: 'Error',
      message: (
        <>
          <Text fz="sm" fw="bold">
            {message}
          </Text>
          <Text fz="sm" lineClamp={5}>
            {errDisp.name}: {errDisp.message}
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
