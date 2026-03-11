import { ActionIcon, Group } from '@mantine/core'
import { IconCategory, IconTrash } from '@tabler/icons-react'

import { RouterNavLink } from '@/components/common/NavLink'
import { useDeleteModelConfig } from '@/hooks/model-config'
import { url } from '@/routes'
import { iconSizeProps } from '@/utils'
import type { ModelConfig } from '@/types/api'

import classes from './Link.module.css'

interface ActionIconsProps {
  modelConfigId: string
}

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

interface ModelConfigLinkProps {
  modelConfig: ModelConfig
}

function ModelConfigLink({ modelConfig }: ModelConfigLinkProps) {
  return (
    <Group className={classes.navLinkWrapper}>
      <RouterNavLink
        className={classes.navLink}
        icon={IconCategory}
        label={modelConfig.name}
        to={url('model-config.edit', { id: modelConfig.id })}
      />
      <ActionIcons modelConfigId={modelConfig.id} />
    </Group>
  )
}

export default ModelConfigLink
