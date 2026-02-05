import { assertNever } from './types/common'

interface IconProps {
  size: number
  stroke: number
}

function iconSizeProps(size: 'lg' | 'md' | 'sm'): IconProps {
  switch (size) {
    case 'lg': {
      return { size: 30, stroke: 2 }
    }
    case 'md': {
      return { size: 24, stroke: 1.5 }
    }
    case 'sm': {
      return { size: 20, stroke: 1 }
    }
    default: {
      assertNever(size)
    }
  }
}

function truncate(string_: string, maxLength = 200) {
  return string_.length > maxLength ? string_.slice(0, maxLength) + '…' : string_
}

export { iconSizeProps, truncate }
