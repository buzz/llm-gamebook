import { IconBrightnessAuto, IconMoon, IconSun } from '@tabler/icons-react'

import SegmentedIconControl from './SegmentedIconControl'
import type { SegmentedIconControlProps } from './SegmentedIconControl'

const colorSchemeControlData = [
  {
    value: 'auto',
    label: 'Auto',
    icon: IconBrightnessAuto,
  },
  {
    value: 'light',
    label: 'Light',
    icon: IconSun,
  },
  {
    value: 'dark',
    label: 'Dark',
    icon: IconMoon,
  },
] as const

type TypedSegmentedIconControlProps = SegmentedIconControlProps<typeof colorSchemeControlData>
type ColorSchemeControlProps = Omit<TypedSegmentedIconControlProps, 'data'>

function ColorSchemeControl(props: ColorSchemeControlProps) {
  return <SegmentedIconControl data={colorSchemeControlData} {...props} />
}

export default ColorSchemeControl
