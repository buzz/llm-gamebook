import { Badge } from '@mantine/core'
import { IconBulb, IconUserCircle } from '@tabler/icons-react'

import { assertNever } from '@/types/common'
import { iconSizeProps } from '@/utils'
import type { ProjectSource } from '@/types/api'

interface ProjectSourceBadgeProps {
  source: ProjectSource
}

function ProjectSourceBadge({ source }: ProjectSourceBadgeProps) {
  switch (source) {
    case 'example': {
      return (
        <Badge color="grape" leftSection={<IconBulb {...iconSizeProps('sm')} />}>
          Example
        </Badge>
      )
    }
    case 'local': {
      return (
        <Badge color="green" leftSection={<IconUserCircle {...iconSizeProps('sm')} />}>
          Local
        </Badge>
      )
    }
    default: {
      assertNever(source)
    }
  }
}

export default ProjectSourceBadge
