import { Alert, Button, Group, Text } from '@mantine/core'
import { IconBook, IconCategoryPlus, IconInfoCircle, IconPlayerPlay } from '@tabler/icons-react'
import { useState } from 'react'
import { Link, useParams } from 'wouter'

import PageShell from '@/components/layout/PageShell'
import ModelConfigSelector from '@/components/model-config/ModelConfigSelector'
import ProjectCard from '@/components/project/ProjectCard'
import { useCreateSession } from '@/hooks/session'
import modelConfigApi from '@/services/model-config'
import projectApi from '@/services/project'
import { iconSizeProps } from '@/utils'

import classes from './NewStory.module.css'

function NewStory() {
  const { namespace, name } = useParams<{ namespace: string; name: string }>()
  const projectId = `${namespace}/${name}`

  const { createSession, isLoading } = useCreateSession()
  const { data: project } = projectApi.useGetProjectByIdQuery(projectId)
  const { data: configsData } = modelConfigApi.useGetModelConfigsQuery()
  const configs = configsData?.data ?? []

  const [modelConfigId, setModelConfigId] = useState<string | null>(null)

  if (modelConfigId && !configs.some(({ id }) => id === modelConfigId)) {
    setModelConfigId(null)
  }
  if (!modelConfigId && configs.length > 0) {
    setModelConfigId(configs[0].id)
  }

  const modelSelector = (
    <Group align="center" wrap="nowrap">
      <Text>Model:</Text>
      <ModelConfigSelector
        selectedModelConfigId={modelConfigId}
        onModelConfigChange={setModelConfigId}
      />
    </Group>
  )

  const footer = (
    <Group justify="flex-end">
      <Button
        color="teal"
        disabled={modelConfigId === null}
        leftSection={<IconPlayerPlay {...iconSizeProps('md')} />}
        loading={isLoading}
        onClick={() => {
          if (modelConfigId) {
            void createSession(projectId, modelConfigId)
          }
        }}
        size="lg"
        type="submit"
        variant="filled"
      >
        Start
      </Button>
    </Group>
  )

  return (
    <PageShell footer={footer} icon={IconBook} title="New Story" topBarRightSection={modelSelector}>
      {project && <ProjectCard project={project} />}
      {configs.length === 0 && (
        <Alert
          classNames={{ message: classes.alertMessage }}
          variant="outline"
          color="blue"
          title="Ready to get started?"
          icon={<IconInfoCircle />}
          mt="lg"
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
      )}
    </PageShell>
  )
}

export default NewStory
