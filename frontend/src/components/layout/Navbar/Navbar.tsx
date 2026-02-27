import { AppShell, ScrollArea } from '@mantine/core'
import {
  IconBooks,
  IconCategory,
  IconCategoryPlus,
  IconHome,
  IconPlus,
  IconSettings,
} from '@tabler/icons-react'
import { ErrorBoundary } from 'react-error-boundary'

import ErrorAlert from '@/components/common/ErrorAlert'
import { CollapsibleNavLink, RouterNavLink } from '@/components/common/NavLink'
import { url } from '@/routes'
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
    <ErrorBoundary FallbackComponent={ErrorAlert}>
      <ScrollArea>
        <RouterNavLink label="Home" icon={IconHome} to={url('home')} />
        <CollapsibleNavLink childrenOffset={OFFSET} icon={IconBooks} label="Gamebooks">
          <RouterNavLink label="New Gamebook" icon={IconPlus} to={url('gamebook.new')} />
          {projectLinks}
        </CollapsibleNavLink>
        <CollapsibleNavLink childrenOffset={OFFSET} icon={IconCategory} label="Models">
          <RouterNavLink label="New Model" icon={IconCategoryPlus} to={url('model-config.new')} />
          {modelConfigLinks}
        </CollapsibleNavLink>
      </ScrollArea>
      <AppShell.Section grow />
      <RouterNavLink label="Settings" icon={IconSettings} to={url('settings')} />
    </ErrorBoundary>
  )
}

export default Navbar
