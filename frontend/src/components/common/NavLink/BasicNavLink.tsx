import { createPolymorphicComponent, NavLink } from '@mantine/core'
import type { NavLinkProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import classes from './BasicNavLink.module.css'

interface BasicNavLinkProps extends Omit<NavLinkProps, 'leftSection'> {
  icon?: Icon
}

const BasicNavLink = createPolymorphicComponent<'a', BasicNavLinkProps>(function BasicNavLink({
  children,
  icon: Icon,
  ref,
  ...otherProps
}: BasicNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
  return (
    <NavLink
      classNames={{ label: classes.label, root: classes.navLink }}
      leftSection={Icon ? <Icon size={24} stroke={1.5} /> : null}
      noWrap
      {...otherProps}
      ref={ref}
    >
      {children}
    </NavLink>
  )
})

export type { BasicNavLinkProps }
export default BasicNavLink
