import { ActionIcon, Group } from '@mantine/core'
import { IconBook, IconTrash } from '@tabler/icons-react'

import { RouterNavLink } from '@/components/common/NavLink'
import { useDeleteModelConfig } from '@/hooks/modelConfig'
import { iconSizeProps } from '@/utils'
import type { ModelConfig } from '@/types/api'

import classes from './AppShell.module.css'

function ActionIcons({ modelConfigId }: ActionIconsProps) {
  const { deleteModelConfig, isLoading } = useDeleteModelConfig()

  return (
    <ActionIcon.Group className={classes.actionIcons}>
      <ActionIcon
        aria-label="Delete"
        loading={isLoading}
        onClick={() => void deleteModelConfig(modelConfigId)}
        variant="default"
      >
        <IconTrash {...iconSizeProps('sm')} />
      </ActionIcon>
    </ActionIcon.Group>
  )
}

interface ActionIconsProps {
  modelConfigId: string
}

function ModelConfigLink({ modelConfig }: ModelConfigLinkProps) {
  return (
    <Group className={classes.navLinkWrapper}>
      <RouterNavLink
        className={classes.navLink}
        icon={IconBook}
        label={modelConfig.name}
        to={`/model-config/${modelConfig.id}`}
      />
      <ActionIcons modelConfigId={modelConfig.id} />
    </Group>
  )
}

interface ModelConfigLinkProps {
  modelConfig: ModelConfig
}

export default ModelConfigLink
