import { assertNever } from './types/common'

interface IconProps {
  size: number
  stroke: number
}

function iconSizeProps(size: 'lg' | 'md' | 'sm'): IconProps {
  switch (size) {
    case 'lg':
      return { size: 30, stroke: 2 }
    case 'md':
      return { size: 24, stroke: 1.5 }
    case 'sm':
      return { size: 20, stroke: 1 }
    default:
      assertNever(size)
  }
}

function truncate(str: string, maxLength = 200) {
  return str.length > maxLength ? str.slice(0, maxLength) + '…' : str
}

export { iconSizeProps, truncate }
