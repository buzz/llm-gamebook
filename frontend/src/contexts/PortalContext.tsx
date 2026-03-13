import { createContext, useCallback, useMemo, useState } from 'react'
import type { PropsWithChildren } from 'react'

type SlotName = 'toolbar' | 'sidebar'
type SlotMap = Map<SlotName, HTMLDivElement>

interface PortalContextValue {
  /** A function that layout areas use to register themselves. */
  registerSlot: (name: SlotName, ref: HTMLDivElement) => void

  /** Maps slot name to element. */
  slots: SlotMap
}

const PortalContext = createContext<PortalContextValue | null>(null)

function PortalProvider({ children }: PropsWithChildren) {
  const [slots, setSlots] = useState<SlotMap>(() => new Map())

  const registerSlot = useCallback((name: SlotName, ref: HTMLDivElement) => {
    setSlots((prev) => {
      const next = new Map(prev)
      next.set(name, ref)
      return next
    })
  }, [])

  const value = useMemo(() => ({ slots, registerSlot }), [slots, registerSlot])

  return <PortalContext value={value}>{children}</PortalContext>
}

export type { SlotName }
export { PortalProvider }
export default PortalContext
