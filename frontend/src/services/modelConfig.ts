import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import type {
  ModelConfig,
  ModelConfigCreate,
  ModelConfigs,
  ModelConfigUpdate,
  ModelProviders,
  ServerMessage,
} from '@/types/api'

const modelConfigApi = createApi({
  reducerPath: 'modelConfigApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/model-configs/' }),
  tagTypes: ['ModelConfig'],
  endpoints: (build) => ({
    getModelConfigs: build.query<ModelConfigs, void>({
      query: () => '',
      providesTags: (result) => {
        return result
          ? [
              ...result.data.map(({ id }) => ({ type: 'ModelConfig' as const, id })),
              { type: 'ModelConfig', id: 'LIST' },
            ]
          : [{ type: 'ModelConfig', id: 'LIST' }]
      },
    }),

    getModelConfig: build.query<ModelConfig, string>({
      query: (id) => id,
      providesTags: (_result, _error, id) => [{ type: 'ModelConfig', id }],
    }),

    createModelConfig: build.mutation<ModelConfig, ModelConfigCreate>({
      query: (config) => ({
        url: '',
        method: 'POST',
        body: config,
      }),
      invalidatesTags: [{ type: 'ModelConfig', id: 'LIST' }],
    }),

    updateModelConfig: build.mutation<ServerMessage, { id: string; config: ModelConfigUpdate }>({
      query: ({ id, config }) => ({
        url: id,
        method: 'PUT',
        body: config,
      }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: 'ModelConfig', id },
        { type: 'ModelConfig', id: 'LIST' },
      ],
    }),

    deleteModelConfig: build.mutation<ServerMessage, string>({
      query: (id) => ({
        url: id,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: 'ModelConfig', id },
        { type: 'ModelConfig', id: 'LIST' },
      ],
    }),

    getProviders: build.query<ModelProviders, void>({
      query: () => 'providers/',
    }),
  }),
})

export default modelConfigApi
