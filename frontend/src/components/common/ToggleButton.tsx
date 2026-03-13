import { Button, createPolymorphicComponent } from '@mantine/core'
import { IconChevronDown } from '@tabler/icons-react'
import cx from 'clsx'
import type { ButtonProps } from '@mantine/core'

import { iconSizeProps } from '@/utils'

import classes from './ToggleButton.module.css'

interface ToggleButtonProps extends ButtonProps {
  opened: boolean
}

const ToggleButton = createPolymorphicComponent<'button', ToggleButtonProps>(function ToggleButton({
  opened,
  children,
  ref,
  ...otherProps
}: ToggleButtonProps & { ref?: React.RefObject<HTMLButtonElement | null> }) {
  return (
    <Button
      classNames={{
        root: classes.toggleBtn,
        inner: classes.toggleBtnInner,
      }}
      fullWidth
      leftSection={
        <IconChevronDown
          className={cx(classes.chevron, classes[opened ? 'rot-180' : 'rot-0'])}
          {...iconSizeProps('md')}
        />
      }
      variant="transparent"
      {...otherProps}
      ref={ref}
    >
      {children}
    </Button>
  )
})

export default ToggleButton
