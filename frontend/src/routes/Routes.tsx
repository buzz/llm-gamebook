import { Route, Switch } from 'wouter'

import NotFound from '@/components/common/NotFound'
import type { RouteDef } from '@/types/routes'

import { ROUTES } from './routes'

const regexpRoutes = Object.fromEntries(
  Object.entries(ROUTES).map(([name, route]: [string, RouteDef]) => [
    name,
    { ...route, path: new RegExp(`^${route.path}$`) },
  ])
)

function Routes() {
  const routes = Object.entries(regexpRoutes).map(([name, { component, path }]) => (
    <Route key={name} component={component} path={path} />
  ))

  return (
    <Switch>
      {routes}
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default Routes
