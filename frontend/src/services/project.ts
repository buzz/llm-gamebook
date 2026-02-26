import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type {
  ProjectBasic,
  ProjectCreate,
  ProjectDetail,
  Projects,
  ServerMessage,
} from '@/types/api'

const projectApi = createApi({
  reducerPath: 'projectApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/projects/' }),
  tagTypes: ['Project'],
  endpoints: (build) => ({
    getProjects: build.query<Projects, void>({
      query: () => '',
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Project' as const, id })),
              { type: 'Project', id: 'LIST' },
            ]
          : [{ type: 'Project', id: 'LIST' }],
    }),

    getProjectById: build.query<ProjectDetail, string>({
      query: (id) => id,
      providesTags: (_result, _error, id) => [{ type: 'Project', id }],
    }),

    createProject: build.mutation<ProjectBasic, ProjectCreate>({
      query: (project) => ({
        url: '',
        method: 'POST',
        body: project,
      }),
      invalidatesTags: [{ type: 'Project', id: 'LIST' }],
    }),

    deleteProject: build.mutation<ServerMessage, string>({
      query: (id) => ({
        url: id,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'Project', id },
        { type: 'Project', id: 'LIST' },
      ],
    }),
  }),
})

export default projectApi
