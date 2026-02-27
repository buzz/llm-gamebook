import { createPolymorphicComponent } from '@mantine/core'
import { use, useEffect, useRef } from 'react'
import { Link, useLocation, useRoute } from 'wouter'
import type { LinkProps } from 'wouter'

import CollapseContext from '@/contexts/CollapseContext'

import BasicNavLink, { type BasicNavLinkProps } from './BasicNavLink'

type RouterNavLinkProps = BasicNavLinkProps & LinkProps

const RouterNavLink = createPolymorphicComponent<'a', RouterNavLinkProps>(function RouterNavLink({
  children,
  ref,
  ...otherProps
}: RouterNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
  const [location, setLocation] = useLocation()
  const prevLocationRef = useRef<string | null>(null)
  const [isActive] = useRoute(otherProps.to ?? '')
  const context = use(CollapseContext)

  useEffect(() => {
    // When we had a route change and this link becomes active, yell up the tree!
    if (context && location !== prevLocationRef.current && isActive) {
      context.onChildActive()
    }
    prevLocationRef.current = location
  }, [context, isActive, location])

  return (
    <BasicNavLink
      active={isActive}
      component={Link}
      onClick={(event) => {
        event.preventDefault()
        if (otherProps.to) {
          setLocation(otherProps.to)
        }
      }}
      {...otherProps}
      ref={ref}
    >
      {children}
    </BasicNavLink>
  )
})

export default RouterNavLink
