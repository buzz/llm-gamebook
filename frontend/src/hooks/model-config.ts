import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowError, useShowSuccess } from '@/hooks/notifications'
import { url } from '@/routes'
import modelConfigApi from '@/services/model-config'
import type { ModelProvider } from '@/types/api'

interface ModelConfigInput {
  name: string
  provider: ModelProvider
  modelId: string
  baseUrl?: string
  apiKey?: string
  contextWindow: number
  maxTokens: number
  temperature: number
  topP: number
  presencePenalty: number
  frequencyPenalty: number
}

function useCreateModelConfig() {
  const [, navigate] = useLocation()
  const [createModelConfig, { isLoading }] = modelConfigApi.useCreateModelConfigMutation()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    createModelConfig: useCallback(
      async (config: ModelConfigInput) => {
        try {
          const createdModel = await createModelConfig({
            name: config.name,
            provider: config.provider,
            model_name: config.modelId,
            base_url: config.baseUrl ?? undefined,
            api_key: config.apiKey ?? undefined,
            context_window: config.contextWindow,
            max_tokens: config.maxTokens,
            temperature: config.temperature,
            top_p: config.topP,
            presence_penalty: config.presencePenalty,
            frequency_penalty: config.frequencyPenalty,
          }).unwrap()
          navigate(url('model-config.view', { id: createdModel.id }))
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
      async (id: string, config: ModelConfigInput) => {
        try {
          await updateModelConfig({
            id,
            config: {
              name: config.name,
              provider: config.provider,
              model_name: config.modelId,
              base_url: config.baseUrl ?? undefined,
              api_key: config.apiKey ?? undefined,
              context_window: config.contextWindow,
              max_tokens: config.maxTokens,
              temperature: config.temperature,
              top_p: config.topP,
              presence_penalty: config.presencePenalty,
              frequency_penalty: config.frequencyPenalty,
            },
          }).unwrap()
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
          if (location === url('model-config.view', { id })) {
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
