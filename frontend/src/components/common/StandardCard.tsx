import { Card, Group, Text } from '@mantine/core'
import type { CardProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'
import type { ReactNode } from 'react'

interface StandardCardProps extends CardProps {
  icon?: Icon
  title: ReactNode
  rightSection?: ReactNode
  children: ReactNode
  actionButtons?: ReactNode
}

function StandardCard({
  icon: Icon,
  title,
  rightSection,
  children,
  actionButtons,
  ...cardProps
}: StandardCardProps) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder {...cardProps}>
      <Group align="center" justify="space-between" mb="lg">
        <Group align="center">
          {Icon ? <Icon size={50} stroke={1} /> : null}
          <Text fw={500} size="xl">
            {title}
          </Text>
        </Group>
        {rightSection && <Group align="center">{rightSection}</Group>}
      </Group>
      {children}
      {actionButtons && (
        <Group justify="flex-end" mt="md">
          {actionButtons}
        </Group>
      )}
    </Card>
  )
}

export default StandardCard
