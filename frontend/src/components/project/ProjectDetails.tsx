import { Alert, Button, Group, Text } from '@mantine/core'
import { IconBook, IconCategoryPlus, IconInfoCircle, IconPlayerPlay } from '@tabler/icons-react'
import { useState } from 'react'
import { Link, useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import PageShell from '@/components/layout/PageShell'
import ModelConfigSelector from '@/components/model-config/ModelConfigSelector'
import ProjectCard from '@/components/project/ProjectCard'
import { useCreateSession } from '@/hooks/session'
import { url } from '@/routes'
import modelConfigApi from '@/services/model-config'
import projectApi from '@/services/project'
import { iconSizeProps } from '@/utils'
import type { ProjectDetail } from '@/types/api'
import type { RouteParams } from '@/types/routes'

import classes from './ProjectDetails.module.css'

interface ProjectDetailsDisplayProps {
  project: ProjectDetail
}

function ProjectDetailsDisplay({ project }: ProjectDetailsDisplayProps) {
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
            void createSession(project.id, modelConfigId)
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
    <PageShell
      footer={footer}
      icon={IconBook}
      title={project.title}
      topBarRightSection={modelSelector}
    >
      <ProjectCard project={project} />
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
            to={url('model-config.new')}
            variant="filled"
          >
            Configure Model
          </Button>
        </Alert>
      )}
    </PageShell>
  )
}

function ProjectDetails() {
  const { namespace, name } = useParams<RouteParams<'gamebook.view'>>()
  const projectResult = projectApi.useGetProjectByIdQuery(`${namespace}/${name}`)

  return (
    <QueryHandler
      notFoundMessage="Gamebook not found"
      notFoundTitle="Not Found"
      result={projectResult}
    >
      {(project) => <ProjectDetailsDisplay project={project} />}
    </QueryHandler>
  )
}

export default ProjectDetails
