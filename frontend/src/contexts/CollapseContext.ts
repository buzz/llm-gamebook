import { createContext } from 'react'

interface CollapseContextValue {
  /** Signal parent to expand. */
  onChildActive: () => void
}

const CollapseContext = createContext<CollapseContextValue | null>(null)

export default CollapseContext
