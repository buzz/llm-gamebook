import { Group } from '@mantine/core'
import type { PropsWithChildren } from 'react'

function Toolbar({ children }: PropsWithChildren) {
  return (
    <Group gap="lg" wrap="nowrap">
      {children}
    </Group>
  )
}

export default Toolbar
