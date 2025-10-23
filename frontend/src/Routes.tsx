import { Route, Switch } from 'wouter'

import NotFound from './components/common/NotFound'
import Player from './components/Player'
import NewStory from './components/Player/NewStory'

const uuidPattern =
  '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}'

function Routes() {
  return (
    <Switch>
      <Route path="/" component={() => 'Home'} />
      <Route path="/editor" component={() => 'Editor'} />
      <Route
        path={new RegExp(`^/editor/story/(?<sessionId>${uuidPattern})$`)}
        component={() => 'Editor'}
      />
      <Route path="/player/new" component={NewStory} />
      <Route path={new RegExp(`^/player/(?<sessionId>${uuidPattern})$`)} component={Player} />
      <Route path="/settings" component={() => 'Settings'} />
      <Route>
        <NotFound />
      </Route>
    </Switch>
  )
}

export default Routes
