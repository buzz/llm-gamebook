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

    getSessions: build.query<Sessions, paths['/api/sessions/']['get']['parameters']['query']>({
      query: (params) => ({ url: '', params }),
      providesTags: (result, _error, args) => [
        ...(result?.data.map(({ id }) => ({ type: 'Session' as const, id })) ?? []),
        ...getListTags(args?.project_id),
      ],
    }),

    createSession: build.mutation<Session, SessionCreate>({
      query: (session) => ({
        url: '',
        method: 'POST',
        body: session,
      }),
      invalidatesTags: (_result, _error, session) => getListTags(session.project_id),
    }),

    updateSession: build.mutation<
      ServerMessage,
      { sessionId: string; projectId: string } & SessionUpdate
    >({
      query: ({ sessionId, config_id }) => ({
        url: sessionId,
        method: 'PATCH',
        body: { config_id },
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
  }),
})

export default sessionApi
