import { Group, Select, Skeleton } from '@mantine/core'

import modelConfigApi from '@/services/modelConfig'

function ModelConfigSelector({
  selectedModelConfigId,
  onModelConfigChange: onConfigChange,
  disabled,
}: ModelConfigSelectorProps) {
  const { data: configsData, isLoading: isLoadingConfigs } =
    modelConfigApi.useGetModelConfigsQuery()
  const { data: providers, isLoading: isLoadingProviders } = modelConfigApi.useGetProvidersQuery()
  const configs = configsData?.data ?? []
  const isLoading = isLoadingConfigs || isLoadingProviders
  const noConfigs = configs.length === 0

  const selectData =
    configsData && providers
      ? configs.map(({ id, name, provider }) => {
          const providerLabel = providers[provider].label
          return {
            value: id,
            label: name + (providerLabel ? ` (${providerLabel})` : ''),
          }
        })
      : []

  if (isLoading || !providers) {
    return <Skeleton height={36} width={200} />
  }

  return (
    <Group gap="xs">
      <Select
        data={selectData}
        disabled={disabled ?? noConfigs}
        onChange={(value) => {
          if (value) {
            onConfigChange(value)
          }
        }}
        placeholder={noConfigs ? 'No model…' : undefined}
        searchable
        size="sm"
        styles={{
          input: {
            minWidth: 180,
          },
        }}
        value={selectedModelConfigId}
      />
    </Group>
  )
}

interface ModelConfigSelectorProps {
  selectedModelConfigId: string | null
  onModelConfigChange: (configId: string) => void
  disabled?: boolean
}

export default ModelConfigSelector
