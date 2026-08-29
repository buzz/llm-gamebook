import { MantineProvider } from '@mantine/core'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useLocation } from 'wouter'

import { useShowConfirmationModal } from '@/hooks/modals'
import { useShowError } from '@/hooks/notifications'
import sessionApi from '@/services/session'
import type { Session, StateHistory } from '@/types/api'

import GameControls from './GameControls'

// Mock modules
vi.mock('@/hooks/modals')
vi.mock('@/hooks/notifications')
vi.mock('@/services/session')
vi.mock('wouter')

const SESSION_ID = 'session-1'
const PROJECT_ID = 'llm-gamebook/test'

const mockNavigate = vi.fn()
const mockGetStates = vi.fn()
const mockRestoreState = vi.fn().mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) })
const mockForkState = vi
  .fn()
  .mockReturnValue({ unwrap: vi.fn().mockResolvedValue({ id: 'fork-1' }) })
const mockEndGame = vi.fn().mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) })
const mockResetSession = vi.fn().mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) })

function makeSession(overrides: Partial<Session> = {}): Session {
  return {
    id: SESSION_ID,
    projectId: PROJECT_ID,
    messageCount: 0,
    ...overrides,
  }
}

function snapshotHistory(steps: number[]): StateHistory {
  return {
    data: steps.map((step, i) => ({
      step,
      timestamp: `2024-01-01T12:0${String(i)}:00`,
      fieldCount: 1,
    })),
  }
}

function mockStatesQuery(history: StateHistory | undefined, isLoading = false) {
  vi.mocked(sessionApi.useLazyGetStatesQuery).mockReturnValue([
    mockGetStates,
    { data: history, isLoading },
  ] as never)
}

function renderGameControls(session: Session = makeSession()) {
  return render(
    <MantineProvider>
      <GameControls disabled={false} session={session} />
    </MantineProvider>
  )
}

function button(name: RegExp): HTMLButtonElement {
  return screen.getByRole('button', { name })
}

beforeEach(() => {
  vi.clearAllMocks()

  vi.mocked(useLocation).mockReturnValue([`/player/${SESSION_ID}`, mockNavigate])
  vi.mocked(useShowError).mockReturnValue(vi.fn())
  vi.mocked(useShowConfirmationModal).mockReturnValue(() => Promise.resolve(true))

  vi.mocked(sessionApi.useLazyGetStatesQuery).mockReturnValue([
    mockGetStates,
    { data: undefined, isLoading: false },
  ] as never)
  vi.mocked(sessionApi.useRestoreStateMutation).mockReturnValue([
    mockRestoreState,
    { isLoading: false },
  ] as never)
  vi.mocked(sessionApi.useForkStateMutation).mockReturnValue([mockForkState, {}] as never)
  vi.mocked(sessionApi.useEndGameMutation).mockReturnValue([mockEndGame, {}] as never)
  vi.mocked(sessionApi.useResetSessionMutation).mockReturnValue([mockResetSession, {}] as never)
})

