import '@mantine/core/styles.css'

import { MantineProvider } from '@mantine/core'

import AppShell from './components/layout/AppShell'
import Routes from './Routes'

function App() {
  return (
    <MantineProvider defaultColorScheme="dark">
      <AppShell>
        <Routes />
      </AppShell>
    </MantineProvider>
  )
}

export default App
