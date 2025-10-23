import { configureStore } from '@reduxjs/toolkit'

import sessionApi from './services/session'

export const store = configureStore({
  reducer: {
    [sessionApi.reducerPath]: sessionApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(sessionApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
