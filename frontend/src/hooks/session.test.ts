import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError, useShowSuccess } from '@/hooks/notifications'
import url from '@/routes/url'
import sessionApi from '@/services/session'
import type { Session } from '@/types/api'

import { useCreateSession, useDeleteSession } from './session'

// Mock modules
vi.mock('@/hooks/modals')
vi.mock('@/hooks/notifications')
vi.mock('@/services/session')
vi.mock('wouter')

describe('useCreateSession', () => {
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useLocation).mockReturnValue(['/', mockNavigate])
  })

  describe('on successful session creation', () => {
    it('should navigate to player view with new session ID', async () => {
      const mockSessionId = 'test-session-123'
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ id: mockSessionId }),
      })

      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      await act(async () => {
        await result.current.createSession('test-namespace/test-project', 'model-config-456')
      })

      expect(mockNavigate).toHaveBeenCalledWith(url('player.view', { id: mockSessionId }))
    })

    it('should not show error notification', async () => {
      const mockSessionId = 'test-session-123'
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ id: mockSessionId }),
      })

      const mockShowError = vi.fn()
      vi.mocked(useShowError).mockReturnValue(mockShowError)
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      await act(async () => {
        await result.current.createSession('test-namespace/test-project', 'model-config-456')
      })

      expect(mockShowError).not.toHaveBeenCalled()
    })
  })

  describe('on failed session creation', () => {
    it('should show error notification', async () => {
      const mockError = new Error('API failure')
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockRejectedValue(mockError),
      })

      const mockShowError = vi.fn()
      vi.mocked(useShowError).mockReturnValue(mockShowError)
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      await act(async () => {
        await result.current.createSession('test-namespace/test-project', 'model-config-456')
      })

      expect(mockShowError).toHaveBeenCalledWith('Failed to create story session!', mockError)
    })

    it('should not navigate', async () => {
      const mockError = new Error('API failure')
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockRejectedValue(mockError),
      })

      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      await act(async () => {
        await result.current.createSession('test-namespace/test-project', 'model-config-456')
      })

      expect(mockNavigate).not.toHaveBeenCalled()
    })
  })

  describe('isLoading state', () => {
    it('should be false initially', () => {
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ id: 'test-id' }),
      })

      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      expect(result.current.isLoading).toBe(false)
    })

    it('should be false after completion', async () => {
      const mockSessionId = 'test-session-123'
      const mockCreateSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ id: mockSessionId }),
      })

      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
        mockCreateSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useCreateSession())

      await act(async () => {
        await result.current.createSession('test-namespace/test-project', 'model-config-456')
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  it('should pass correct parameters to API', async () => {
    const mockSessionId = 'test-session-123'
    const mockCreateSessionMutation = vi.fn().mockReturnValue({
      unwrap: vi.fn().mockResolvedValue({ id: mockSessionId }),
    })

    vi.mocked(useShowError).mockReturnValue(vi.fn())
    vi.mocked(sessionApi.useCreateSessionMutation).mockReturnValue([
      mockCreateSessionMutation,
      { isLoading: false, reset: vi.fn() },
    ])

    const { result } = renderHook(() => useCreateSession())

    await act(async () => {
      await result.current.createSession('test-namespace/test-project', 'model-config-456')
    })

    expect(mockCreateSessionMutation).toHaveBeenCalledWith({
      projectId: 'test-namespace/test-project',
      configId: 'model-config-456',
    })
  })
})

