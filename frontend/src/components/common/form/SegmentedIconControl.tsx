import { Center, SegmentedControl } from '@mantine/core'
import { useMemo } from 'react'
import type { MantineBreakpoint, SegmentedControlProps } from '@mantine/core'
import type { Icon } from '@tabler/icons-react'

import { iconSizeProps } from '@/utils'
import type { IconSize } from '@/types/common'

import classes from './SegmentedIconControl.module.css'

interface SegmentedIconControlItem<T extends string> {
  value: T
  label: string
  icon: Icon
  disabled?: boolean
}

type Value = readonly SegmentedIconControlItem<string>[]
type BaseSegmentedControlProps = Omit<SegmentedControlProps, 'data' | 'onChange'>
type ValueOf<T> = T extends readonly SegmentedIconControlItem<infer V>[] ? V : never

interface SegmentedIconControlProps<T extends Value> extends BaseSegmentedControlProps {
  data: T
  iconSize?: IconSize
  labelsVisibleFrom?: MantineBreakpoint
  onChange?: (value: ValueOf<T>) => void
}

function SegmentedIconControl<T extends Value>({
  data,
  iconSize = 'sm',
  labelsVisibleFrom = 'md',
  onChange,
  ...otherProps
}: SegmentedIconControlProps<T>) {
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

  return (
    <SegmentedControl
      data={controlData}
      onChange={
        onChange
          ? (value) => {
              onChange(value as ValueOf<T>)
            }
          : undefined
      }
      {...otherProps}
    />
  )
}

export type { SegmentedIconControlProps }
export default SegmentedIconControl
