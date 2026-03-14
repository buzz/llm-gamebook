import { createPolymorphicComponent } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { use, useCallback } from 'react'

import CollapseContext from '@/contexts/CollapseContext'

import BaseNavLink from './BaseNavLink'
import type { BaseNavLinkProps } from './BaseNavLink'

const CollapsibleNavLink = createPolymorphicComponent<'a', BaseNavLinkProps>(
  function CollapsibleNavLink({
    children,
    ref,
    ...otherProps
  }: BaseNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
    const [isOpen, { toggle, open }] = useDisclosure(false)
    const parentContext = use(CollapseContext)

    const onChildActive = useCallback(() => {
      open()

      // Bubble upward
      if (parentContext) {
        parentContext.onChildActive()
      }
    }, [open, parentContext])

    return (
      <CollapseContext value={{ onChildActive }}>
        <BaseNavLink
          opened={isOpen}
          onClick={(event) => {
            toggle()
            otherProps.onClick?.(event)
          }}
          ref={ref}
          {...otherProps}
        >
          {children}
        </BaseNavLink>
      </CollapseContext>
    )
  }
)

export default CollapsibleNavLink
