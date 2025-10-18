import { AppShell, ScrollArea } from '@mantine/core'
import { IconBooks, IconHome, IconSettings, IconTextPlus } from '@tabler/icons-react'

import { BasicNavLink, RouterNavLink } from '@/components/common/NavLink'
import chatApi from '@/services/chat'

import StoryLink from './StoryLink'

const OFFSET = 8

function Navbar() {
  const { data } = chatApi.useGetChatsQuery()
  const chats = data?.data ?? []
  const storyLinks = chats.map((chat) => <StoryLink chat={chat} key={chat.id} />)

  return (
    <>
      <ScrollArea>
        <RouterNavLink label="Home" icon={IconHome} to="/" />
        <BasicNavLink label="Gamebooks" icon={IconBooks} childrenOffset={OFFSET}>
          <BasicNavLink label="Broken Bulb" childrenOffset={OFFSET}>
            <RouterNavLink label="New Story" icon={IconTextPlus} to="/player/new" />
            {storyLinks}
          </BasicNavLink>
        </BasicNavLink>
      </ScrollArea>
      <AppShell.Section grow />
      <RouterNavLink label="Settings" icon={IconSettings} to="/settings" />
    </>
  )
}

export default Navbar
