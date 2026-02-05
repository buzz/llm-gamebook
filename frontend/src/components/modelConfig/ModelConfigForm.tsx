import {
  Button,
  Collapse,
  Group,
  Paper,
  PasswordInput,
  Select,
  Stack,
  Switch,
  TextInput,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks'
import { skipToken } from '@reduxjs/toolkit/query'
import { IconCategoryPlus, IconDeviceFloppy, IconPlus, IconTrash } from '@tabler/icons-react'
import { useEffect } from 'react'
import { useParams } from 'wouter'

import InputSlider from '@/components/common/InputSlider'
import StandardCard from '@/components/common/StandardCard'
import {
  useCreateModelConfig,
  useDeleteModelConfig,
  useUpdateModelConfig,
} from '@/hooks/modelConfig'
import modelConfigApi from '@/services/modelConfig'
import { iconSizeProps } from '@/utils'
import type { ModelProvider } from '@/types/api'

const EMPTY_FORM = {
  name: '',
  provider: 'openai-compatible',
  modelId: '',
  baseUrl: '',
  apiKey: '',
  contextWindow: 32_768,
  maxTokens: 2000,
  temperature: 1,
  topP: 0.95,
  presencePenalty: 0,
  frequencyPenalty: 0,
} satisfies ConfigFormData

interface ConfigFormData {
  name: string
  provider: ModelProvider
  modelId: string
  baseUrl: string
  apiKey: string
  contextWindow: number
  maxTokens: number
  temperature: number
  topP: number
  presencePenalty: number
  frequencyPenalty: number
}

function ModelConfigForm() {
  const { modelConfigId } = useParams()
  const isEditing = modelConfigId !== undefined

  const [advancedOpened, advancedHandlers] = useDisclosure(false)

  const { data: modelConfig, isLoading: isLoadingConfig } = modelConfigApi.useGetModelConfigQuery(
    isEditing ? modelConfigId : skipToken
  )
  const { createModelConfig, isLoading: isCreating } = useCreateModelConfig()
  const { updateModelConfig, isLoading: isUpdating } = useUpdateModelConfig()
  const { deleteModelConfig, isLoading: isDeleting } = useDeleteModelConfig()

  const { data: providers, isLoading: isLoadingProviders } = modelConfigApi.useGetProvidersQuery()

  const isLoading = isLoadingConfig || isCreating || isUpdating || isDeleting || isLoadingProviders

  const form = useForm<ConfigFormData>({
    initialValues: EMPTY_FORM,
    validate: {
      name: (value) => (value.length === 0 ? 'Name is required' : null),
      provider: (value) => (value.length === 0 ? 'Provider is required' : null),
      modelId: (value) => (value.length === 0 ? 'Model ID is required' : null),
    },
  })
  const formValues = form.getValues()

  // Avoid passing form to deps as it's unstable
  const { reset, setFieldValue, setValues } = form

  useEffect(() => {
    if (isEditing && modelConfig) {
      setValues({
        name: modelConfig.name,
        provider: modelConfig.provider,
        modelId: modelConfig.model_name,
        baseUrl: modelConfig.base_url ?? undefined,
        apiKey: modelConfig.api_key ?? undefined,
        contextWindow: modelConfig.context_window,
        maxTokens: modelConfig.max_tokens,
        temperature: modelConfig.temperature,
        topP: modelConfig.top_p,
        presencePenalty: modelConfig.presence_penalty,
        frequencyPenalty: modelConfig.frequency_penalty,
      })
    } else {
      reset()
    }
  }, [isEditing, modelConfig, setValues, reset])

  const handleSubmit = form.onSubmit(async () => {
    if (isLoading) {
      return
    }

    const config = {
      name: formValues.name,
      provider: formValues.provider,
      modelId: formValues.modelId,
      baseUrl: formValues.baseUrl,
      apiKey: formValues.apiKey,
      contextWindow: formValues.contextWindow,
      maxTokens: formValues.maxTokens,
      temperature: formValues.temperature,
      topP: formValues.topP,
      presencePenalty: formValues.presencePenalty,
      frequencyPenalty: formValues.frequencyPenalty,
    }

    await (isEditing && modelConfig
      ? updateModelConfig(modelConfig.id, config)
      : createModelConfig(config))
  })

  const providerSelectData = providers
    ? Object.entries(providers).map(([value, info]) => ({
        value,
        label: info.label,
      }))
    : []

  const { provider } = formValues
  const providerInfo = providers ? providers[provider] : undefined
  const baseUrlPlaceHolder = providerInfo?.supports_base_url
    ? providerInfo.default_base_url
    : undefined

  function handleProviderChange(newProvider: ModelProvider) {
    const newProviderInfo = providers ? providers[newProvider] : undefined
    if (newProviderInfo && !newProviderInfo.supports_base_url) {
      setFieldValue('baseUrl', newProviderInfo.default_base_url ?? '')
    }
  }

  function resetAdvanced() {
    form.setFieldValue('maxTokens', EMPTY_FORM.maxTokens)
    form.setFieldValue('temperature', EMPTY_FORM.temperature)
    form.setFieldValue('topP', EMPTY_FORM.topP)
    form.setFieldValue('presencePenalty', EMPTY_FORM.presencePenalty)
    form.setFieldValue('frequencyPenalty', EMPTY_FORM.frequencyPenalty)
  }

  return (
    <form aria-disabled={isLoading} onSubmit={handleSubmit}>
      <StandardCard
        icon={IconCategoryPlus}
        title={isEditing ? 'Update Model' : 'Create Model'}
        actionButtons={
          <>
            {isEditing ? (
              <Button
                bg="red"
                loading={isLoading}
                onClick={() => void deleteModelConfig(modelConfigId)}
                leftSection={<IconTrash {...iconSizeProps('md')} />}
              >
                Delete Model
              </Button>
            ) : null}
            <Button
              loading={isLoading}
              leftSection={
                isEditing ? (
                  <IconDeviceFloppy {...iconSizeProps('md')} />
                ) : (
                  <IconPlus {...iconSizeProps('md')} />
                )
              }
              type="submit"
            >
              {isEditing ? 'Update Model' : 'Create Model'}
            </Button>
          </>
        }
      >
        <Stack gap="md">
          <TextInput disabled={isLoading} label="Name" required {...form.getInputProps('name')} />

          <Select
            disabled={isLoading}
            label="Provider"
            placeholder="Select provider"
            data={providerSelectData}
            required
            {...form.getInputProps('provider')}
            searchable
            onChange={(value) => {
              const typedValue = value as ModelProvider
              form.setFieldValue('provider', typedValue)
              handleProviderChange(typedValue)
            }}
          />

          <TextInput
            disabled={isLoading}
            label="Model ID"
            required
            {...form.getInputProps('modelId')}
          />

          <TextInput
            disabled={isLoading}
            display={providerInfo?.supports_base_url ? 'block' : 'none'}
            label="Base URL"
            placeholder={baseUrlPlaceHolder ?? undefined}
            {...form.getInputProps('baseUrl')}
          />

          <PasswordInput
            disabled={isLoading}
            label="API Key"
            placeholder="sk-..."
            {...form.getInputProps('apiKey')}
          />

          <InputSlider
            disabled={isLoading}
            label="Context window"
            mb="sm"
            max={262_144}
            min={0}
            marks={[
              { value: 0, label: '0' },
              { value: 8192, label: '8k' },
              { value: 16_384, label: '16k' },
              { value: 32_768, label: '32k' },
              { value: 64_556, label: '64k' },
              { value: 98_304, label: '96k' },
              { value: 131_072, label: '128k' },
              { value: 163_840, label: '160k' },
              { value: 196_608, label: '192k' },
              { value: 229_376, label: '224k' },
              { value: 262_144, label: '256k' },
            ]}
            onChange={(value) => {
              form.setFieldValue('contextWindow', value)
            }}
            snapToMarks
            value={formValues.contextWindow}
          />

          <Paper p="sm">
            <Stack>
              <Group justify="space-between">
                <Switch
                  color="gray"
                  checked={advancedOpened}
                  label="Advanced settings"
                  onChange={(event) => {
                    if (event.currentTarget.checked) {
                      advancedHandlers.open()
                    } else {
                      advancedHandlers.close()
                    }
                  }}
                  ps="xs"
                  withThumbIndicator={false}
                />
                <Button onClick={resetAdvanced} variant="subtle">
                  Reset values
                </Button>
              </Group>

              <Collapse in={advancedOpened} pb="xs">
                <Stack>
                  <InputSlider
                    description="The maximum number of tokens to generate before stopping."
                    disabled={isLoading}
                    display={providerInfo?.supports_max_tokens ? 'block' : 'none'}
                    label="Max. tokens"
                    max={50_000}
                    min={0}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 5000, label: '5,000' },
                      { value: 10_000, label: '10,000' },
                      { value: 20_000, label: '20,000' },
                      { value: 30_000, label: '30,000' },
                      { value: 40_000, label: '40,000' },
                      { value: 50_000, label: '50,000' },
                    ]}
                    onChange={(value) => {
                      form.setFieldValue('maxTokens', value)
                    }}
                    snapToMarks
                    value={formValues.maxTokens}
                  />

                  <InputSlider
                    description="Amount of randomness injected into the response."
                    disabled={isLoading}
                    display={providerInfo?.supports_temperature ? 'block' : 'none'}
                    label="Temperature"
                    min={0}
                    max={2}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 0.5, label: '0.5' },
                      { value: 1, label: '1' },
                      { value: 1.5, label: '1.5' },
                      { value: 2, label: '2' },
                    ]}
                    onChange={(value) => {
                      form.setFieldValue('temperature', value)
                    }}
                    step={0.01}
                    value={formValues.temperature}
                  />

                  <InputSlider
                    description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top-p probability mass."
                    disabled={isLoading}
                    display={providerInfo?.supports_top_p ? 'block' : 'none'}
                    label="Top-p"
                    min={0}
                    max={1}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 0.2, label: '0.2' },
                      { value: 0.4, label: '0.4' },
                      { value: 0.6, label: '0.6' },
                      { value: 0.8, label: '0.8' },
                      { value: 1, label: '1' },
                    ]}
                    onChange={(value) => {
                      form.setFieldValue('topP', value)
                    }}
                    step={0.01}
                    value={formValues.topP}
                  />

                  <InputSlider
                    description="Penalize new tokens based on whether they have appeared in the text so far."
                    disabled={isLoading}
                    display={providerInfo?.supports_presence_penalty ? 'block' : 'none'}
                    label="Presence penalty"
                    max={2}
                    min={-2}
                    marks={[
                      { value: -2, label: '-2' },
                      { value: -1, label: '-1' },
                      { value: 0, label: '0' },
                      { value: 1, label: '1' },
                      { value: 2, label: '2' },
                    ]}
                    onChange={(value) => {
                      form.setFieldValue('presencePenalty', value)
                    }}
                    step={0.01}
                    value={formValues.presencePenalty}
                  />

                  <InputSlider
                    description="Penalize new tokens based on their existing frequency in the text so far."
                    disabled={isLoading}
                    display={providerInfo?.supports_frequency_penalty ? 'block' : 'none'}
                    label="Frequency penalty"
                    min={-2}
                    max={2}
                    marks={[
                      { value: -2, label: '-2' },
                      { value: -1, label: '-1' },
                      { value: 0, label: '0' },
                      { value: 1, label: '1' },
                      { value: 2, label: '2' },
                    ]}
                    onChange={(value) => {
                      form.setFieldValue('frequencyPenalty', value)
                    }}
                    step={0.01}
                    value={formValues.frequencyPenalty}
                  />
                </Stack>
              </Collapse>
            </Stack>
          </Paper>
        </Stack>
      </StandardCard>
    </form>
  )
}

export default ModelConfigForm
