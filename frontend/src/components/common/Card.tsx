import { Card as MantineCard, Group, Image, Title } from '@mantine/core'
import type { CardProps as MantineCardProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'
import type { ReactNode } from 'react'

import { iconSizeProps } from '@/utils'

interface CardProps extends MantineCardProps {
  icon?: Icon
  title: ReactNode
  rightSection?: ReactNode
  children: ReactNode
  actionButtons?: ReactNode
  imageSrc?: string
  imageAlt?: string
}

function Card({
  icon: Icon,
  title,
  rightSection,
  children,
  actionButtons,
  imageSrc,
  imageAlt,
  ...cardProps
}: CardProps) {
  return (
    <MantineCard shadow="sm" padding="lg" radius="md" withBorder {...cardProps}>
      {imageSrc && (
        <MantineCard.Section>
          <Image src={imageSrc} height={160} alt={imageAlt} />
        </MantineCard.Section>
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
    </MantineCard>
  )
}

export default Card
