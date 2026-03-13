import { ActionIcon, Anchor, Group, Text } from '@mantine/core'
import { IconEdit, IconTrash, IconZoom } from '@tabler/icons-react'
import cx from 'clsx'
import { Link, useLocation } from 'wouter'
import type { CardProps } from '@mantine/core'

import StandardCard from '@/components/common/StandardCard'
import ProjectSourceBadge from '@/components/project/ProjectSourceBadge'
import { useDeleteProject } from '@/hooks/project'
import { url } from '@/routes'
import { iconSizeProps, projectImageSrc, splitProjectId } from '@/utils'
import type { ProjectBasic } from '@/types/api'

import classes from './ProjectCard.module.css'

interface ActionButtonsProps {
  project: ProjectBasic
}

function ActionButtons({ project }: ActionButtonsProps) {
  const { deleteProject, isLoading: isDeleting } = useDeleteProject()
  const [location] = useLocation()

  const viewUrl = url('gamebook.view', splitProjectId(project.id))
  const enableViewLink = location !== viewUrl

  return (
    <Group justify="space-between" w="100%" wrap="nowrap">
      <ProjectSourceBadge source={project.source} />
      <Group gap="xs" wrap="nowrap">
        <ActionIcon
          aria-label="Edit Gamebook"
          color="blue"
          component={Link}
          size="lg"
          to={url('editor.edit', splitProjectId(project.id))}
        >
          <IconEdit {...iconSizeProps('sm')} />
        </ActionIcon>
        <ActionIcon
          aria-label="Delete Gamebook"
          color="red"
          loading={isDeleting}
          onClick={() => {
            void deleteProject(project)
          }}
          size="lg"
        >
          <IconTrash {...iconSizeProps('sm')} />
        </ActionIcon>
        {enableViewLink && (
          <ActionIcon
            aria-label="Gamebook Details"
            color="teal"
            component={Link}
            size="lg"
            to={viewUrl}
          >
            <IconZoom {...iconSizeProps('sm')} />
          </ActionIcon>
        )}
      </Group>
    </Group>
  )
}

interface ProjectCardProps extends CardProps {
  project: ProjectBasic
}

function ProjectCard({ project, ...cardProps }: ProjectCardProps) {
  const imageSrc = projectImageSrc(project)
  const imageAlt = project.image ? project.title : undefined

  return (
    <StandardCard
      title={
        <Anchor
          className={cx(classes.title, classes.textShadow)}
          component={Link}
          to={url('gamebook.view', splitProjectId(project.id))}
          truncate="end"
        >
          {project.title}
        </Anchor>
      }
      actionButtons={<ActionButtons project={project} />}
      imageSrc={imageSrc}
      imageAlt={imageAlt}
      shadow="lg"
      classNames={{ root: classes.cardRoot }}
      {...cardProps}
    >
      {imageSrc && (
        <div
          className={classes.blurredBackground}
          style={{ backgroundImage: `url("${imageSrc}")` }}
        ></div>
      )}
      <Text className={cx(classes.description, classes.textShadow)} lineClamp={6} size="md">
        {project.description ?? 'No description…'}
      </Text>
    </StandardCard>
  )
}

export default ProjectCard
