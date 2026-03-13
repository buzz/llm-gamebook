import { Button, Collapse } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconBrain, IconChevronDown } from '@tabler/icons-react'
import cx from 'clsx'
import { useEffect } from 'react'
import { Streamdown } from 'streamdown'

import { formatDuration, useNow } from '@/hooks/time'
import { iconSizeProps } from '@/utils'
import type { ThinkingPart as ThinkingPartType } from '@/types/api'

import classes from './Messages.module.css'

interface PropsWithTimestamp {
  timestamp: string
}

function StreamingDuration({ timestamp }: PropsWithTimestamp) {
  const now = useNow(1000)
  const delta = Math.floor(now - Date.parse(timestamp))

  return <>Thinking for {formatDuration(delta)}…</>
}

interface ThinkingDurationLabelProps extends PropsWithTimestamp {
  durationSecs: number | null
  isStreaming: boolean
}

function ThinkingDurationLabel({
  timestamp,
  durationSecs,
  isStreaming,
}: ThinkingDurationLabelProps) {
  // Only mount the hook-heavy component when streaming is actually active
  if (isStreaming) {
    return <StreamingDuration timestamp={timestamp} />
  }

  // Fallback to static duration
  if (durationSecs != null) {
    return <>Thought for {formatDuration(durationSecs * 1000)}</>
  }

  return <>Thoughts</>
}

interface ThinkingPartProps {
  isStreaming: boolean
  part: ThinkingPartType
}

function ThinkingPart({ isStreaming, part }: ThinkingPartProps) {
  const [thinkingOpened, { toggle, close, open }] = useDisclosure(false)

  // Auto-close after streaming is done
  useEffect(() => {
    let closeTimeoutId: number | null = null
    if (isStreaming) {
      open()
    } else {
      closeTimeoutId = globalThis.setTimeout(() => {
        close()
      }, 1000)
    }
    return () => {
      if (closeTimeoutId) {
        globalThis.clearTimeout(closeTimeoutId)
      }
    }
  }, [isStreaming, close, open])

  return (
    <div className={classes.thinkingPart}>
      {/* TODO: Consolidate with ToggleButton? */}
      <Button
        classNames={{
          root: classes.toggleBtn,
          inner: classes.toggleBtnInner,
          label: isStreaming ? classes.shimmerEffect : undefined,
        }}
        fullWidth
        leftSection={<IconBrain {...iconSizeProps('sm')} />}
        rightSection={
          <IconChevronDown
            className={cx(classes.chevron, classes[thinkingOpened ? 'rot-180' : 'rot-0'])}
            {...iconSizeProps('sm')}
          />
        }
        onClick={toggle}
        size="xs"
        variant="transparent"
      >
        <ThinkingDurationLabel
          timestamp={part.timestamp}
          durationSecs={part.duration_seconds}
          isStreaming={isStreaming}
        />
      </Button>
      <Collapse in={thinkingOpened}>
        <Streamdown
          animated
          isAnimating={isStreaming}
          mode={isStreaming ? 'streaming' : 'static'}
          className={cx(classes.thinkingText, classes.text)}
        >
          {part.content}
        </Streamdown>
      </Collapse>
    </div>
  )
}

export default ThinkingPart
