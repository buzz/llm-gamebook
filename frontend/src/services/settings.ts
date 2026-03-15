import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type { ServerMessage, UserSettings } from '@/types/api'

const userSettingsApi = createApi({
  reducerPath: 'userSettingsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/settings/' }),
  tagTypes: ['UserSettings'],
  endpoints: (build) => ({
    getUserSettings: build.query<UserSettings, void>({
      query: () => '',
      providesTags: ['UserSettings'],
    }),

    updateUserSettings: build.mutation<ServerMessage, UserSettings>({
      query: (update) => ({
        url: '',
        method: 'PUT',
        body: update,
      }),
      invalidatesTags: ['UserSettings'],
    }),
  }),
})

export default userSettingsApi
