## 1. Implement ProjectForm Component

- [x] 1.1 Implement form in existing `ProjectForm.tsx` using Mantine `useForm`
- [x] 1.2 Add namespace field (required, TextInput, kebab-case validation)
- [x] 1.3 Add name field (required, TextInput, kebab-case validation)
- [x] 1.4 Add title field (required, TextInput)
- [x] 1.5 Add description field (optional, Textarea)
- [x] 1.6 Add author field (optional, TextInput)
- [x] 1.7 Add client-side validation for required fields
- [x] 1.8 Add loading state with disabled submit button during submission

## 2. API Integration

- [x] 2.1 Use existing `projectApi.createProject` mutation from services/project.ts
- [x] 2.2 Handle successful submission - navigate to `/gamebook/ID` (gamebook detail page) and show success notification
- [x] 2.3 Handle API errors - display error message with Alert

## 3. Navigation

- [x] 3.1 Verify existing "New Gamebook" link in navbar links to `/gamebook/new`
