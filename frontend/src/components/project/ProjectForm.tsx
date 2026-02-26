import { Alert, Button, Group, Stack, Textarea, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { IconBook, IconPlus } from '@tabler/icons-react'

import PageShell from '@/components/layout/PageShell'
import { KEBAB_CASE_PATTERN } from '@/constants'
import { useCreateProject } from '@/hooks/project'
import { iconSizeProps } from '@/utils'

interface FormData {
  namespace: string
  name: string
  title: string
  description: string
  author: string
}

const KEBAB_CASE_REGEX = new RegExp(`^${KEBAB_CASE_PATTERN}$`)

function ProjectForm() {
  const { createProject, isLoading } = useCreateProject()

  const form = useForm<FormData>({
    initialValues: {
      namespace: '',
      name: '',
      title: '',
      description: '',
      author: '',
    },
    validate: {
      namespace: (value) => {
        if (value.length === 0) {
          return 'Namespace is required'
        }
        if (!KEBAB_CASE_REGEX.test(value)) {
          return 'Namespace must be kebab-case (lowercase letters, numbers, hyphens)'
        }
        return null
      },
      name: (value) => {
        if (value.length === 0) {
          return 'Name is required'
        }
        if (!KEBAB_CASE_REGEX.test(value)) {
          return 'Name must be kebab-case (lowercase letters, numbers, hyphens)'
        }
        return null
      },
      title: (value) => (value.length === 0 ? 'Title is required' : null),
    },
  })

  const handleSubmit = form.onSubmit(async (values) => {
    if (isLoading) {
      return
    }

    await createProject({
      id: `${values.namespace}/${values.name}`,
      title: values.title,
      description: values.description || undefined,
      author: values.author || undefined,
    })
  })

  const footer = (
    <Group justify="flex-end">
      <Button
        loading={isLoading}
        leftSection={<IconPlus {...iconSizeProps('md')} />}
        size="lg"
        type="submit"
      >
        Create
      </Button>
    </Group>
  )

  return (
    <form aria-disabled={isLoading} onSubmit={handleSubmit}>
      <PageShell footer={footer} icon={IconBook} title="Create Gamebook">
        <Stack gap="md">
          <Group align="flex-end" gap="xs">
            <TextInput
              disabled={isLoading}
              label="ID"
              placeholder="your-username"
              required
              style={{ flex: 1 }}
              {...form.getInputProps('namespace')}
            />
            <div style={{ paddingBottom: '10px', fontSize: '18px' }}>/</div>
            <TextInput disabled={isLoading} style={{ flex: 1 }} {...form.getInputProps('name')} />
          </Group>
          <TextInput
            disabled={isLoading}
            label="Title"
            placeholder="My Amazing Gamebook"
            required
            {...form.getInputProps('title')}
          />
          <Textarea
            disabled={isLoading}
            label="Description"
            placeholder="A brief description of your gamebook..."
            {...form.getInputProps('description')}
          />
          <TextInput
            disabled={isLoading}
            label="Author"
            placeholder="Your Name"
            {...form.getInputProps('author')}
          />
          {Object.keys(form.errors).length > 0 && (
            <Alert color="red" variant="light">
              Please fix the errors above before submitting.
            </Alert>
          )}
        </Stack>
      </PageShell>
    </form>
  )
}

export default ProjectForm
