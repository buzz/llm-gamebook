import { useCallback } from 'react'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError, useShowSuccess } from '@/hooks/notifications'
import url from '@/routes/url'
import projectApi from '@/services/project'
import { splitProjectId } from '@/utils'
import type { ProjectBasic, ProjectCreate } from '@/types/api'

function useCreateProject() {
  const [, navigate] = useLocation()
  const [createProject, { isLoading }] = projectApi.useCreateProjectMutation()
  const showError = useShowError()
  const showSuccess = useShowSuccess()

  return {
    createProject: useCallback(
      async (project: ProjectCreate) => {
        try {
          const createdProject = await createProject(project).unwrap()
          navigate(url('gamebook.view', splitProjectId(createdProject.id)))
          showSuccess('Gamebook was created.')
        } catch (error) {
          showError('Failed to create gamebook!', error)
        }
      },
      [createProject, navigate, showError, showSuccess]
    ),
    isLoading,
  }
}

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
                url('gamebook.view', splitProjectId(project.id)),
                url('editor.edit', splitProjectId(project.id)),
              ].includes(location)
            ) {
              navigate(url('home'))
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

export { useCreateProject, useDeleteProject }
