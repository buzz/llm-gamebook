import Editor from '@/components/editor/Editor'
import ModelConfigForm from '@/components/model-config/ModelConfigForm'
import Player from '@/components/player'
import ProjectDetails from '@/components/project/ProjectDetails'
import ProjectForm from '@/components/project/ProjectForm'
import ProjectList from '@/components/project/ProjectList'
import Settings from '@/components/settings/Settings'
import { KEBAB_CASE_PATTERN, UUID_PATTERN } from '@/constants'
import type { RouteDef, RouteName, RouteParams } from '@/types/routes'

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
    component: Settings,
  },
} satisfies Record<string, RouteDef>

/**
 * Build a URL from a route name and parameters
 *
 * @example
 * url('home') → '/'
 * url('gamebook.view', { namespace: 'foo', name: 'bar' }) → '/gamebook/foo/bar'
 */
function url<T extends RouteName>(
  routeName: T,
  ...args: [RouteParams<T>] extends [never] ? [] : [params: RouteParams<T>]
): string {
  let path: string = ROUTES[routeName].path
  const params = args[0] as Record<string, string> | undefined

  // Replace parameters, e.g. `(?<id>...)`
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      const pattern = new RegExp(String.raw`\(\?<${key}>[^/]+\)`)
      path = path.replace(pattern, value)
    }
  }

  return path
}

export { ROUTES, url }
