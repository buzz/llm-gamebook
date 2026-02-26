import type { ComponentType } from 'react'

import Editor from './components/editor/Editor'
import ModelConfigForm from './components/model-config/ModelConfigForm'
import Player from './components/player'
import NewStory from './components/player/NewStory'
import ProjectDetails from './components/project/ProjectDetails'
import ProjectForm from './components/project/ProjectForm'
import ProjectList from './components/project/ProjectList'
import Settings from './components/settings/Settings'
import { KEBAB_CASE_PATTERN, UUID_PATTERN } from './constants'

const re = (pattern: string) => new RegExp(`^${pattern}$`)
const PROJECT_ID = `(?<namespace>${KEBAB_CASE_PATTERN})/(?<name>${KEBAB_CASE_PATTERN})`
const MODEL_CONFIG_ID = `(?<modelConfigId>${UUID_PATTERN})`

interface RouteDef {
  path: string | RegExp
  component: ComponentType
}

const routes: RouteDef[] = [
  {
    path: '/',
    component: ProjectList,
  },
  {
    path: '/gamebook/new',
    component: ProjectForm,
  },
  {
    path: re(`/gamebook/${PROJECT_ID}`),
    component: ProjectDetails,
  },
  {
    path: '/editor',
    component: () => 'Editor',
  },
  {
    path: '/model-config/new',
    component: ModelConfigForm,
  },
  {
    path: re(`/model-config/${MODEL_CONFIG_ID}`),
    component: ModelConfigForm,
  },
  {
    path: re(`/editor/${PROJECT_ID}`),
    component: Editor,
  },
  {
    path: re(`/player/new/${PROJECT_ID}`),
    component: NewStory,
  },
  {
    path: re(`/player/${PROJECT_ID}`),
    component: Player,
  },
  {
    path: '/settings',
    component: Settings,
  },
] as const

export default routes
