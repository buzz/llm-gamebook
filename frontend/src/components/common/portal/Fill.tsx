import { createPortal } from 'react-dom'
import type { PropsWithChildren } from 'react'

import usePortalContext from '@/hooks/portal'
import type { SlotName } from '@/contexts/PortalContext'

interface FillProps extends PropsWithChildren {
  name: SlotName
}

function Fill({ children, name }: FillProps) {
  const { slots } = usePortalContext()
  const target = slots.get(name)

  if (!target) {
    // Slot hasn't registered yet
    return null
  }

  return createPortal(children, target)
}

export default Fill
