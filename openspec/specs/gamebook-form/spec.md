## ADDED Requirements

### Requirement: Create Gamebook page

The frontend SHALL provide a page at `/gamebook/new` for creating new gamebooks.

#### Scenario: Navigate to create page

- **WHEN** a user navigates to `/gamebook/new`
- **THEN** the system SHALL display a form for creating a new gamebook

#### Scenario: Page title

- **WHEN** the create page is displayed
- **THEN** the page title SHALL be "Create Gamebook"

### Requirement: Gamebook creation form

The system SHALL provide a form with fields for creating a new gamebook.

#### Scenario: Form fields displayed

- **WHEN** the form is displayed
- **THEN** the following fields SHALL be present:
  - Namespace (required, text input, kebab-case format)
  - Name (required, text input, kebab-case format)
  - Title (required, text input)
  - Description (optional, textarea)
  - Author (optional, text input)

#### Scenario: Namespace field validation

- **WHEN** the user leaves the namespace field empty
- **AND** attempts to submit the form
- **THEN** the system SHALL display a validation error "Namespace is required"

#### Scenario: Name field validation

- **WHEN** the user leaves the name field empty
- **AND** attempts to submit the form
- **THEN** the system SHALL display a validation error "Name is required"

#### Scenario: Title field validation

- **WHEN** the user leaves the title field empty
- **AND** attempts to submit the form
- **THEN** the system SHALL display a validation error "Title is required"

#### Scenario: Kebab-case validation

- **WHEN** the user enters a namespace or name with invalid characters (uppercase, spaces, special chars)
- **AND** attempts to submit the form
- **THEN** the system SHALL display a validation error about kebab-case format

#### Scenario: Successful form submission

- **WHEN** the user fills in namespace, name, and title
- **AND** clicks the "Create" button
- **THEN** the system SHALL submit the form data to the API with ID `namespace/name`
- **AND** navigate to the gamebook detail page on success
- **AND** show success notification

#### Scenario: API error handling

- **WHEN** the API returns an error during submission
- **THEN** the system SHALL display an error message

#### Scenario: Loading state during submission

- **WHEN** the form is being submitted
- **THEN** the submit button SHALL be disabled
- **AND** a loading indicator SHALL be displayed

### Requirement: Navigation to create page

#### Scenario: Create link in navbar

- **WHEN** the navbar is displayed
- **THEN** a "New Gamebook" link SHALL be visible linking to `/gamebook/new`

## API

### Components

- `CreateGamebook.tsx` - Page component
- `CreateGamebookForm.tsx` - Form component

### Routes

```
/gamebook/new -> ProjectForm
```
