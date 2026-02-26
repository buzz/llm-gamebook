## Why

Users currently cannot create new gamebooks from the UI. They can only play existing stories. Adding a gamebook creation form enables users to create and publish their own interactive gamebooks, expanding the platform's content library.

## What Changes

- Add a new "Create Gamebook" page accessible from the navbar
- Create a form component for gamebook creation with fields for namespace, name, title, description, and author
- Add a route `/gamebook/new` that renders the creation form
- Integrate with the existing story API to save new gamebooks with client-side ID generation (`namespace/name`)

## Capabilities

### New Capabilities
- `gamebook-form`: A new frontend capability for creating gamebooks via a form UI

### Modified Capabilities
- (none - this is a net new feature)

## Impact

- **Frontend**: New page at `/gamebook/new`, using existing `ProjectForm` component
- **API**: Existing story creation API (verify endpoint exists)
- **Dependencies**: Mantine form components, React Router
