import { createPolymorphicComponent } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { use, useCallback } from 'react'

import CollapseContext from '@/contexts/CollapseContext'

import BasicNavLink, { type BasicNavLinkProps } from './BasicNavLink'

const CollapsibleNavLink = createPolymorphicComponent<'a', BasicNavLinkProps>(
  function CollapsibleNavLink({
    children,
    ref,
    ...otherProps
  }: BasicNavLinkProps & { ref?: React.RefObject<HTMLAnchorElement | null> }) {
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
        <BasicNavLink
          opened={isOpen}
          onClick={(event) => {
            toggle()
            otherProps.onClick?.(event)
          }}
          ref={ref}
          {...otherProps}
        >
          {children}
        </BasicNavLink>
      </CollapseContext>
    )
  }
)

export default CollapsibleNavLink
