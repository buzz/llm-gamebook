import { ActionIcon, Avatar, Group } from '@mantine/core'
import { IconBook, IconPencil, IconTrash } from '@tabler/icons-react'
import { Link } from 'wouter'

import { RouterNavLink } from '@/components/common/NavLink'
import { useDeleteProject } from '@/hooks/project'
import { iconSizeProps, projectImageSrc } from '@/utils'
import type { ProjectBasic } from '@/types/api'

import classes from './Link.module.css'

interface ActionIconsProps {
  project: ProjectBasic
}

function ActionIcons({ project }: ActionIconsProps) {
  const { deleteProject, isLoading } = useDeleteProject()

  return (
    <ActionIcon.Group className={classes.actionIcons}>
      <ActionIcon component={Link} aria-label="Edit" to={`/editor/${project.id}`} variant="default">
        <IconPencil {...iconSizeProps('sm')} />
      </ActionIcon>
      <ActionIcon
        aria-label="Delete"
        loading={isLoading}
        onClick={() => {
          void deleteProject(project)
        }}
        variant="default"
      >
        <IconTrash {...iconSizeProps('sm')} />
      </ActionIcon>
    </ActionIcon.Group>
  )
}

interface ProjectLinkProps {
  project: ProjectBasic
}

function ProjectLink({ project }: ProjectLinkProps) {
  const sizeProps = iconSizeProps('sm')

  const imageSrc = projectImageSrc(project)
  const icon = imageSrc ? (
    <Avatar size={sizeProps.size} src={imageSrc} />
  ) : (
    <Avatar color="inherit" size={sizeProps.size} src={imageSrc}>
      <IconBook {...sizeProps} />
    </Avatar>
  )

  return (
    <Group className={classes.navLinkWrapper}>
      <RouterNavLink
        className={classes.navLink}
        leftSection={icon}
        label={project.title}
        to={`/player/new/${project.id}`}
      />
      {/* <RouterNavLink
        className={classes.navLink}
        icon={IconBook}
        label={project.title}
        to={`/player/new/${project.id}`}
      /> */}
      <ActionIcons project={project} />
    </Group>
  )
}

export default ProjectLink
