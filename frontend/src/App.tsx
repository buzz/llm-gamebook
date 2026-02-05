import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

import { MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { Notifications } from '@mantine/notifications'
import { ErrorBoundary } from 'react-error-boundary'
import { Provider as ReactReduxProvider } from 'react-redux'

import ErrorAlert from './components/common/ErrorAlert'
import AppShell from './components/layout/AppShell'
import { WebSocketProvider } from './contexts/WebSocketContext'
import Routes from './Routes'
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
                <Routes />
              </ErrorBoundary>
            </AppShell>
          </ModalsProvider>
        </MantineProvider>
      </WebSocketProvider>
    </ReactReduxProvider>
  )
}

export default App
