import { Box, Stack } from '@mantine/core'
import { useCallback, useState } from 'react'
import { useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import ModelConfigSelector from '@/components/model-config/ModelConfigSelector'
import sessionApi from '@/services/session'
import type { SessionFull } from '@/types/api'

import Controls from './Controls'
import Messages from './Messages/Messages'
import classes from './Player.module.css'
import useMessages from './use-messages'

interface PlayerLoadedProps {
  session: SessionFull
}

function PlayerLoaded({ session }: PlayerLoadedProps) {
  const { currentStreamingPartId, messages, streamStatus } = useMessages(session)
  const [modelConfigId, setModelConfigId] = useState(session.config_id ?? null)
  const [updateSession, { isLoading: isUpdating }] = sessionApi.useUpdateSessionMutation()

  const handleModelChange = useCallback(
    (newConfigId: string) => {
      updateSession({ id: session.id, config_id: newConfigId })
        .unwrap()
        .then(() => {
          setModelConfigId(newConfigId)
        })
        .catch(() => {
          console.error('Failed to update session model')
        })
    },
    [session.id, updateSession]
  )

  return (
    <Stack gap="md" justify="center" h="100%">
      <ModelConfigSelector
        selectedModelConfigId={modelConfigId}
        onModelConfigChange={handleModelChange}
        disabled={isUpdating || streamStatus === 'started'}
      />
      <Box className={classes.container}>
        <Messages currentStreamingPartId={currentStreamingPartId} messages={messages} />
        <Controls isGenerating={streamStatus === 'started'} sessionId={session.id} />
      </Box>
    </Stack>
  )
}

function Player() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const result = sessionApi.useGetSessionByIdQuery(sessionId)

  return (
    <QueryHandler
      notFoundTitle="Story session not found"
      notFoundMessage="The story session does not exist."
      result={result}
    >
      {(data) => <PlayerLoaded session={data} />}
    </QueryHandler>
  )
}

export default Player
