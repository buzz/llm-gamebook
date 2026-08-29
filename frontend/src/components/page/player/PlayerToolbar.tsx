import ChatViewControl from '@/components/common/form/ChatViewControl'
import ModelConfigSelector from '@/components/common/form/ModelConfigSelector'
import Toolbar from '@/components/common/toolbar/Toolbar'
import ToolbarGroup from '@/components/common/toolbar/ToolbarGroup'
import type { Session } from '@/types/api'

import GameControls from './GameControls'

interface PlayerToolbarProps {
  disabled: boolean
  session: Session
  handleModelChange: (configId: string) => void
  modelConfigId: string | null
}

function PlayerToolbar({
  disabled,
  session,
  handleModelChange,
  modelConfigId,
}: PlayerToolbarProps) {
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

      <ToolbarGroup label="Game">
        <GameControls disabled={disabled} session={session} />
      </ToolbarGroup>
    </Toolbar>
  )
}

export default PlayerToolbar
