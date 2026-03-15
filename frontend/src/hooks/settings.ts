import { useCallback } from 'react'

import userSettingsApi from '@/services/settings'
import type { UserSettings } from '@/types/api'

import { useShowError } from './notifications'

function useUpdateUserSettings() {
  const [updateUserSettings, { isLoading }] = userSettingsApi.useUpdateUserSettingsMutation()
  const showError = useShowError()

  return {
    updateUserSettings: useCallback(
      async (update: UserSettings) => {
        try {
          await updateUserSettings(update).unwrap()
        } catch (error) {
          showError('Failed to update user settings!', error)
        }
      },
      [showError, updateUserSettings]
    ),
    isLoading,
  }
}

export { useUpdateUserSettings }
