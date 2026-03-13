import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

import { localStorageColorSchemeManager, MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { Notifications } from '@mantine/notifications'
import { ErrorBoundary } from 'react-error-boundary'
import { Provider as ReactReduxProvider } from 'react-redux'

import ErrorAlert from './components/common/ErrorAlert'
import AppShell from './components/layout/AppShell'
import { PortalProvider } from './contexts/PortalContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import Routes from './routes/Routes'
import store from './store'
import { cssVariablesResolver, themeOverride } from './theme/theme'

const colorSchemeManager = localStorageColorSchemeManager({ key: 'llm-gamebook-color-scheme' })

function App() {
  return (
    <ReactReduxProvider store={store}>
      <WebSocketProvider>
        <MantineProvider
          colorSchemeManager={colorSchemeManager}
          cssVariablesResolver={cssVariablesResolver}
          defaultColorScheme="auto"
          theme={themeOverride}
        >
          <ModalsProvider>
            <Notifications />
            <PortalProvider>
              <AppShell>
                <ErrorBoundary FallbackComponent={ErrorAlert}>
                  <Routes />
                </ErrorBoundary>
              </AppShell>
            </PortalProvider>
          </ModalsProvider>
        </MantineProvider>
      </WebSocketProvider>
    </ReactReduxProvider>
  )
}

export default App
