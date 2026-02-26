import type { ComponentType } from 'react'

import Editor from './components/editor/Editor'
import ModelConfigForm from './components/model-config/ModelConfigForm'
import Player from './components/player'
import NewStory from './components/player/NewStory'
import ProjectDetails from './components/project/ProjectDetails'
import ProjectForm from './components/project/ProjectForm'
import ProjectList from './components/project/ProjectList'
import Settings from './components/settings/Settings'

const re = (pattern: string) => new RegExp(`^${pattern}$`)
const KEBAB_CASE = '[a-z0-9]+(?:-[a-z0-9]+)*'
const UUID = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}'
const PROJECT_ID = `(?<namespace>${KEBAB_CASE})/(?<name>${KEBAB_CASE})`
const MODEL_CONFIG_ID = `(?<modelConfigId>${UUID})`

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
