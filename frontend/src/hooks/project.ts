import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError, useShowSuccess } from '@/hooks/notifications'
import projectApi from '@/services/project'
import type { ProjectBasic } from '@/types/api'

function useDeleteProject() {
  const [location, navigate] = useLocation()
  const [deleteProject, { isLoading }] = projectApi.useDeleteProjectMutation()
  const showConfirmationModal = useShowConfirmationModal()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    deleteProject: useCallback(
      async (project: ProjectBasic) => {
        try {
          if (
            await showConfirmationModal(
              'Delete gamebook?',
              'Are you sure you want to delete this gamebook?'
            )
          ) {
            await deleteProject(project.id).unwrap()
            if (
              [
                `/gamebook/${project.id}`,
                `/player/new/${project.id}`,
                `/editor/${project.id}`,
              ].includes(location)
            ) {
              navigate('/')
            }
            showSuccess('Gamebook was deleted.')
          }
        } catch (error) {
          showError('Failed to delete project!', error)
        }
      },
      [deleteProject, location, navigate, showConfirmationModal, showError, showSuccess]
    ),
    isLoading,
  }
}

export { useDeleteProject }
