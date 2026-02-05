import { Alert, Button, Group, Text } from '@mantine/core'
import { IconBooks, IconCategoryPlus, IconInfoCircle, IconPlayerPlay } from '@tabler/icons-react'
import { useState } from 'react'
import { Link } from 'wouter'

import StandardCard from '@/components/common/StandardCard'
import ModelConfigSelector from '@/components/modelConfig/ModelConfigSelector'
import { useCreateSession } from '@/hooks/session'
import modelConfigApi from '@/services/modelConfig'
import { iconSizeProps } from '@/utils'

function NewStory() {
  const { createSession, isLoading } = useCreateSession()

  const { data: configsData } = modelConfigApi.useGetModelConfigsQuery()
  const configs = configsData?.data ?? []

  const [modelConfigId, setModelConfigId] = useState<string | null>(null)

  if (modelConfigId && !configs.some(({ id }) => id === modelConfigId)) {
    setModelConfigId(null)
  }
  if (!modelConfigId && configs.length > 0) {
    setModelConfigId(configs[0].id)
  }

  return (
    <StandardCard
      icon={IconBooks}
      title="Start New Story"
      rightSection={
        <Group align="center">
          Model:
          <ModelConfigSelector
            selectedModelConfigId={modelConfigId}
            onModelConfigChange={setModelConfigId}
          />
        </Group>
      }
      actionButtons={
        <Button
          color="blue"
          disabled={modelConfigId === null}
          leftSection={<IconPlayerPlay {...iconSizeProps('md')} />}
          loading={isLoading}
          onClick={() => {
            if (modelConfigId) {
              void createSession(modelConfigId)
            }
          }}
          type="submit"
          variant="filled"
        >
          Start
        </Button>
      }
    >
      {configs.length === 0 ? (
        <Alert
          variant="outline"
          color="blue"
          title="Ready to get started?"
          icon={<IconInfoCircle />}
          mb="lg"
        >
          <p>You haven't set up any models yet. Create a model configuration to begin.</p>
          <Button
            component={Link}
            color="green"
            leftSection={<IconCategoryPlus {...iconSizeProps('md')} />}
            to="/model-config/new"
            variant="filled"
          >
            Configure Model
          </Button>
        </Alert>
      ) : null}
      Title:
      <Text fw={500} size="xl">
        Broken Bulb
      </Text>
    </StandardCard>
  )
}

export default NewStory
