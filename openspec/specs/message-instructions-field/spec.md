# Message Instructions Field

## Purpose

Persist the `instructions` field from Pydantic AI's `ModelRequest` to the database `Message` object and expose it via the API for future frontend use.

## Requirements

### Requirement: Message model stores instructions

The `Message` database model SHALL include an `instructions` column of type `String` (or `Text`) that is nullable with a default of `null`.

#### Scenario: New message persists instructions
- **WHEN** Pydantic AI creates a `ModelRequest` containing `instructions`
- **AND** the engine creates a `Message` for the request
- **THEN** the engine SHALL extract `instructions` from the request
- **AND** `Message.instructions` SHALL be set from the extracted value
- **AND** the value SHALL be persisted to the database

#### Scenario: Missing instructions stored as null
- **WHEN** the `ModelRequest` has `null` or `undefined` `instructions`
- **THEN** `Message.instructions` SHALL be stored as `null`

#### Scenario: Existing messages default to null
- **GIVEN** messages created before the field existed
- **WHEN** they are read
- **THEN** their `instructions` value SHALL be `null`

### Requirement: API responses include instructions

Message response DTOs SHALL include an `instructions` field of type `string` or `null`, optional, serialized in API responses.

#### Scenario: Message response serialized
- **WHEN** a message is returned from the API
- **THEN** the response SHALL include the `instructions` field with the stored value or `null`

### Requirement: Frontend types include instructions

The frontend OpenAPI types SHALL include `instructions` on message types.

#### Scenario: API types regenerated
- **WHEN** `pnpm generate-api-types` is run after the backend change
- **THEN** the generated message types SHALL include `instructions` as an optional string field
