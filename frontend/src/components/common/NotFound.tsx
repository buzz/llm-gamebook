import { Alert, Button, Center, Stack } from '@mantine/core'
import { IconHome, IconInfoCircle } from '@tabler/icons-react'
import { Link } from 'wouter'

import { iconSizeProps } from '@/utils'

interface NotFoundProps {
  title?: string
  message?: string
}

function NotFound({
  title = 'Page not found',
  message = 'This page does not exist.',
}: NotFoundProps) {
  return (
    <Center h="100%">
      <Alert
        color="blue"
        icon={<IconInfoCircle {...iconSizeProps('lg')} />}
        title={title}
        variant="light"
      >
        <Stack>
          {message}
          <Button component={Link} leftSection={<IconHome {...iconSizeProps('md')} />} to="/">
            Home
          </Button>
        </Stack>
      </Alert>
    </Center>
  )
}

export default NotFound
