import { Button, Center, Stack } from '@mantine/core'
import { IconPlayerPlay } from '@tabler/icons-react'
import { useLocation } from 'wouter'

import { useShowError } from '@/hooks/notifications'
import chatApi from '@/services/chat'
import { iconSizeProps } from '@/utils'

function NewStory() {
  const [_location, navigate] = useLocation()
  const [createChat, { isLoading }] = chatApi.useCreateChatMutation()
  const showError = useShowError()

  const start = async () => {
    try {
      const { id } = await createChat({}).unwrap()
      navigate(`/player/story/${id}`)
    } catch (err) {
      showError('Failed to create story chat!', err)
    }
  }

  return (
    <Center h="100%">
      <Stack ta="center">
        <Button
          leftSection={<IconPlayerPlay {...iconSizeProps('lg')} />}
          loading={isLoading}
          onClick={() => void start()}
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
