import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

import { MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { Notifications } from '@mantine/notifications'
import { ErrorBoundary } from 'react-error-boundary'
import { Provider as ReactReduxProvider } from 'react-redux'
import { Route, Switch } from 'wouter'

import ErrorAlert from './components/common/ErrorAlert'
import NotFound from './components/common/NotFound'
import AppShell from './components/layout/AppShell'
import { WebSocketProvider } from './contexts/WebSocketContext'
import routes from './routes'
import store from './store'

function App() {
  return (
    <ReactReduxProvider store={store}>
      <WebSocketProvider>
        <MantineProvider defaultColorScheme="dark">
          <ModalsProvider>
            <Notifications />
            <AppShell>
              <ErrorBoundary FallbackComponent={ErrorAlert}>
                <Switch>
                  {routes.map(({ component, path }) => (
                    <Route key={String(path)} component={component} path={path} />
                  ))}
                  <Route>
                    <NotFound />
                  </Route>
                </Switch>
              </ErrorBoundary>
            </AppShell>
          </ModalsProvider>
        </MantineProvider>
      </WebSocketProvider>
    </ReactReduxProvider>
  )
}

export default App
