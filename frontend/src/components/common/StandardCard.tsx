import { Card, Group, Image, Title } from '@mantine/core'
import type { CardProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'
import type { ReactNode } from 'react'

import { iconSizeProps } from '@/utils'

interface StandardCardProps extends CardProps {
  icon?: Icon
  title: ReactNode
  rightSection?: ReactNode
  children: ReactNode
  actionButtons?: ReactNode
  imageSrc?: string
  imageAlt?: string
}

function StandardCard({
  icon: Icon,
  title,
  rightSection,
  children,
  actionButtons,
  imageSrc,
  imageAlt,
  ...cardProps
}: StandardCardProps) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder {...cardProps}>
      {imageSrc && (
        <Card.Section>
          <Image src={imageSrc} height={160} alt={imageAlt} />
        </Card.Section>
      )}

      <Group
        align="center"
        justify="space-between"
        mb="xs"
        mt={imageSrc ? 'lg' : undefined}
        preventGrowOverflow={false}
        w="100%"
        wrap="nowrap"
      >
        <Group align="center" preventGrowOverflow={false} w="100%" wrap="nowrap">
          {Icon ? <Icon {...iconSizeProps('lg')} /> : null}
          {typeof title === 'string' ? <Title order={3}>{title}</Title> : title}
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
