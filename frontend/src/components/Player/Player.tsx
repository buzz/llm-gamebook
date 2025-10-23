import { Flex } from '@mantine/core'
import { skipToken } from '@reduxjs/toolkit/query'
import { useParams } from 'wouter'

import QueryHandler from '@/components/common/QueryHandler'
import sessionApi from '@/services/session'
import type { SessionFull } from '@/types/api'

import Controls from './Controls'
import Messages from './Messages/Messages'
import useMessages from './useMessages'

interface PlayerLoadedProps {
  session: SessionFull
}

function PlayerLoaded({ session }: PlayerLoadedProps) {
  const { currentStreamingPartId, messages, streamStatus } = useMessages(session)

  return (
    <Flex direction="column" gap={{ base: 'sm', sm: 'lg' }} justify="center" h="100%">
      <Messages currentStreamingPartId={currentStreamingPartId} messages={messages} />
      <Controls isGenerating={streamStatus === 'started'} sessionId={session.id} />
    </Flex>
  )
}

function Player() {
  const { sessionId } = useParams()
  const result = sessionApi.useGetSessionByIdQuery(sessionId ?? skipToken)

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
