import {
  assertNever,
  isApiQueryError,
  isApiValidationError,
  isWebsocketError,
} from './types/typeguards'
import type { ProjectBasic } from './types/api'
import type { ErrorDisplay, IconSize } from './types/common'

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

function standardizeErrorMessage(error: unknown): ErrorDisplay {
  const errorDisp: ErrorDisplay = {
    name: 'Unknown Error',
    message: null,
    details: null,
  }

  if (isApiQueryError(error)) {
    if (isApiValidationError(error)) {
      errorDisp.name = `${String(error.status)} Validation Error`
      if (error.data.detail !== undefined) {
        errorDisp.details = JSON.stringify(error.data.detail, undefined, 2)
      }
    } else {
      errorDisp.name = `${String(error.status)} Query Error`
    }
  } else if (isWebsocketError(error)) {
    errorDisp.name = error.name
    errorDisp.message = error.message
    if (error.sessionId !== null) {
      errorDisp.details = `sessionId: ${error.sessionId}`
    }
  } else if (error instanceof Error) {
    errorDisp.name = error.name
    errorDisp.message = error.message
    if (error.stack) {
      errorDisp.details = error.stack
    }
  }

  return errorDisp
}

export { iconSizeProps, projectImageSrc, splitProjectId, standardizeErrorMessage }
