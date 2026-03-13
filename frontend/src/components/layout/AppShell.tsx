import { AppShell as MantineAppShell } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { use, useEffect } from 'react'

import WebSocketContext from '@/contexts/WebSocketContext'
import { useShowErrorModal } from '@/hooks/modals'

import Header from './Header/Header'
import Navbar from './Navbar/Navbar'

function AppShell({ children }: { children: React.ReactNode }) {
  const context = use(WebSocketContext)
  const [navbarOpened, { toggle: toggleNavbar }] = useDisclosure(true)
  const showErrorModal = useShowErrorModal()

  useEffect(() => {
    if (context?.error) {
      showErrorModal(context.error)
    }
  }, [context?.error, showErrorModal])

  return (
    <MantineAppShell
      padding={{ base: 'xs', sm: 'sm', md: 'md' }}
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { desktop: !navbarOpened, mobile: !navbarOpened },
      }}
    >
      <MantineAppShell.Header>
        <Header navbarOpened={navbarOpened} onToggleNavbar={toggleNavbar} />
      </MantineAppShell.Header>

      <MantineAppShell.Navbar>
        <Navbar />
      </MantineAppShell.Navbar>

      <MantineAppShell.Main h="100dvh">{children}</MantineAppShell.Main>
    </MantineAppShell>
  )
}

export default AppShell
