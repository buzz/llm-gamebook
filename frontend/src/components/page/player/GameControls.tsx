import { Button, Group, Menu, Text } from '@mantine/core'
import { IconArrowBack, IconFlag, IconGitFork, IconHistory, IconRefresh } from '@tabler/icons-react'
import { useEffect } from 'react'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError } from '@/hooks/notifications'
import url from '@/routes/url'
import sessionApi from '@/services/session'
import { iconSizeProps } from '@/utils'
import type { Session, StateEntry } from '@/types/api'

interface GameControlsProps {
  session: Session
  /** Disables all controls, e.g. while a model response is streaming. */
  disabled: boolean
}

function formatTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) {
    return 'unknown time'
  }
  return new Date(timestamp).toLocaleString()
}

function GameControls({ session, disabled }: GameControlsProps) {
  const ended = session.endedAt != null
  const [, navigate] = useLocation()

  const [getStates, { data: states, isLoading: isLoadingStates }] =
    sessionApi.useLazyGetStatesQuery()
  const [restoreState, { isLoading: isRestoring }] = sessionApi.useRestoreStateMutation()
  const [forkState] = sessionApi.useForkStateMutation()
  const [endGame] = sessionApi.useEndGameMutation()
  const [resetSession] = sessionApi.useResetSessionMutation()
  const showConfirmationModal = useShowConfirmationModal()
  const showError = useShowError()

  // Load the state history so history-dependent controls can reflect availability.
  useEffect(() => {
    void getStates(session.id)
  }, [session.id, getStates])

  const snapshots: readonly StateEntry[] = states?.data ?? []
  const hasSnapshots = snapshots.length > 0
  const hasPreviousSnapshot = snapshots.length > 1

  const restore = async (step: number) => {
    try {
      await restoreState({ sessionId: session.id, projectId: session.projectId, step }).unwrap()
    } catch (error) {
      showError('Failed to restore state!', error)
    }
  }

  const handleUndo = () => {
    // Undo targets the second-newest snapshot (the one before the current position).
    const previous = snapshots.at(-2)
    if (previous) {
      void restore(previous.step)
    }
  }

  const handleFork = async () => {
    try {
      const { id } = await forkState({
        sessionId: session.id,
        projectId: session.projectId,
        step: -1,
      }).unwrap()
      navigate(url('player.view', { id }))
    } catch (error) {
      showError('Failed to fork session!', error)
    }
  }

  const handleEndGame = async () => {
    try {
      await endGame({ sessionId: session.id, projectId: session.projectId }).unwrap()
    } catch (error) {
      showError('Failed to end game!', error)
    }
  }

  const handleReset = async () => {
    try {
      if (
        await showConfirmationModal(
          'Reset session?',
          'Clears the game state and restarts from the project defaults. The message history is kept. This cannot be undone.'
        )
      ) {
        await resetSession({ sessionId: session.id, projectId: session.projectId }).unwrap()
      }
    } catch (error) {
      showError('Failed to reset session!', error)
    }
  }

  return (
    <Group gap="xs" wrap="nowrap">
      <Button
        aria-label="Undo"
        disabled={disabled || !hasPreviousSnapshot || isRestoring}
        leftSection={<IconArrowBack {...iconSizeProps('sm')} />}
        variant="subtle"
        onClick={handleUndo}
      >
        Undo
      </Button>

      <Menu disabled={disabled || isLoadingStates} withinPortal width={320}>
        <Menu.Target>
          <Button
            aria-label="State history"
            leftSection={<IconHistory {...iconSizeProps('sm')} />}
            variant="subtle"
          >
            History
          </Button>
        </Menu.Target>
        <Menu.Dropdown>
          {snapshots.length === 0 ? (
            <Menu.Item disabled>
              <Text size="sm" c="dimmed">
                No saved states yet.
              </Text>
            </Menu.Item>
          ) : (
            snapshots.map((snapshot) => (
              <Menu.Item
                key={snapshot.step}
                leftSection={<IconHistory {...iconSizeProps('sm')} />}
                onClick={() => void restore(snapshot.step)}
              >
                <Group gap="sm" wrap="nowrap">
                  <Text size="sm" fw={500}>
                    Step {snapshot.step}
                  </Text>
                  <Text size="xs" c="dimmed">
                    {formatTimestamp(snapshot.timestamp)}
                  </Text>
                  <Text size="xs" c="dimmed" ta="right">
                    Continue from here
                  </Text>
                </Group>
              </Menu.Item>
            ))
          )}
        </Menu.Dropdown>
      </Menu>

      <Button
        aria-label="Fork session"
        disabled={disabled || !hasSnapshots || isLoadingStates}
        leftSection={<IconGitFork {...iconSizeProps('sm')} />}
        variant="subtle"
        onClick={() => void handleFork()}
      >
        Fork
      </Button>

      <Button
        aria-label="End game"
        disabled={disabled || ended}
        leftSection={<IconFlag {...iconSizeProps('sm')} />}
        variant="subtle"
        onClick={() => void handleEndGame()}
      >
        End game
      </Button>

      <Button
        aria-label="Reset session"
        disabled={disabled}
        leftSection={<IconRefresh {...iconSizeProps('sm')} />}
        variant="subtle"
        onClick={() => void handleReset()}
      >
        Reset
      </Button>
    </Group>
  )
}

export default GameControls
