import { AppShell, ScrollArea } from '@mantine/core'
import {
  IconBooks,
  IconCategory,
  IconCategoryPlus,
  IconHome,
  IconPlus,
  IconSettings,
} from '@tabler/icons-react'

import { CollapsibleNavLink, RouterNavLink } from '@/components/common/NavLink'
import modelConfigApi from '@/services/model-config'
import projectApi from '@/services/project'

import ModelConfigLink from './ModelConfigLink'
import ProjectLink from './ProjectLink'

const OFFSET = 16

function Navbar() {
  const { data: projectsData } = projectApi.useGetProjectsQuery()
  const { data: modelConfigsData } = modelConfigApi.useGetModelConfigsQuery()

  const projectLinks = projectsData?.data.map((project) => (
    <ProjectLink project={project} key={project.id} />
  ))

  const modelConfigLinks = modelConfigsData?.data.map((config) => (
    <ModelConfigLink modelConfig={config} key={config.id} />
  ))

  return (
    <>
      <ScrollArea>
        <RouterNavLink label="Home" icon={IconHome} to="/" />
        <CollapsibleNavLink
          childrenOffset={OFFSET}
          icon={IconBooks}
          label="Gamebooks"
          matchRoute={['/gamebook/*', '/player/new/*']}
        >
          <RouterNavLink label="New Gamebook" icon={IconPlus} to="/gamebook/new" />
          {projectLinks}
        </CollapsibleNavLink>
        <CollapsibleNavLink
          childrenOffset={OFFSET}
          icon={IconCategory}
          label="Models"
          matchRoute="/model-config/*"
        >
          <RouterNavLink label="New Model" icon={IconCategoryPlus} to="/model-config/new" />
          {modelConfigLinks}
        </CollapsibleNavLink>
      </ScrollArea>
      <AppShell.Section grow />
      <RouterNavLink label="Settings" icon={IconSettings} to="/settings" />
    </>
  )
}

export default Navbar
