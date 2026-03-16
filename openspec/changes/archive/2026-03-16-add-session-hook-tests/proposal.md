## Why

The frontend session hooks (`useCreateSession` and `useDeleteSession`) currently have zero test coverage. These hooks handle critical user flows: creating new story sessions and deleting existing ones. Without tests, refactoring or adding features to session management risks introducing regressions in the core storytelling experience.

## What Changes

- Add comprehensive unit tests for `useCreateSession` hook
- Add comprehensive unit tests for `useDeleteSession` hook
- Test successful session creation and navigation
- Test error handling for failed API calls
- Test confirmation modal flow for deletion
- Test navigation when deleting active session
- Mock RTK Query API calls and modal hooks

## Capabilities

### New Capabilities

- `session-hook-testing`: Comprehensive test coverage for session management hooks including creation, deletion, error handling, and navigation flows

### Modified Capabilities

- None

## Impact

- **Code**: New test file at `frontend/src/hooks/session.test.ts`
- **Dependencies**: May need additional testing utilities (MSW for API mocking, test utilities for modals)
- **Tests**: Adds to frontend test suite, runs with existing Vitest configuration
- **No production code changes**: This is purely test coverage addition
