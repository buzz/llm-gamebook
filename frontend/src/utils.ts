import { assertNever } from './types/typeguards'
import type { ProjectBasic } from './types/api'
import type { IconSize } from './types/common'

interface IconProps {
  size: number
  stroke: number
}

function iconSizeProps(size: IconSize): IconProps {
  switch (size) {
    case 'lg': {
      return { size: 32, stroke: 1.1 }
    }
    case 'md': {
      return { size: 24, stroke: 1.4 }
    }
    case 'sm': {
      return { size: 20, stroke: 1.5 }
    }
    default: {
      assertNever(size)
    }
  }
}

function projectImageSrc(project: ProjectBasic) {
  return project.image ? `/api/projects/${project.id}/image` : undefined
}

/**
 * Split a project ID into namespace and name
 */
function splitProjectId(projectId: string) {
  const [namespace, name] = projectId.split('/', 2)
  if (!namespace || !name) {
    throw new Error(`Invalid project ID format: ${projectId}. Expected "namespace/name"`)
  }
  return { namespace, name }
}

export { iconSizeProps, projectImageSrc, splitProjectId }
