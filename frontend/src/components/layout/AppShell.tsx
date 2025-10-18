import { ActionIcon, AppShell as MantineAppShell, Group, Title } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconMenu2 } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'

import classes from './AppShell.module.css'
import Navbar from './Navbar'

function AppShell({ children }: { children: React.ReactNode }) {
  const [opened, { toggle }] = useDisclosure(true)

  return (
    <MantineAppShell
      padding={{ base: 'xs', sm: 'sm', md: 'md' }}
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { desktop: !opened, mobile: !opened },
      }}
    >
      <MantineAppShell.Header>
        <Group h="100%" wrap="nowrap" p="md">
          <ActionIcon
            title="Toggle menu"
            onClick={toggle}
            size="lg"
            variant={opened ? 'filled' : 'default'}
          >
            <IconMenu2 {...iconSizeProps('md')} />
          </ActionIcon>
          <div className={classes.titleWrapper}>
            <Title className={classes.title} lineClamp={2} order={1} size="xl">
              LLM Gamebook
            </Title>
          </div>
        </Group>
      </MantineAppShell.Header>

      <MantineAppShell.Navbar>
        <Navbar />
      </MantineAppShell.Navbar>

      <MantineAppShell.Main h="100dvh">{children}</MantineAppShell.Main>
    </MantineAppShell>
  )
}

export default AppShell
