import { Button, Collapse } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconBrain, IconChevronDown } from '@tabler/icons-react'
import { clsx } from 'clsx'
import { useEffect, useRef, useState } from 'react'
import { Streamdown } from 'streamdown'

import { iconSizeProps } from '@/utils'
import type { ThinkingPart as ThinkingPartType } from '@/types/api'

import classes from './Messages.module.css'

interface ThinkingPartProperties {
  isStreaming: boolean
  part: ThinkingPartType
}

function ThinkingPart({ isStreaming, part }: ThinkingPartProperties) {
  const [thinkingOpened, { toggle, close, open }] = useDisclosure(false)
  const mountTime = useRef<number | null>(null)
  const [deltaSecs, setDeltaSecs] = useState<number | null>(null)

  useEffect(() => {
    let timerIntervalId: number | null = null
    let closeTimeoutId: number | null = null

    if (isStreaming) {
      open()
      mountTime.current ??= Date.now() // Remember time on mount
      setDeltaSecs(Math.floor((Date.now() - mountTime.current) / 1000))

      // Start interval to update every second
      timerIntervalId = globalThis.setInterval(() => {
        if (mountTime.current !== null) {
          setDeltaSecs(Math.floor((Date.now() - mountTime.current) / 1000))
        }
      }, 1000)
    } else {
      // Auto-collapse if we have been streaming
      if (mountTime.current !== null) {
        closeTimeoutId = globalThis.setTimeout(() => {
          close()
        }, 1000)
      }
    }

    return () => {
      if (timerIntervalId) {
        globalThis.clearInterval(timerIntervalId)
      }
      if (closeTimeoutId) {
        globalThis.clearTimeout(closeTimeoutId)
      }
    }
  }, [close, isStreaming, open])

  const label =
    deltaSecs === null
      ? part.duration_seconds === null
        ? 'Thoughts'
        : `Thought for ${part.duration_seconds.toString()} seconds`
      : isStreaming
        ? `Thinking for ${deltaSecs.toString()} seconds…`
        : `Thought for ${deltaSecs.toString()} seconds`

  return (
    <div className={classes.thinkingPart}>
      <Button
        classNames={{ root: classes.toggleBtn, inner: classes.toggleBtnInner }}
        fullWidth
        leftSection={<IconBrain {...iconSizeProps('sm')} />}
        rightSection={
          <IconChevronDown
            className={clsx(classes.chevron, classes[thinkingOpened ? 'rot-180' : 'rot-0'])}
            {...iconSizeProps('sm')}
          />
        }
        onClick={toggle}
        size="xs"
        variant="transparent"
      >
        {label}
      </Button>
      <Collapse in={thinkingOpened}>
        <Streamdown className={clsx(classes.thinkingText, classes.text)}>{part.content}</Streamdown>
      </Collapse>
    </div>
  )
}

export default ThinkingPart
