import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type {
  ModelRequest,
  ModelRequestCreate,
  ServerMessage,
  Session,
  SessionCreate,
  SessionFull,
  Sessions,
  SessionUpdate,
} from '@/types/api'

const sessionApi = createApi({
  reducerPath: 'sessionApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/sessions/' }),
  tagTypes: ['Session'],
  endpoints: (build) => ({
    getSessionById: build.query<SessionFull, string>({
      query: (id) => id,
      providesTags: (_result, _error, id) => [{ type: 'Session', id }],
    }),

    getSessions: build.query<Sessions, void>({
      query: () => '',
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Session' as const, id })),
              { type: 'Session', id: 'LIST' },
            ]
          : [{ type: 'Session', id: 'LIST' }],
    }),

    createSession: build.mutation<Session, SessionCreate>({
      query: (session) => ({
        url: '',
        method: 'POST',
        body: session,
      }),
      invalidatesTags: [{ type: 'Session', id: 'LIST' }],
    }),

    updateSession: build.mutation<ServerMessage, { id: string } & SessionUpdate>({
      query: ({ id, config_id }) => ({
        url: id,
        method: 'PATCH',
        body: { config_id },
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'Session', id }],
    }),

    deleteSession: build.mutation<ServerMessage, string>({
      query: (id) => ({
        url: id,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'Session', id },
        { type: 'Session', id: 'LIST' },
      ],
    }),

    createRequest: build.mutation<ModelRequest, { sessionId: string; request: ModelRequestCreate }>(
      {
        query: ({ sessionId, request }) => ({
          url: `${sessionId}/request`,
          method: 'POST',
          body: request,
        }),
        invalidatesTags: (_result, _error, { sessionId }) => [{ type: 'Session', id: sessionId }],
      }
    ),
  }),
})

export default sessionApi
