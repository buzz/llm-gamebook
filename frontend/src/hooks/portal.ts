import { use } from 'react'

import PortalContext from '@/contexts/PortalContext'

function usePortalContext() {
  const value = use(PortalContext)

  if (!value) {
    throw new Error('No PortalProvider found!')
  }

  return value
}

export default usePortalContext
