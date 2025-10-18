import { createPolymorphicComponent, NavLink } from '@mantine/core'
import type { NavLinkProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'

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
      leftSection={Icon ? <Icon {...iconSizeProps('md')} /> : null}
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
