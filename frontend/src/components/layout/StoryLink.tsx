import { ActionIcon } from '@mantine/core'
import { IconBook, IconPencil, IconTrash } from '@tabler/icons-react'

import { RouterNavLink } from '@/components/common/NavLink'
import type { ChatListPublic } from '@/types/api'

import classes from './AppShell.module.css'

interface ActionIconsProps {
  chatId: string
}

function ActionIcons({ chatId }: ActionIconsProps) {
  return (
    <ActionIcon.Group className={classes.actionIcons}>
      <ActionIcon aria-label="Edit" variant="default">
        <IconPencil size={20} stroke={1.0} />
      </ActionIcon>
      <ActionIcon aria-label="Delete" variant="default">
        <IconTrash size={20} stroke={1.0} />
      </ActionIcon>
    </ActionIcon.Group>
  )
}

interface StoryLinkProps {
  chat: ChatListPublic
}

function StoryLink({ chat }: StoryLinkProps) {
  return (
    <RouterNavLink
      className={classes.storyLink}
      icon={IconBook}
      rightSection={<ActionIcons chatId={chat.id} />}
      label={chat.id}
      to={`/player/story/${chat.id}`}
    />
  )
}

export default StoryLink
