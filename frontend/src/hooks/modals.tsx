import { Stack, Text } from '@mantine/core'
import { modals } from '@mantine/modals'
import { useCallback } from 'react'

import ErrorAlert from '@/components/common/ErrorAlert'

function useShowConfirmationModal() {
  return useCallback(
    (title: string, message: string) =>
      new Promise<boolean>((resolve) =>
        modals.openConfirmModal({
          title,
          children: <Text>{message}</Text>,
          labels: { confirm: 'Confirm', cancel: 'Cancel' },
          onConfirm: () => {
            resolve(true)
          },
          onCancel: () => {
            resolve(false)
          },
        })
      ),
    []
  )
}

function useShowErrorModal() {
  return useCallback((error: unknown) => {
    modals.open({
      title: 'Oops… something went wrong.',
      children: (
        <Stack>
          <ErrorAlert error={error} />
          <Text size="lg">Please check the console for detail.</Text>
        </Stack>
      ),
    })
  }, [])
}

export { useShowConfirmationModal, useShowErrorModal }
