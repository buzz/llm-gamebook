import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowError, useShowSuccess } from '@/hooks/notifications'
import url from '@/routes/url'
import modelConfigApi from '@/services/model-config'
import type { ModelConfigCreate, ModelConfigUpdate } from '@/types/api'

function useCreateModelConfig() {
  const [, navigate] = useLocation()
  const [createModelConfig, { isLoading }] = modelConfigApi.useCreateModelConfigMutation()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    createModelConfig: useCallback(
      async (config: ModelConfigCreate) => {
        try {
          const createdModel = await createModelConfig(config).unwrap()
          navigate(url('model-config.edit', { id: createdModel.id }))
          showSuccess('Model config was created.')
        } catch (error) {
          showError('Failed to create model config!', error)
        }
      },
      [createModelConfig, navigate, showError, showSuccess]
    ),
    isLoading,
  }
}

function useUpdateModelConfig() {
  const [updateModelConfig, { isLoading }] = modelConfigApi.useUpdateModelConfigMutation()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    updateModelConfig: useCallback(
      async (id: string, config: ModelConfigUpdate) => {
        try {
          await updateModelConfig({ id, config }).unwrap()
          showSuccess('Model config was updated.')
        } catch (error) {
          showError('Failed to update model config!', error)
        }
      },
      [updateModelConfig, showError, showSuccess]
    ),
    isLoading,
  }
}

function useDeleteModelConfig() {
  const [location, navigate] = useLocation()
  const [deleteModelConfig, { isLoading }] = modelConfigApi.useDeleteModelConfigMutation()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    deleteModelConfig: useCallback(
      async (id: string) => {
        try {
          await deleteModelConfig(id).unwrap()
          if (location === url('model-config.edit', { id })) {
            navigate(url('home'))
            showSuccess('Model config was deleted.')
          }
        } catch (error) {
          showError('Failed to delete model config!', error)
        }
      },
      [deleteModelConfig, location, navigate, showError, showSuccess]
    ),
    isLoading,
  }
}

export { useCreateModelConfig, useDeleteModelConfig, useUpdateModelConfig }
