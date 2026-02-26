import { createPolymorphicComponent, NavLink } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { useEffect, useMemo } from 'react'
import { useLocation } from 'wouter'
import type { NavLinkProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'

import classes from './CollapsibleNavLink.module.css'

interface CollapsibleNavLinkProps extends NavLinkProps {
  icon?: Icon
  matchRoute?: string | string[]
}

function routeMatches(path: string, pattern: string): boolean {
  const regexPattern = pattern.replaceAll('*', '.*').replaceAll(':', String.raw`\w+`)
  const regex = new RegExp(`^${regexPattern}$`)
  return regex.test(path)
}

const CollapsibleNavLink = createPolymorphicComponent<'a', CollapsibleNavLinkProps>(
  function CollapsibleNavLink({
    children,
    icon: Icon,
    matchRoute,
    ref,
    ...otherProps
  }: CollapsibleNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
    const [isOpen, handlers] = useDisclosure(false)
    const [location] = useLocation()

    const isAnyMatch = useMemo(() => {
      const routes = Array.isArray(matchRoute) ? matchRoute : matchRoute ? [matchRoute] : []
      return routes.some((route) => routeMatches(location, route))
    }, [location, matchRoute])

    useEffect(() => {
      if (isAnyMatch) {
        handlers.open()
      }
    }, [isAnyMatch, handlers])

    return (
      <NavLink
        classNames={{ label: classes.label, root: classes.navLink }}
        leftSection={Icon ? <Icon {...iconSizeProps('md')} /> : null}
        noWrap
        opened={isOpen}
        onClick={(event) => {
          handlers.toggle()
          otherProps.onClick?.(event)
        }}
        ref={ref}
        {...otherProps}
      >
        {children}
      </NavLink>
    )
  }
)

export type { CollapsibleNavLinkProps }
export default CollapsibleNavLink
