import type { RouteName, RouteParams } from '@/types/routes'

import ROUTES from './routes'

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

export default url
