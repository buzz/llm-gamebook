import { Text } from '@mantine/core'
import { modals } from '@mantine/modals'
import { useCallback } from 'react'

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

export { useShowConfirmationModal }
