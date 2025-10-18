import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type { ChatCreate, ChatPublic, ChatsPublic, ServerMessage } from '@/types/api'

const chatApi = createApi({
  reducerPath: 'chatApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/chats/' }),
  tagTypes: ['Chat'],
  endpoints: (build) => ({
    getChatById: build.query<ChatPublic, string>({
      query: (id) => id,
      providesTags: (_result, _error, id) => [{ type: 'Chat', id }],
    }),
    getChats: build.query<ChatsPublic, void>({
      query: () => '',
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Chat' as const, id })),
              { type: 'Chat', id: 'LIST' },
            ]
          : [{ type: 'Chat', id: 'LIST' }],
    }),
    createChat: build.mutation<ChatPublic, ChatCreate>({
      query: (body) => ({
        url: '',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Chat', id: 'LIST' }],
    }),
    deleteChat: build.mutation<ServerMessage, string>({
      query: (id) => ({
        url: id,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'Chat', id },
        { type: 'Chat', id: 'LIST' },
      ],
    }),
  }),
})

export default chatApi
