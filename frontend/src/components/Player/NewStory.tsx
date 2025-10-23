import { Button, Center, Stack } from '@mantine/core'
import { IconPlayerPlay } from '@tabler/icons-react'

import { useCreateSession } from '@/hooks/session'
import { iconSizeProps } from '@/utils'

function NewStory() {
  const { createSession, isLoading } = useCreateSession()

  return (
    <Center h="100%">
      <Stack ta="center">
        <Button
          leftSection={<IconPlayerPlay {...iconSizeProps('lg')} />}
          loading={isLoading}
          onClick={() => void createSession()}
          size="xl"
          type="submit"
          variant="filled"
        >
          Start Story
        </Button>
      </Stack>
    </Center>
  )
}

export default NewStory
