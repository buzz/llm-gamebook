import { Button } from '@mantine/core'
import { IconBook, IconEdit } from '@tabler/icons-react'
import { Link, useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import PageShell from '@/components/layout/PageShell'
import { url } from '@/routes'
import projectApi from '@/services/project'
import { splitProjectId } from '@/utils'
import type { ProjectDetail } from '@/types/api'
import type { RouteParams } from '@/types/routes'

interface ProjectDetailsDisplayProps {
  project: ProjectDetail
}

function ProjectDetailsDisplay({ project }: ProjectDetailsDisplayProps) {
  return (
    <PageShell icon={IconBook} title={project.title}>
      <Button
        component={Link}
        leftSection={<IconEdit />}
        to={url('editor.edit', splitProjectId(project.id))}
        variant="light"
      >
        Edit
      </Button>
    </PageShell>
  )
}

function ProjectDetails() {
  const { namespace, name } = useParams<RouteParams<'gamebook.view'>>()
  const projectResult = projectApi.useGetProjectByIdQuery(`${namespace}/${name}`)

  return (
    <QueryHandler
      notFoundMessage="Project not found"
      notFoundTitle="Project Not Found"
      result={projectResult}
    >
      {(project) => <ProjectDetailsDisplay project={project} />}
    </QueryHandler>
  )
}

export default ProjectDetails
