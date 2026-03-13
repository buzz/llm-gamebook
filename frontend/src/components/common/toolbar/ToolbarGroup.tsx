import { Group, Text } from '@mantine/core'
import type { PropsWithChildren } from 'react'

interface ToolbarGroupProps extends PropsWithChildren {
  label: string
}

function ToolbarGroup({ children, label }: ToolbarGroupProps) {
  return (
    <Group gap="sm" wrap="nowrap">
      <Text fw={500} size="sm" visibleFrom="sm">
        {label}
      </Text>
      {children}
    </Group>
  )
}

export default ToolbarGroup
