import { describe, expect, it } from 'vitest'

import { iconSizeProps, projectImageSrc, splitProjectId, standardizeErrorMessage } from './utils'
import type { ApiQueryError, ApiValidationError, ProjectBasic } from './types/api'
import type { WebSocketErrorMessage } from './types/websocket'

describe('splitProjectId', () => {
  it('should split valid project ID with namespace and name', () => {
    const result = splitProjectId('foo/bar')
    expect(result).toEqual({ namespace: 'foo', name: 'bar' })
  })

  it('should split project ID with hyphens and underscores', () => {
    const result = splitProjectId('my-namespace/my_project')
    expect(result).toEqual({ namespace: 'my-namespace', name: 'my_project' })
  })

  it('should throw error for missing namespace', () => {
    expect(() => splitProjectId('/name')).toThrow(
      'Invalid project ID format: /name. Expected "namespace/name"'
    )
  })

  it('should throw error for multiple slashes', () => {
    expect(() => splitProjectId('namespace/name/extra')).toThrow(
      'Invalid project ID format: namespace/name/extra. Expected "namespace/name"'
    )
  })

  it('should throw error for missing name', () => {
    expect(() => splitProjectId('namespace/')).toThrow(
      'Invalid project ID format: namespace/. Expected "namespace/name"'
    )
  })

  it('should throw error for empty string', () => {
    expect(() => splitProjectId('')).toThrow(
      'Invalid project ID format: . Expected "namespace/name"'
    )
  })

  it('should throw error for string without slash', () => {
    expect(() => splitProjectId('invalid')).toThrow(
      'Invalid project ID format: invalid. Expected "namespace/name"'
    )
  })
})

describe('standardizeErrorMessage', () => {
  it('should handle ApiValidationError with array details', () => {
    const error: ApiValidationError = {
      status: 422,
      data: {
        detail: [
          { loc: ['body', 'name'], msg: 'Field required', type: 'missing' },
          { loc: ['body', 'email'], msg: 'Invalid email', type: 'value_error' },
        ],
      },
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('422 Validation Error')
    expect(result.message).toBeNull()
    expect(result.details).toBe(JSON.stringify(error.data.detail, undefined, 2))
  })

  it('should handle ApiValidationError with empty array details', () => {
    const error: ApiValidationError = {
      status: 422,
      data: {
        detail: [],
      },
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('422 Validation Error')
    expect(result.message).toBeNull()
    expect(result.details).toBe('[]')
  })

  it('should handle ApiValidationError with single validation error', () => {
    const error: ApiValidationError = {
      status: 422,
      data: {
        detail: [{ loc: ['body', 'name'], msg: 'Field required', type: 'missing' }],
      },
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('422 Validation Error')
    expect(result.message).toBeNull()
    expect(result.details).toBe(JSON.stringify(error.data.detail, undefined, 2))
  })

  it('should handle ApiQueryError without validation details', () => {
    const error: ApiQueryError = {
      status: 404,
      data: {
        detail: 'Not found',
      },
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('404 Query Error')
    expect(result.message).toBeNull()
    expect(result.details).toBeNull()
  })

  it('should handle WebSocket error with session ID', () => {
    const error: WebSocketErrorMessage = {
      kind: 'error',
      name: 'ConnectionError',
      message: 'WebSocket connection lost',
      sessionId: 'abc-123-def',
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('ConnectionError')
    expect(result.message).toBe('WebSocket connection lost')
    expect(result.details).toBe('sessionId: abc-123-def')
  })

  it('should handle WebSocket error without session ID', () => {
    const error: WebSocketErrorMessage = {
      kind: 'error',
      name: 'TimeoutError',
      message: 'Connection timed out',
      sessionId: null,
    }
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('TimeoutError')
    expect(result.message).toBe('Connection timed out')
    expect(result.details).toBeNull()
  })

  it('should handle regular Error with stack trace', () => {
    const error = new Error('Something went wrong')
    error.name = 'CustomError'
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('CustomError')
    expect(result.message).toBe('Something went wrong')
    expect(result.details).toContain('CustomError: Something went wrong')
  })

  it('should handle regular Error without stack trace', () => {
    const error = new Error('Simple error')
    error.stack = undefined
    const result = standardizeErrorMessage(error)
    expect(result.name).toBe('Error')
    expect(result.message).toBe('Simple error')
    expect(result.details).toBeNull()
  })

  it('should handle null error', () => {
    const result = standardizeErrorMessage(null as unknown)
    expect(result.name).toBe('Unknown Error')
    expect(result.message).toBeNull()
    expect(result.details).toBeNull()
  })

  it('should handle undefined error', () => {
    const result = standardizeErrorMessage(undefined as unknown)
    expect(result.name).toBe('Unknown Error')
    expect(result.message).toBeNull()
    expect(result.details).toBeNull()
  })

  it('should handle primitive error values', () => {
    const resultString = standardizeErrorMessage('string error')
    expect(resultString.name).toBe('Unknown Error')
    expect(resultString.message).toBeNull()

    const resultNumber = standardizeErrorMessage(42)
    expect(resultNumber.name).toBe('Unknown Error')
    expect(resultNumber.message).toBeNull()

    const resultBoolean = standardizeErrorMessage(true)
    expect(resultBoolean.name).toBe('Unknown Error')
    expect(resultBoolean.message).toBeNull()
  })

  it('should handle empty object error', () => {
    const result = standardizeErrorMessage({})
    expect(result.name).toBe('Unknown Error')
    expect(result.message).toBeNull()
    expect(result.details).toBeNull()
  })
})

describe('iconSizeProps', () => {
  it('should return correct props for lg size', () => {
    const result = iconSizeProps('lg')
    expect(result).toEqual({ size: 32, stroke: 1.1 })
  })

  it('should return correct props for md size', () => {
    const result = iconSizeProps('md')
    expect(result).toEqual({ size: 24, stroke: 1.4 })
  })

  it('should return correct props for sm size', () => {
    const result = iconSizeProps('sm')
    expect(result).toEqual({ size: 20, stroke: 1.5 })
  })
})

describe('projectImageSrc', () => {
  it('should return image URL when project has image', () => {
    const project: ProjectBasic = {
      id: 'namespace/name',
      source: 'local',
      title: 'Test Project',
      description: 'A test project',
      image: '/uploaded/image.jpg',
    }
    const result = projectImageSrc(project)
    expect(result).toBe('/api/projects/namespace/name/image')
  })

  it('should return undefined when project has no image', () => {
    const project: ProjectBasic = {
      id: 'namespace/name',
      source: 'local',
      title: 'Test Project',
      description: 'A test project',
    }
    const result = projectImageSrc(project)
    expect(result).toBeUndefined()
  })
})
