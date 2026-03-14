import Editor from '@/components/page/editor/Editor'
import ModelConfigForm from '@/components/page/ModelConfigForm'
import Player from '@/components/page/player/Player'
import ProjectDetails from '@/components/page/project/ProjectDetails'
import ProjectForm from '@/components/page/project/ProjectForm'
import ProjectList from '@/components/page/project/ProjectList'
import SettingsForm from '@/components/page/SettingsForm'
import { KEBAB_CASE_PATTERN, UUID_PATTERN } from '@/constants'
import type { RouteDef } from '@/types/routes'

const PROJECT_ID = `(?<namespace>${KEBAB_CASE_PATTERN})/(?<name>${KEBAB_CASE_PATTERN})` as const
const UUID = `(?<id>${UUID_PATTERN})` as const

const ROUTES = {
  home: {
    path: '/' as const,
    component: ProjectList,
  },

  'gamebook.new': {
    path: '/gamebook/new' as const,
    component: ProjectForm,
  },
  'gamebook.view': {
    path: `/gamebook/${PROJECT_ID}` as const,
    component: ProjectDetails,
  },

  'model-config.new': {
    path: '/model-config/new' as const,
    component: ModelConfigForm,
  },
  'model-config.edit': {
    path: `/model-config/${UUID}` as const,
    component: ModelConfigForm,
  },

  'editor.edit': {
    path: `/editor/${PROJECT_ID}` as const,
    component: Editor,
  },

  'player.view': {
    path: `/player/${UUID}` as const,
    component: Player,
  },

  settings: {
    path: '/settings' as const,
    component: SettingsForm,
  },
} as const satisfies Record<string, RouteDef>

export default ROUTES
