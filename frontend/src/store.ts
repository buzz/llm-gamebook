import { configureStore } from '@reduxjs/toolkit'

import modelConfigApi from './services/model-config'
import projectApi from './services/project'
import sessionApi from './services/session'

const store = configureStore({
  reducer: {
    [modelConfigApi.reducerPath]: modelConfigApi.reducer,
    [projectApi.reducerPath]: projectApi.reducer,
    [sessionApi.reducerPath]: sessionApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    // eslint-disable-next-line unicorn/prefer-spread
    getDefaultMiddleware().concat(
      modelConfigApi.middleware,
      projectApi.middleware,
      sessionApi.middleware
    ),
})

type RootState = ReturnType<typeof store.getState>
type AppDispatch = typeof store.dispatch

export type { AppDispatch, RootState }
export default store
