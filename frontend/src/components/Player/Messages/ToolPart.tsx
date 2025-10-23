import { Group, Text } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'
import type { ReactNode } from 'react'

import { iconSizeProps } from '@/utils'

import classes from './Messages.module.css'

interface ToolPartProps {
  children: ReactNode
  icon: Icon
  title: string
}

function ToolPart({ children, icon: Icon, title }: ToolPartProps) {
  return (
    <Group className={classes.toolPart}>
      <Group className={classes.title}>
        <Icon {...iconSizeProps('sm')} />
        <Text>{title}</Text>
      </Group>
      <Group className={classes.data}>{children}</Group>
    </Group>
  )
}

export default ToolPart
