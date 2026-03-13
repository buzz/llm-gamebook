import { Center, SegmentedControl } from '@mantine/core'
import { IconBug, IconEye, IconListDetails } from '@tabler/icons-react'

import Toolbar from '@/components/common/toolbar/Toolbar'
import ToolbarGroup from '@/components/common/toolbar/ToolbarGroup'
import ModelConfigSelector from '@/components/model-config/ModelConfigSelector'
import { iconSizeProps } from '@/utils'

function ViewControl() {
  return (
    <SegmentedControl
      data={[
        {
          value: 'basic',
          label: (
            <Center style={{ gap: 10 }}>
              <IconEye {...iconSizeProps('sm')} />
              <span className="mantine-visible-from-md">Standard</span>
            </Center>
          ),
        },
        {
          value: 'details',
          label: (
            <Center style={{ gap: 10 }}>
              <IconListDetails {...iconSizeProps('sm')} />
              <span className="mantine-visible-from-md">Details</span>
            </Center>
          ),
        },
        {
          value: 'debug',
          label: (
            <Center style={{ gap: 10 }}>
              <IconBug {...iconSizeProps('sm')} />
              <span className="mantine-visible-from-md">Debug</span>
            </Center>
          ),
        },
      ]}
    />
  )
}

interface PlayerToolbarProps {
  disabled: boolean
  handleModelChange: (configId: string) => void
  modelConfigId: string | null
}

function PlayerToolbar({ disabled, handleModelChange, modelConfigId }: PlayerToolbarProps) {
  return (
    <Toolbar>
      <ToolbarGroup label="View">
        <ViewControl />
      </ToolbarGroup>

      <ToolbarGroup label="Model">
        <ModelConfigSelector
          disabled={disabled}
          onModelConfigChange={handleModelChange}
          selectedModelConfigId={modelConfigId}
        />
      </ToolbarGroup>
    </Toolbar>
  )
}

export default PlayerToolbar
