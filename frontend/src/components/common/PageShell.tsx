import { Container, Group, ScrollArea, Stack, Title } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'
import type { ReactNode } from 'react'

import { iconSizeProps } from '@/utils'

import classes from './PageShell.module.css'

interface PageShellProps {
  children: ReactNode
  fluid?: boolean
  footer?: ReactNode
  icon?: Icon
  title: string
  topBarMiddleSection?: ReactNode
  topBarRightSection?: ReactNode
}

function PageShell({
  children,
  fluid = false,
  footer,
  icon: Icon,
  title,
  topBarMiddleSection,
  topBarRightSection,
}: PageShellProps) {
  return (
    <Container className={classes.container} fluid={fluid}>
      <Stack gap="md" justify="center" h="100%">
        <Group className={classes.titleRow} preventGrowOverflow={false}>
          <Group className={classes.title} preventGrowOverflow={false}>
            {Icon && <Icon className={classes.icon} {...iconSizeProps('lg')} />}
            <Title lineClamp={1} order={2} textWrap="nowrap">
              {title}
            </Title>
          </Group>
          {(topBarMiddleSection ?? topBarRightSection) && (
            <>
              {topBarMiddleSection && <div className={classes.noShrink}>{topBarMiddleSection}</div>}
              {topBarRightSection && <div className={classes.noShrink}>{topBarRightSection}</div>}
            </>
          )}
        </Group>
        <ScrollArea
          classNames={{ root: classes.scrollArea, thumb: classes.scrollThumb }}
          scrollbars="y"
          type="scroll"
        >
          {children}
        </ScrollArea>
        {footer}
      </Stack>
    </Container>
  )
}

export default PageShell
