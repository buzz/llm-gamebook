import { useParams } from 'wouter'

function ProjectDetails() {
  const { namespace, name } = useParams<{ namespace: string; name: string }>()
  const projectId = `${namespace}/${name}`

  return projectId
}

export default ProjectDetails
