import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

import { MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { Notifications } from '@mantine/notifications'
import { Provider } from 'react-redux'

import AppShell from './components/layout/AppShell'
import Routes from './Routes'
import { store } from './store'

function App() {
  return (
    <Provider store={store}>
      <MantineProvider defaultColorScheme="dark">
        <ModalsProvider>
          <Notifications />
          <AppShell>
            <Routes />
          </AppShell>
        </ModalsProvider>
      </MantineProvider>
    </Provider>
  )
}

export default App
