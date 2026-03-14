interface ErrorDisplay {
  /** Error name. */
  name: string

  /** Error message. */
  message: string | null

  /** Error details like stack or validation issues. */
  details: string | null
}

type IconSize = 'lg' | 'md' | 'sm'

export type { ErrorDisplay, IconSize }
