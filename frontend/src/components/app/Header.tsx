import { ActionIcon, Group, Title } from '@mantine/core'
import { IconMenu2 } from '@tabler/icons-react'

import Slot from '@/components/common/portal/Slot'
import { iconSizeProps } from '@/utils'

import classes from './Header.module.css'

interface HeaderProps {
  navbarOpened: boolean
  onToggleNavbar: () => void
}

function Header({ navbarOpened, onToggleNavbar }: HeaderProps) {
  return (
    <Group h="100%" wrap="nowrap" p="md">
      <ActionIcon
        title="Toggle menu"
        onClick={onToggleNavbar}
        size="lg"
        variant={navbarOpened ? 'filled' : 'default'}
      >
        <IconMenu2 {...iconSizeProps('md')} />
      </ActionIcon>
      <div className={classes.titleWrapper}>
        <Title className={classes.title} lineClamp={2} order={1} size="xl">
          LLM Gamebook
        </Title>
      </div>
      <Slot name="toolbar" />
    </Group>
  )
}

export default Header
