import { ActionIcon, Anchor, Group, Text } from '@mantine/core'
import { IconEdit, IconPlayerPlay, IconTrash, IconZoom } from '@tabler/icons-react'
import cx from 'clsx'
import { Link } from 'wouter'
import type { CardProps } from '@mantine/core'

import StandardCard from '@/components/common/StandardCard'
import ProjectSourceBadge from '@/components/project/ProjectSourceBadge'
import { useDeleteProject } from '@/hooks/project'
import { iconSizeProps, projectImageSrc } from '@/utils'
import type { ProjectBasic } from '@/types/api'

import classes from './ProjectCard.module.css'

interface ActionButtonsProps {
  enablePlayAction: boolean
  project: ProjectBasic
}

function ActionButtons({ enablePlayAction, project }: ActionButtonsProps) {
  const { deleteProject, isLoading: isDeleting } = useDeleteProject()

  return (
    <Group justify="space-between" w="100%" wrap="nowrap">
      <ProjectSourceBadge source={project.source} />
      <Group gap="xs" wrap="nowrap">
        <ActionIcon
          aria-label="Gamebook Details"
          className={classes.detailsButton}
          component={Link}
          size="lg"
          to={`/gamebook/${project.id}`}
          variant="default"
        >
          <IconZoom {...iconSizeProps('sm')} />
        </ActionIcon>
        <ActionIcon
          aria-label="Edit Gamebook"
          color="blue"
          component={Link}
          size="lg"
          to={`/editor/${project.id}`}
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
        {project.source === 'local' && <></>}
        {enablePlayAction && (
          <ActionIcon
            aria-label="Play"
            color="teal"
            component={Link}
            size="lg"
            to={`/player/new/${project.id}`}
          >
            <IconPlayerPlay {...iconSizeProps('sm')} />
          </ActionIcon>
        )}
      </Group>
    </Group>
  )
}

interface ProjectCardProps extends CardProps {
  enablePlayAction?: boolean
  project: ProjectBasic
}

function ProjectCard({ enablePlayAction = false, project, ...cardProps }: ProjectCardProps) {
  const imageSrc = projectImageSrc(project)
  const imageAlt = project.image ? project.title : undefined

  return (
    <StandardCard
      title={
        <Anchor
          className={cx(classes.title, classes.textShadow)}
          component={Link}
          to={`/gamebook/${project.id}`}
          truncate="end"
        >
          {project.title}
        </Anchor>
      }
      actionButtons={<ActionButtons enablePlayAction={enablePlayAction} project={project} />}
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
