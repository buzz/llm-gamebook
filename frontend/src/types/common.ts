/** Type guard for `object`. */
function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Utility function to be used as exhaustion check. */
function assertNever(value: never): never {
  // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
  throw new Error(`This code should never be reached. Value='${value}'`)
}

export { assertNever, isObject }
