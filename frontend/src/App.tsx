import '@mantine/core/styles.css'

import { AppShell, Burger, MantineProvider } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'

import Routes from './Routes'

function App() {
  const [opened, { toggle }] = useDisclosure()

  return (
    <MantineProvider defaultColorScheme="dark">
      <AppShell
        padding="md"
        header={{ height: 60 }}
        navbar={{
          width: 300,
          breakpoint: 'sm',
          collapsed: { mobile: !opened },
        }}
      >
        <AppShell.Header>
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />

          <div>Logo</div>
        </AppShell.Header>

        <AppShell.Navbar>Navbar</AppShell.Navbar>

        <AppShell.Main>
          <Routes />
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  )
}

export default App
