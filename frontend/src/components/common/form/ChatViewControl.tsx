import { IconBug, IconEye, IconListDetails } from '@tabler/icons-react'

import SegmentedIconControl from './SegmentedIconControl'
import type { SegmentedIconControlProps } from './SegmentedIconControl'

const viewControlData = [
  {
    value: 'standard',
    label: 'Standard',
    icon: IconEye,
  },
  {
    value: 'details',
    label: 'Details',
    icon: IconListDetails,
  },
  {
    value: 'debug',
    label: 'Debug',
    icon: IconBug,
  },
] as const

type ChatViewControlProps = Omit<SegmentedIconControlProps, 'data'>

function ChatViewControl(props: ChatViewControlProps) {
  return <SegmentedIconControl data={viewControlData} {...props} />
}

export default ChatViewControl
