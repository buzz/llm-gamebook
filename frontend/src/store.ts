import { configureStore } from '@reduxjs/toolkit'

import sessionApi from './services/session'

export const store = configureStore({
  reducer: {
    [sessionApi.reducerPath]: sessionApi.reducer,
  },
  // eslint-disable-next-line unicorn/prefer-spread
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(sessionApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
