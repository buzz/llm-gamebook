import { Alert, Button, SimpleGrid, Text } from '@mantine/core'
import { IconBooks, IconInfoCircle, IconPlus } from '@tabler/icons-react'
import { Link } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import PageShell from '@/components/layout/PageShell'
import ProjectCard from '@/components/project/ProjectCard'
import { url } from '@/routes'
import projectApi from '@/services/project'
import type { Projects } from '@/types/api'

interface ProjectListDisplayProps {
  data: Projects
}

function ProjectListDisplay({ data }: ProjectListDisplayProps) {
  if (data.count === 0) {
    return (
      <Alert icon={<IconInfoCircle />} mb="md">
        <Text>No projects to display…</Text>
      </Alert>
    )
  }

  const count = (
    <Text c="dimmed">
      Showing {data.count} gamebook{data.count !== 1 && 's'}
    </Text>
  )

  const createButton = (
    <Button component={Link} leftSection={<IconPlus />} to={url('gamebook.new')} variant="light">
      Create Gamebook
    </Button>
  )

  return (
    <PageShell
      fluid
      icon={IconBooks}
      title="Gamebooks"
      topBarMiddleSection={count}
      topBarRightSection={createButton}
    >
      <SimpleGrid cols={{ base: 1, '40em': 2, '60em': 3, '80em': 4, '100em': 5 }} type="container">
        {data.data.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </SimpleGrid>
    </PageShell>
  )
}

function ProjectList() {
  const projectsResult = projectApi.useGetProjectsQuery()
  return (
    <QueryHandler
      notFoundMessage="No projects found"
      notFoundTitle="No Projects"
      result={projectsResult}
    >
      {(data) => <ProjectListDisplay data={data} />}
    </QueryHandler>
  )
}

export default ProjectList
