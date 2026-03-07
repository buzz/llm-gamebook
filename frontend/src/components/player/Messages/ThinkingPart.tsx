import { Button, Collapse } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconBrain, IconChevronDown } from '@tabler/icons-react'
import cx from 'clsx'
import { useEffect, useState } from 'react'
import { Streamdown } from 'streamdown'

import { iconSizeProps } from '@/utils'
import type { ThinkingPart as ThinkingPartType } from '@/types/api'

import classes from './Messages.module.css'

interface ThinkingDurationLabelProps {
  timestamp: string
  durationSecs: number | null
  isStreaming: boolean
}

function formatDuration(totalSecs: number): string {
  const mins = Math.floor(totalSecs / 60)
  const secs = totalSecs % 60

  if (mins === 0) {
    return `${String(secs)} second${secs === 1 ? '' : 's'}`
  }
  if (secs === 0) {
    return `${String(mins)} minute${mins === 1 ? '' : 's'}`
  }
  return (
    `${String(mins)} minute${mins === 1 ? '' : 's'} ` +
    `${String(secs)} second${secs === 1 ? '' : 's'}`
  )
}

function calculateDeltaSecs(startMillis: number): number {
  return Math.floor((Date.now() - startMillis) / 1000)
}

function ThinkingDurationLabel({
  timestamp,
  durationSecs,
  isStreaming,
}: ThinkingDurationLabelProps) {
  const startMillis = Date.parse(timestamp)
  const [deltaSecs, setDeltaSecs] = useState<number | null>(() => calculateDeltaSecs(startMillis))

  useEffect(() => {
    if (!isStreaming) {
      return
    }

    const id = globalThis.setInterval(() => {
      setDeltaSecs(calculateDeltaSecs(startMillis))
    }, 1000)

    return () => {
      globalThis.clearInterval(id)
    }
  }, [isStreaming, startMillis])

  const secs = deltaSecs ?? durationSecs

  if (secs == null) {
    return <>Thoughts</>
  }

  return (
    <>
      {isStreaming ? 'Thinking for' : 'Thought for'} {formatDuration(secs)}
      {isStreaming && '…'}
    </>
  )
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
