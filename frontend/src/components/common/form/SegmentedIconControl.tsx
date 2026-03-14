import { Center, SegmentedControl } from '@mantine/core'
import { useMemo } from 'react'
import type { MantineBreakpoint, SegmentedControlProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'
import type { IconSize } from '@/types/common'

import classes from './SegmentedIconControl.module.css'

interface SegmentedIconControlItem {
  value: string
  label: string
  icon: Icon
  disabled?: boolean
}

interface SegmentedIconControlProps extends Omit<SegmentedControlProps, 'data'> {
  data: readonly SegmentedIconControlItem[]
  iconSize?: IconSize
  labelsVisibleFrom?: MantineBreakpoint
}

function SegmentedIconControl({
  data,
  iconSize = 'sm',
  labelsVisibleFrom = 'md',
  ...otherProps
}: SegmentedIconControlProps) {
  const controlData = useMemo(
    () =>
      data.map(({ value, label, icon: Icon, disabled }) => ({
        value,
        label: (
          <Center className={classes.segment}>
            <Icon {...iconSizeProps(iconSize)} />
            <span className={`mantine-visible-from-${labelsVisibleFrom}`}>{label}</span>
          </Center>
        ),
        disabled,
      })),
    [data, iconSize, labelsVisibleFrom]
  )

  return <SegmentedControl data={controlData} {...otherProps} />
}

export type { SegmentedIconControlProps }
export default SegmentedIconControl
