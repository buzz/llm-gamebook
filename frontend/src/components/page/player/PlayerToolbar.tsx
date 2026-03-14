import ChatViewControl from '@/components/common/form/ChatViewControl'
import ModelConfigSelector from '@/components/common/form/ModelConfigSelector'
import Toolbar from '@/components/common/toolbar/Toolbar'
import ToolbarGroup from '@/components/common/toolbar/ToolbarGroup'

interface PlayerToolbarProps {
  disabled: boolean
  handleModelChange: (configId: string) => void
  modelConfigId: string | null
}

function PlayerToolbar({ disabled, handleModelChange, modelConfigId }: PlayerToolbarProps) {
  return (
    <Toolbar>
      <ToolbarGroup label="View">
        <ChatViewControl />
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