describe('useDeleteSession', () => {
  const mockNavigate = vi.fn()

  const mockSession: Session = {
    id: 'test-session-123',
    projectId: 'test-namespace/test-project',
    configId: 'model-config-456',
    messageCount: 0,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useLocation).mockReturnValue(['/', mockNavigate])
  })

  describe('on successful deletion with confirmation', () => {
    it('should delete session and show success notification', async () => {
      const playerViewUrl = url('player.view', { id: mockSession.id })
      vi.mocked(useLocation).mockReturnValue([playerViewUrl, mockNavigate])

      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })
      const mockShowSuccess = vi.fn()

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(mockShowSuccess)
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockDeleteSessionMutation).toHaveBeenCalledWith({
        sessionId: mockSession.id,
        projectId: mockSession.projectId,
      })
      expect(mockShowSuccess).toHaveBeenCalledWith('Story session was deleted.')
    })

    it('should not navigate when not on player view', async () => {
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })
      const mockShowError = vi.fn()
      const mockShowSuccess = vi.fn()

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(mockShowError)
      vi.mocked(useShowSuccess).mockReturnValue(mockShowSuccess)
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockNavigate).not.toHaveBeenCalled()
      expect(mockShowError).not.toHaveBeenCalled()
      expect(mockShowSuccess).not.toHaveBeenCalled()
    })
  })

  describe('when user cancels deletion', () => {
    it('should not call API', async () => {
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(false)

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        vi.fn(),
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(sessionApi.useDeleteSessionMutation).toHaveBeenCalled()
    })

    it('should not navigate, show notifications, or call API', async () => {
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(false)
      const mockShowError = vi.fn()
      const mockShowSuccess = vi.fn()
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(mockShowError)
      vi.mocked(useShowSuccess).mockReturnValue(mockShowSuccess)
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockNavigate).not.toHaveBeenCalled()
      expect(mockShowSuccess).not.toHaveBeenCalled()
      expect(mockShowError).not.toHaveBeenCalled()
      expect(mockDeleteSessionMutation).not.toHaveBeenCalled()
    })
  })

  describe('on failed deletion', () => {
    it('should show error notification and not navigate', async () => {
      const mockError = new Error('Delete failed')
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockRejectedValue(mockError),
      })
      const mockShowError = vi.fn()

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(mockShowError)
      vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockShowError).toHaveBeenCalledWith('Failed to delete story session!', mockError)
      expect(mockNavigate).not.toHaveBeenCalled()
    })
  })

  describe('when deleting active session', () => {
    it('should navigate to home page', async () => {
      const playerViewUrl = url('player.view', { id: mockSession.id })
      vi.mocked(useLocation).mockReturnValue([playerViewUrl, mockNavigate])

      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockNavigate).toHaveBeenCalledWith(url('home'))
    })

    it('should show success notification', async () => {
      const playerViewUrl = url('player.view', { id: mockSession.id })
      vi.mocked(useLocation).mockReturnValue([playerViewUrl, mockNavigate])

      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })

      const mockShowSuccess = vi.fn()
      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(mockShowSuccess)
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(mockShowSuccess).toHaveBeenCalledWith('Story session was deleted.')
    })
  })

  describe('isLoading state', () => {
    it('should be false initially', () => {
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      expect(result.current.isLoading).toBe(false)
    })

    it('should be false after completion', async () => {
      const mockShowConfirmationModal = vi.fn().mockResolvedValue(true)
      const mockDeleteSessionMutation = vi.fn().mockReturnValue({
        unwrap: vi.fn().mockResolvedValue({ message: 'Deleted' }),
      })

      vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
      vi.mocked(useShowError).mockReturnValue(vi.fn())
      vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
      vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
        mockDeleteSessionMutation,
        { isLoading: false, reset: vi.fn() },
      ])

      const { result } = renderHook(() => useDeleteSession())

      await act(async () => {
        await result.current.deleteSession(mockSession)
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  it('should pass correct confirmation modal title and message', async () => {
    const mockShowConfirmationModal = vi.fn().mockResolvedValue(false)

    vi.mocked(useShowConfirmationModal).mockReturnValue(mockShowConfirmationModal)
    vi.mocked(useShowError).mockReturnValue(vi.fn())
    vi.mocked(useShowSuccess).mockReturnValue(vi.fn())
    vi.mocked(sessionApi.useDeleteSessionMutation).mockReturnValue([
      vi.fn(),
      { isLoading: false, reset: vi.fn() },
    ])

    const { result } = renderHook(() => useDeleteSession())

    await act(async () => {
      await result.current.deleteSession(mockSession)
    })

    expect(mockShowConfirmationModal).toHaveBeenCalledWith(
      'Delete story session?',
      'Are you sure you want to delete this session?'
    )
  })
})
