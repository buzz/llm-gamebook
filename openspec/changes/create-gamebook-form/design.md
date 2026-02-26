## Context

Users can browse and play existing gamebooks but cannot create new ones from the UI. The backend already supports project creation via `POST /api/projects/`, but there's no frontend UI for it. This change adds a creation form accessible from the navbar.

Current state:
- Existing stories page at `/` (root) shows available gamebooks
- Backend has `POST /api/projects/` endpoint accepting `ProjectCreate` schema
- Uses Mantine v8 components and wouter for routing

## Goals / Non-Goals

**Goals:**
- Add `/gamebook/new` route with a form for creating new gamebooks
- Form fields: namespace (required, like username), name (required, like repo name), title (required), description (optional), author (optional)
- Submit to existing `POST /api/projects/` endpoint with ID in format `namespace/name`
- Navigate to gamebook details page after successful creation

**Non-Goals:**
- Image upload for project cover (future enhancement)
- Draft saving (future enhancement)

## Decisions

1. **Form validation**: Use Mantine's `useForm` hook for client-side validation
    - Alternative: React Hook Form - chose Mantine native for consistency with existing codebase

2. **Project ID generation**: Client-side, user provides namespace and name (format: `namespace/name`)
    - ID must be kebab-case (lowercase letters, numbers, hyphens)

3. **Source field**: Is set to `"local"` by backend

4. **Navigation after success**: Redirect to gamebook details page to see the new gamebook

## Risks / Trade-offs

- [Risk] API error handling → Display user-friendly error message from API response
- [Risk] Form submission during pending request → Disable submit button while loading
- [Risk] Empty title submission → Client-side validation before submission
