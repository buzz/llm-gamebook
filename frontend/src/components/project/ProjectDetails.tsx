import { Alert, Button, Collapse, Group, Paper, Stack, Text } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import {
  IconBook,
  IconCategoryPlus,
  IconInfoCircle,
  IconMessage2Off,
  IconPlayerPlay,
} from '@tabler/icons-react'
import { useState } from 'react'
import { Link, useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import ToggleButton from '@/components/common/ToggleButton'
import PageShell from '@/components/layout/PageShell'
import ModelConfigSelector from '@/components/model-config/ModelConfigSelector'
import { useCreateSession } from '@/hooks/session'
import { url } from '@/routes'
import modelConfigApi from '@/services/model-config'
import projectApi from '@/services/project'
import sessionApi from '@/services/session'
import { iconSizeProps } from '@/utils'
import type { ProjectDetail } from '@/types/api'
import type { RouteParams } from '@/types/routes'

import ProjectCard from './ProjectCard'
import classes from './ProjectDetails.module.css'
import SessionList from './SessionList'

interface ProjectDetailsDisplayProps {
  project: ProjectDetail
}

function ProjectDetailsDisplay({ project }: ProjectDetailsDisplayProps) {
  const { createSession, isLoading } = useCreateSession()
  const { data: configsData } = modelConfigApi.useGetModelConfigsQuery()
  const configs = configsData?.data ?? []
  const sessionsResult = sessionApi.useGetSessionsQuery({ project_id: project.id })

  const [modelConfigId, setModelConfigId] = useState<string | null>(null)
  const [sessionListOpened, sessionListHandlers] = useDisclosure(true)

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

  const sessionList = (
    <Paper bg="dark.6" p="sm">
      <QueryHandler result={sessionsResult}>
        {(sessions) =>
          sessions.count > 0 ? (
            <Stack>
              <ToggleButton opened={sessionListOpened} onClick={sessionListHandlers.toggle}>
                {sessions.count} Session{sessions.count === 1 ? '' : 's'}
              </ToggleButton>
              <Collapse in={sessionListOpened}>
                <SessionList sessions={sessions.data} />
              </Collapse>
            </Stack>
          ) : (
            <Group>
              <IconMessage2Off {...iconSizeProps('md')} />
              <Text c="dimmed" fz="lg">
                No sessions…
              </Text>
            </Group>
          )
        }
      </QueryHandler>
    </Paper>
  )

  const startButton = (
    <Button
      color="teal"
      disabled={modelConfigId === null}
      fullWidth
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
  )

  return (
    <PageShell icon={IconBook} title={project.title} topBarRightSection={modelSelector}>
      <Stack>
        <ProjectCard project={project} />

        {configs.length === 0 ? (
          <Alert
            classNames={{ message: classes.alertMessage }}
            variant="outline"
            color="blue"
            title="Ready to get started?"
            icon={<IconInfoCircle />}
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
        ) : (
          startButton
        )}

        {sessionList}
      </Stack>
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
