import { configureStore } from '@reduxjs/toolkit'

import chatApi from './services/chat'

export const store = configureStore({
  reducer: {
    [chatApi.reducerPath]: chatApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(chatApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
