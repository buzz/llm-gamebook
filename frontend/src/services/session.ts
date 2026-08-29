import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type {
  ModelRequest,
  ModelRequestCreate,
  paths,
  ServerMessage,
  Session,
  SessionCreate,
  SessionFull,
  Sessions,
  SessionUpdate,
  StateHistory,
} from '@/types/api'

/** Helper function to handle the global and project-specific list tags. */
function getListTags(projectId?: string | null) {
  const tags = [{ type: 'Session' as const, id: 'LIST' }]
  if (projectId) {
    tags.push({ type: 'Session' as const, id: `LIST_${projectId}` })
  }
  return tags
}

const sessionApi = createApi({
  reducerPath: 'sessionApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/sessions/' }),
  tagTypes: ['Session'],
  endpoints: (build) => ({
    getSessionById: build.query<SessionFull, string>({
      query: (id) => id,
      providesTags: (_result, _error, id) => [{ type: 'Session', id }],
    }),

    getSessions: build.query<Sessions, { projectId?: string; skip?: number; limit?: number }>({
      query: ({ projectId, skip, limit }) => ({
        url: '',
        params: {
          project_id: projectId,
          skip,
          limit,
        } satisfies paths['/api/sessions/']['get']['parameters']['query'],
      }),
      providesTags: (result, _error, args) => [
        ...(result?.data.map(({ id }) => ({ type: 'Session' as const, id })) ?? []),
        ...getListTags(args.projectId),
      ],
    }),

    createSession: build.mutation<Session, SessionCreate>({
      query: (session) => ({
        url: '',
        method: 'POST',
        body: session,
      }),
      invalidatesTags: (_result, _error, session) => getListTags(session.projectId),
    }),

    updateSession: build.mutation<
      ServerMessage,
      { sessionId: string; projectId: string } & SessionUpdate
    >({
      query: ({ sessionId, configId }) => ({
        url: sessionId,
        method: 'PATCH',
        body: { configId },
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', sessionId },
        ...getListTags(projectId),
      ],
    }),

    deleteSession: build.mutation<ServerMessage, { sessionId: string; projectId: string }>({
      query: ({ sessionId }) => ({
        url: sessionId,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    createRequest: build.mutation<
      ModelRequest,
      { sessionId: string; projectId: string; request: ModelRequestCreate }
    >({
      query: ({ sessionId, request }) => ({
        url: `${sessionId}/request`,
        method: 'POST',
        body: request,
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    restoreState: build.mutation<
      ServerMessage,
      { sessionId: string; projectId: string; step: number }
    >({
      query: ({ sessionId, step }) => ({
        url: `${sessionId}/restore`,
        method: 'POST',
        body: { step },
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    forkState: build.mutation<SessionFull, { sessionId: string; projectId: string; step: number }>({
      query: ({ sessionId, step }) => ({
        url: `${sessionId}/fork`,
        method: 'POST',
        body: { step },
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    endGame: build.mutation<
      ServerMessage,
      { sessionId: string; projectId: string; reason?: string }
    >({
      query: ({ sessionId, reason }) => ({
        url: `${sessionId}/end-game`,
        method: 'POST',
        body: reason === undefined ? {} : { reason },
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    resetSession: build.mutation<ServerMessage, { sessionId: string; projectId: string }>({
      query: ({ sessionId }) => ({
        url: `${sessionId}/reset`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _error, { sessionId, projectId }) => [
        { type: 'Session', id: sessionId },
        ...getListTags(projectId),
      ],
    }),

    // Consumed lazily via useLazyGetStatesQuery (e.g. by the player toolbar).
    getStates: build.query<StateHistory, string>({
      query: (id) => `${id}/states`,
      providesTags: (_result, _error, id) => [{ type: 'Session', id: `STATES_${id}` }],
    }),
  }),
})

export default sessionApi