describe('GameControls', () => {
  describe('controls render', () => {
    it('shows undo, history, fork, end game, and reset', () => {
      mockStatesQuery(snapshotHistory([2, 5, 7]))

      renderGameControls()

      expect(button(/undo/i)).not.toBeNull()
      expect(button(/history/i)).not.toBeNull()
      expect(button(/fork/i)).not.toBeNull()
      expect(button(/end game/i)).not.toBeNull()
      expect(button(/reset/i)).not.toBeNull()
    })

    it('loads the state history for the session', () => {
      mockStatesQuery(snapshotHistory([2]))

      renderGameControls()

      expect(mockGetStates).toHaveBeenCalledWith(SESSION_ID)
    })
  })

  describe('disabled states', () => {
    it('disables undo and fork when there are no snapshots', () => {
      mockStatesQuery(snapshotHistory([]))

      renderGameControls()

      expect(button(/undo/i).disabled).toBe(true)
      expect(button(/fork/i).disabled).toBe(true)
      // Reset stays available for an existing session
      expect(button(/reset/i).disabled).toBe(false)
    })

    it('disables end game when the session is already ended', () => {
      mockStatesQuery(snapshotHistory([2]))

      renderGameControls(makeSession({ endedAt: '2024-01-01T00:00:00' }))

      expect(button(/end game/i).disabled).toBe(true)
    })

    it('disables all controls while a response is streaming', async () => {
      const user = userEvent.setup()
      mockStatesQuery(snapshotHistory([2, 5]))

      render(
        <MantineProvider>
          <GameControls disabled session={makeSession()} />
        </MantineProvider>
      )

      expect(button(/undo/i).disabled).toBe(true)
      expect(button(/fork/i).disabled).toBe(true)
      expect(button(/end game/i).disabled).toBe(true)
      expect(button(/reset/i).disabled).toBe(true)
      // The history menu does not open while disabled.
      await user.click(button(/history/i))
      expect(screen.queryByText(/^step \d+$/i)).toBeNull()
    })
  })

  describe('state history menu', () => {
    it('lists the snapshots in ascending step order with timestamps', async () => {
      const user = userEvent.setup()
      const history = snapshotHistory([2, 5, 7])
      mockStatesQuery({
        data: history.data.map((entry) => ({
          ...entry,
          timestamp: `2024-01-01T12:0${String(entry.step - 1)}:00`,
        })),
      })

      renderGameControls()
      await user.click(button(/history/i))

      // Wait for the dropdown to mount, then assert the full listing.
      await screen.findByText('Step 5')
      const items = screen.getAllByText(/^step \d+$/i)
      expect(items.map((item) => item.textContent)).toEqual(['Step 2', 'Step 5', 'Step 7'])
      // Each entry shows its snapshot timestamp, formatted like the component does.
      expect(
        await screen.findByText(new Date('2024-01-01T12:01:00').toLocaleString())
      ).not.toBeNull()
      expect(
        await screen.findByText(new Date('2024-01-01T12:04:00').toLocaleString())
      ).not.toBeNull()
      expect(
        await screen.findByText(new Date('2024-01-01T12:06:00').toLocaleString())
      ).not.toBeNull()
    })

    it('sends a restore request for the selected snapshot', async () => {
      const user = userEvent.setup()
      mockStatesQuery(snapshotHistory([2, 5, 7]))

      renderGameControls()
      await user.click(button(/history/i))
      await user.click(await screen.findByText('Step 5'))

      expect(mockRestoreState).toHaveBeenCalledWith({
        sessionId: SESSION_ID,
        projectId: PROJECT_ID,
        step: 5,
      })
    })

    it('indicates that no snapshots exist', async () => {
      const user = userEvent.setup()
      mockStatesQuery(snapshotHistory([]))

      renderGameControls()
      await user.click(button(/history/i))

      expect(await screen.findByText(/no saved states yet/i)).not.toBeNull()
    })
  })

  describe('undo', () => {
    it('restores the second-newest snapshot', async () => {
      const user = userEvent.setup()
      mockStatesQuery(snapshotHistory([2, 5, 7]))

      renderGameControls()
      await user.click(button(/undo/i))

      expect(mockRestoreState).toHaveBeenCalledWith({
        sessionId: SESSION_ID,
        projectId: PROJECT_ID,
        step: 5,
      })
    })
  })

  describe('fork', () => {
    it('forks the latest state and navigates to the new session', async () => {
      const user = userEvent.setup()
      mockStatesQuery(snapshotHistory([2, 5, 7]))

      renderGameControls()
      await user.click(button(/fork/i))

      expect(mockForkState).toHaveBeenCalledWith({
        sessionId: SESSION_ID,
        projectId: PROJECT_ID,
        step: -1,
      })
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/player/fork-1')
      })
    })
  })

  describe('end game', () => {
    it('ends the session', async () => {
      const user = userEvent.setup()

      renderGameControls()
      await user.click(button(/end game/i))

      expect(mockEndGame).toHaveBeenCalledWith({
        sessionId: SESSION_ID,
        projectId: PROJECT_ID,
      })
    })
  })

  describe('reset', () => {
    it('sends the reset request only after confirmation', async () => {
      const user = userEvent.setup()
      vi.mocked(useShowConfirmationModal).mockReturnValue(() => Promise.resolve(true))

      renderGameControls()
      await user.click(button(/reset/i))

      await waitFor(() => {
        expect(mockResetSession).toHaveBeenCalledWith({
          sessionId: SESSION_ID,
          projectId: PROJECT_ID,
        })
      })
    })

    it('does not send a reset request when canceled', async () => {
      const user = userEvent.setup()
      vi.mocked(useShowConfirmationModal).mockReturnValue(() => Promise.resolve(false))

      renderGameControls()
      await user.click(button(/reset/i))

      expect(mockResetSession).not.toHaveBeenCalled()
    })
  })
})
