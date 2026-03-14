import { createPolymorphicComponent, NavLink } from '@mantine/core'
import type { NavLinkProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'

import classes from './Link.module.css'

interface BaseNavLinkProps extends NavLinkProps {
  icon?: Icon
}

const BaseNavLink = createPolymorphicComponent<'a', BaseNavLinkProps>(function BaseNavLink({
  children,
  icon: Icon,
  ref,
  ...otherProps
}: BaseNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
  return (
    <NavLink
      classNames={{
        label: classes.label,
        root: classes.navLinkRoot,
      }}
      leftSection={Icon ? <Icon {...iconSizeProps('md')} /> : null}
      noWrap
      {...otherProps}
      ref={ref}
    >
      {children}
    </NavLink>
  )
})

export type { BaseNavLinkProps }
export default BaseNavLink
