import { ActionIcon, Group } from '@mantine/core'
import { IconBook, IconPencil, IconTrash } from '@tabler/icons-react'
import { Link } from 'wouter'

import { RouterNavLink } from '@/components/common/NavLink'
import { useDeleteChat } from '@/hooks/chats'
import { iconSizeProps } from '@/utils'
import type { ChatListPublic } from '@/types/api'

import classes from './AppShell.module.css'

interface ActionIconsProps {
  chatId: string
}

function ActionIcons({ chatId }: ActionIconsProps) {
  const { deleteChat, isLoading } = useDeleteChat()

  return (
    <ActionIcon.Group className={classes.actionIcons}>
      <ActionIcon
        component={Link}
        aria-label="Edit"
        to={`/editor/story/${chatId}`}
        variant="default"
      >
        <IconPencil {...iconSizeProps('sm')} />
      </ActionIcon>
      <ActionIcon
        aria-label="Delete"
        loading={isLoading}
        onClick={() => void deleteChat(chatId)}
        variant="default"
      >
        <IconTrash {...iconSizeProps('sm')} />
      </ActionIcon>
    </ActionIcon.Group>
  )
}

interface StoryLinkProps {
  chat: ChatListPublic
}

function StoryLink({ chat }: StoryLinkProps) {
  return (
    <Group className={classes.storyLinkWrapper}>
      <RouterNavLink
        className={classes.storyLink}
        icon={IconBook}
        label={chat.id}
        to={`/player/story/${chat.id}`}
      />
      <ActionIcons chatId={chat.id} />
    </Group>
  )
}

export default StoryLink
