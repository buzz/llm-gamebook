import { ActionIcon, Group } from '@mantine/core'
import { IconBook, IconPencil, IconTrash } from '@tabler/icons-react'
import { Link } from 'wouter'

import { RouterNavLink } from '@/components/common/NavLink'
import { useDeleteSession } from '@/hooks/session'
import { iconSizeProps } from '@/utils'
import type { Session } from '@/types/api'

import classes from './AppShell.module.css'

interface ActionIconsProperties {
  sessionId: string
}

function ActionIcons({ sessionId }: ActionIconsProperties) {
  const { deleteSession, isLoading } = useDeleteSession()

  return (
    <ActionIcon.Group className={classes.actionIcons}>
      <ActionIcon
        component={Link}
        aria-label="Edit"
        to={`/editor/story/${sessionId}`}
        variant="default"
      >
        <IconPencil {...iconSizeProps('sm')} />
      </ActionIcon>
      <ActionIcon
        aria-label="Delete"
        loading={isLoading}
        onClick={() => void deleteSession(sessionId)}
        variant="default"
      >
        <IconTrash {...iconSizeProps('sm')} />
      </ActionIcon>
    </ActionIcon.Group>
  )
}

interface StoryLinkProperties {
  session: Session
}

function StoryLink({ session }: StoryLinkProperties) {
  return (
    <Group className={classes.storyLinkWrapper}>
      <RouterNavLink
        className={classes.storyLink}
        icon={IconBook}
        label={session.id}
        to={`/player/${session.id}`}
      />
      <ActionIcons sessionId={session.id} />
    </Group>
  )
}

export default StoryLink
