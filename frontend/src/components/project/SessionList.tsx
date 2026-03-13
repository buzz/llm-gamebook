import { Anchor, Text, Timeline } from '@mantine/core'
import { Link } from 'wouter'

import { formatDuration, useNow } from '@/hooks/time'
import { url } from '@/routes'
import type { Session } from '@/types/api'

interface SessionProps {
  session: Session
}

function Session({ session }: SessionProps) {
  const now = useNow()

  return (
    <Timeline.Item
      key={session.id}
      title={
        <Anchor component={Link} to={url('player.view', { id: session.id })} truncate="end">
          {session.title ?? 'Untitled Session'}
        </Anchor>
      }
    >
      <Text size="sm">
        {session.message_count} Message{session.message_count === 1 ? '' : 's'}
      </Text>
      {session.timestamp && (
        <Text c="dimmed" size="xs" mt={4}>
          {formatDuration(now - Date.parse(session.timestamp))} ago
        </Text>
      )}
    </Timeline.Item>
  )
}

interface SessionListProps {
  sessions: readonly Session[]
}

function SessionList({ sessions }: SessionListProps) {
  return (
    <>
      <Timeline lineWidth={2}>
        {sessions.map((session) => (
          <Session key={session.id} session={session} />
        ))}
      </Timeline>
    </>
  )
}

export default SessionList
