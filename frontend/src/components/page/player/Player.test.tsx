import { MantineProvider } from '@mantine/core'
import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useParams } from 'wouter'

import { PortalProvider } from '@/contexts/PortalContext'
import useMessages from '@/hooks/messages'
import { useShowError } from '@/hooks/notifications'
import sessionApi from '@/services/session'
import type { SessionFull } from '@/types/api'

import Player from './Player'

// Mock modules
vi.mock('@/components/page/player/PlayerToolbar', () => ({ default: () => null }))
vi.mock('@/hooks/messages')
vi.mock('@/hooks/notifications')
vi.mock('@/services/session')
vi.mock('wouter')

const SESSION_ID = 'session-1'
const PROJECT_ID = 'llm-gamebook/test'

function makeSessionFull(overrides: Partial<SessionFull> = {}): SessionFull {
  return {
    id: SESSION_ID,
    projectId: PROJECT_ID,
    messageCount: 0,
    messages: [],
    endedAt: null,
    ...overrides,
  }
}

function mockSessionQuery(session: SessionFull) {
  vi.mocked(sessionApi.useGetSessionByIdQuery).mockReturnValue({
    data: session,
    isLoading: false,
  } as never)
}

function renderPlayer(session: SessionFull) {
  mockSessionQuery(session)
  return render(
    <MantineProvider>
      <PortalProvider>
        <Player />
      </PortalProvider>
    </MantineProvider>
  )
}

beforeEach(() => {
  vi.clearAllMocks()

  vi.mocked(useParams).mockReturnValue({ id: SESSION_ID })
  vi.mocked(useMessages).mockReturnValue({
    currentPartId: null,
    messages: [],
    streamStatus: 'done',
  } as never)
  vi.mocked(useShowError).mockReturnValue(vi.fn())
  vi.mocked(sessionApi.useUpdateSessionMutation).mockReturnValue([
    vi.fn(),
    { isLoading: false },
  ] as never)
  vi.mocked(sessionApi.useCreateRequestMutation).mockReturnValue([
    vi.fn(),
    { isLoading: false },
  ] as never)
})

describe('Player ended display', () => {
  it('shows an ended banner and disables the input and send action', () => {
    renderPlayer(makeSessionFull({ endedAt: '2024-01-01T00:00:00' }))

    expect(screen.getByText(/game over/i)).not.toBeNull()
    expect(screen.getByRole('textbox', { name: /user message/i }).hasAttribute('disabled')).toBe(
      true
    )
    expect(screen.getByRole('button', { name: /send/i }).hasAttribute('disabled')).toBe(true)
  })

  it('shows no banner and keeps the input enabled for active sessions', () => {
    renderPlayer(makeSessionFull())

    expect(screen.queryByText(/game over/i)).toBeNull()
    expect(screen.getByRole('textbox', { name: /user message/i }).hasAttribute('disabled')).toBe(
      false
    )
    expect(screen.getByRole('button', { name: /send/i }).hasAttribute('disabled')).toBe(false)
  })
})
