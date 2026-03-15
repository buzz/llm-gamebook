import { Input, Kbd, Stack, Switch, useMantineColorScheme } from '@mantine/core'
import { useForm } from '@mantine/form'
import { IconSettings } from '@tabler/icons-react'

import ChatViewControl from '@/components/common/form/ChatViewControl'
import ColorSchemeControl from '@/components/common/form/ColorSchemeControl'
import PageShell from '@/components/common/PageShell'
import QueryHandler from '@/components/common/QueryHandler'
import { useUpdateUserSettings } from '@/hooks/settings'
import userSettingsApi from '@/services/settings'
import type { UserSettings } from '@/types/api'

interface SettingsFormLoadedProps {
  settings: UserSettings
}

function SettingsFormLoaded({ settings }: SettingsFormLoadedProps) {
  const { setColorScheme } = useMantineColorScheme()

  const { updateUserSettings, isLoading: isUpdating } = useUpdateUserSettings()

  const form = useForm<UserSettings>({
    initialValues: { ...settings },
    onValuesChange: (values) => {
      if (isUpdating) {
        return
      }

      void updateUserSettings(values)
    },
  })

  return (
    <PageShell icon={IconSettings} title="Settings">
      <Stack gap="md">
        {/* Color scheme is stored in browser */}
        <Input.Wrapper label="Color Scheme">
          <ColorSchemeControl
            fullWidth
            iconSize="md"
            labelsVisibleFrom="xs"
            onChange={(value) => {
              setColorScheme(value)
            }}
          />
        </Input.Wrapper>

        <form>
          <Input.Wrapper
            description={
              <>
                <span>Control what messages are shown in the chat.</span>
                <br />
                <strong>Standard</strong>: Only user messages and narration.
                <br />
                <strong>Details</strong>: Additionally show thinking
                <br />
                <strong>Debug</strong>: Additionally show tool calls and returns.
              </>
            }
            label="Chat View"
          >
            <ChatViewControl
              fullWidth
              iconSize="md"
              labelsVisibleFrom="xs"
              {...form.getInputProps('chatView')}
            />
          </Input.Wrapper>

          <Switch
            label="Enter submits message"
            description={
              <>
                When <strong>enabled</strong>: <Kbd>Enter</Kbd> sends message and
                <Kbd>Shift</Kbd>+<Kbd>Enter</Kbd> inserts newline.
                <br />
                When <strong>disabled</strong>, <Kbd>Enter</Kbd> inserts newline and <Kbd>Ctrl</Kbd>
                +<Kbd>Enter</Kbd> sends message.
              </>
            }
            {...form.getInputProps('enterSubmitsMessage')}
          />
        </form>
      </Stack>
    </PageShell>
  )
}

function SettingsForm() {
  const result = userSettingsApi.useGetUserSettingsQuery()

  return (
    <QueryHandler result={result}>
      {(settings) => <SettingsFormLoaded settings={settings} />}
    </QueryHandler>
  )
}

export default SettingsForm
