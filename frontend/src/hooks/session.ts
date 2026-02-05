import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError } from '@/hooks/notifications'
import sessionApi from '@/services/session'

function useCreateSession() {
  const [_location, navigate] = useLocation()
  const [createSession, { isLoading }] = sessionApi.useCreateSessionMutation()
  const showError = useShowError()

  return {
    createSession: useCallback(async () => {
      try {
        const { id } = await createSession().unwrap()
        navigate(`/player/${id}`)
      } catch (error) {
        showError('Failed to create story session!', error)
      }
    }, [createSession, navigate, showError]),
    isLoading,
  }
}

function useDeleteSession() {
  const [location, navigate] = useLocation()
  const [deleteSession, { isLoading }] = sessionApi.useDeleteSessionMutation()
  const showConfirmationModal = useShowConfirmationModal()
  const showError = useShowError()

  return {
    deleteSession: useCallback(
      async (sessionId: string) => {
        try {
          if (
            await showConfirmationModal(
              'Delete story session?',
              'Are you sure you want to delete this session?'
            )
          ) {
            await deleteSession(sessionId).unwrap()
            if (location === `/player/${sessionId}`) {
              navigate('/')
            }
          }
        } catch (error) {
          showError('Failed to delete story session!', error)
        }
      },
      [deleteSession, location, navigate, showConfirmationModal, showError]
    ),
    isLoading,
  }
}

export { useCreateSession, useDeleteSession }
