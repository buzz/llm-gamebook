import { configureStore } from '@reduxjs/toolkit'

import modelConfigApi from './services/modelConfig'
import sessionApi from './services/session'

const store = configureStore({
  reducer: {
    [modelConfigApi.reducerPath]: modelConfigApi.reducer,
    [sessionApi.reducerPath]: sessionApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    // eslint-disable-next-line unicorn/prefer-spread
    getDefaultMiddleware().concat(sessionApi.middleware, modelConfigApi.middleware),
})

type RootState = ReturnType<typeof store.getState>
type AppDispatch = typeof store.dispatch

export type { AppDispatch, RootState }
export default store
