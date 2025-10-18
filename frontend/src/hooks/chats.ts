import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError } from '@/hooks/notifications'
import chatApi from '@/services/chat'

function useDeleteChat() {
  const [location, navigate] = useLocation()
  const [deleteChat, { isLoading }] = chatApi.useDeleteChatMutation()
  const showConfirmationModal = useShowConfirmationModal()
  const showError = useShowError()

  return {
    deleteChat: useCallback(
      async (chatId: string) => {
        try {
          if (
            await showConfirmationModal(
              'Delete story chat?',
              'Are you sure you want to delete this chat?'
            )
          ) {
            await deleteChat(chatId).unwrap()
            if (location === `/player/story/${chatId}`) {
              navigate('/')
            }
          }
        } catch (err) {
          showError('Failed to delete story chat!', err)
        }
      },
      [deleteChat, location, navigate, showConfirmationModal, showError]
    ),
    isLoading,
  }
}

export { useDeleteChat }
