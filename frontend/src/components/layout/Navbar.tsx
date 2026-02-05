import { AppShell, ScrollArea } from '@mantine/core'
import {
  IconBooks,
  IconCategory,
  IconCategoryPlus,
  IconHome,
  IconSettings,
  IconTextPlus,
} from '@tabler/icons-react'

import { BasicNavLink, RouterNavLink } from '@/components/common/NavLink'
import modelConfigApi from '@/services/modelConfig'
import sessionApi from '@/services/session'

import ModelConfigLink from './ModelConfigLink'
import StoryLink from './StoryLink'

const OFFSET = 8

function Navbar() {
  const { data: sessionsData } = sessionApi.useGetSessionsQuery()
  const sessions = sessionsData?.data ?? []
  const sessionLinks = sessions.map((session) => <StoryLink session={session} key={session.id} />)

  const { data: modelConfigsData } = modelConfigApi.useGetModelConfigsQuery()
  const modelConfigs = modelConfigsData?.data ?? []
  const modelConfigLinks = modelConfigs.map((config) => (
    <ModelConfigLink modelConfig={config} key={config.id} />
  ))

  return (
    <>
      <ScrollArea>
        <RouterNavLink label="Home" icon={IconHome} to="/" />
        <BasicNavLink label="Gamebooks" icon={IconBooks} childrenOffset={OFFSET}>
          <BasicNavLink label="Broken Bulb" childrenOffset={OFFSET}>
            <RouterNavLink label="New Story" icon={IconTextPlus} to="/player/new" />
            {sessionLinks}
          </BasicNavLink>
        </BasicNavLink>
        <BasicNavLink label="Models" icon={IconCategory} childrenOffset={OFFSET}>
          <RouterNavLink label="New Model" icon={IconCategoryPlus} to="/model-config/new" />
          {modelConfigLinks}
        </BasicNavLink>
      </ScrollArea>
      <AppShell.Section grow />
      <RouterNavLink label="Settings" icon={IconSettings} to="/settings" />
    </>
  )
}

export default Navbar
