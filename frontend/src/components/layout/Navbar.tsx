import { AppShell, ScrollArea } from '@mantine/core'
import { IconBooks, IconHome, IconSettings, IconTextPlus } from '@tabler/icons-react'

import { BasicNavLink, RouterNavLink } from '@/components/common/NavLink'
import sessionApi from '@/services/session'

import StoryLink from './StoryLink'

const OFFSET = 8

function Navbar() {
  const { data } = sessionApi.useGetSessionsQuery()
  const sessions = data?.data ?? []
  const storyLinks = sessions.map((session) => <StoryLink session={session} key={session.id} />)

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
