import { Route, Switch } from 'wouter'

import Player from './components/Player'
import NewStory from './components/Player/NewStory'

function Routes() {
  return (
    <Switch>
      <Route path="/" component={() => 'Home'} />
      <Route path="/editor" component={() => 'Editor'} />
      <Route path="/player" nest>
        <Route path="/new" component={NewStory} />
        <Route path="/story/:id" component={Player} />
      </Route>
      <Route path="/settings" component={() => 'Settings'} />
      <Route path="/*" component={() => '404 - Not Found'} />
    </Switch>
  )
}

export default Routes
