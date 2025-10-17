import { Button, Center, Stack } from '@mantine/core'
import { IconPlayerPlay } from '@tabler/icons-react'

function NewStory() {
  return (
    <Center h="100%">
      <Stack ta="center">
        <Button leftSection={<IconPlayerPlay />} size="xl" type="submit" variant="filled">
          Start Story
        </Button>
      </Stack>
    </Center>
  )
}

export default NewStory
