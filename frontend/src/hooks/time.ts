import prettyMilliseconds from 'pretty-ms'
import { useSyncExternalStore } from 'react'

interface TimeStore {
  subscribe: (onStoreChange: () => void) => () => void
  getSnapshot: () => number
}

// Global registry to share stores across components requesting the same interval
const storeRegistry = new Map<number, TimeStore>()

function createTimeStore(intervalMs: number): TimeStore {
  let snapshot = Date.now()
  let intervalId: ReturnType<typeof setInterval> | null = null
  const subscribers = new Set<() => void>()

  const subscribe = (onStoreChange: () => void) => {
    subscribers.add(onStoreChange)

    // Start the interval only when the first subscriber connects
    if (!intervalId) {
      snapshot = Date.now()
      intervalId = setInterval(() => {
        snapshot = Date.now() // Update stable snapshot
        for (const cb of subscribers) {
          // Notify React to re-render
          cb()
        }
      }, intervalMs)
    }

    // Cleanup when a component unmounts
    return () => {
      subscribers.delete(onStoreChange)
      if (subscribers.size === 0 && intervalId) {
        clearInterval(intervalId)
        intervalId = null
      }
    }
  }

  // React requires this to return the exact same value between interval ticks
  const getSnapshot = () => snapshot

  return { subscribe, getSnapshot }
}

const getServerSnapshot = () => 0

function useNow(intervalMs = 60_000) {
  // Lazily initialize the store for this specific interval duration
  if (!storeRegistry.has(intervalMs)) {
    storeRegistry.set(intervalMs, createTimeStore(intervalMs))
  }

  const entry = storeRegistry.get(intervalMs)
  if (!entry) {
    throw new Error('entry is defined here')
  }

  const { subscribe, getSnapshot } = entry

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}

function formatDuration(millis: number): string {
  return prettyMilliseconds(millis, {
    verbose: true,
    unitCount: 2,
  })
}

export { formatDuration, useNow }
