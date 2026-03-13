import { useCallback } from 'react'

import usePortalContext from '@/hooks/portal'
import type { SlotName } from '@/contexts/PortalContext'

interface SlotProps {
  name: SlotName
}

function Slot({ name }: SlotProps) {
  const { registerSlot } = usePortalContext()

  const divRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (node) {
        registerSlot(name, node)
      }
    },
    [name, registerSlot]
  )

  return <div ref={divRef} />
}

export default Slot
