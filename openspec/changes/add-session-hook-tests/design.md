## Context

The session hooks (`useCreateSession` and `useDeleteSession`) in `frontend/src/hooks/session.ts` manage critical user flows for story sessions. Currently, they have no test coverage. The hooks use RTK Query mutations (`sessionApi.useCreateSessionMutation` and `sessionApi.useDeleteSessionMutation`), integrate with navigation (`wouter`), and interact with modal hooks for confirmation and notifications.

## Goals / Non-Goals

**Goals:**
- Achieve full test coverage for `useCreateSession` and `useDeleteSession` hooks
- Test successful flows (creation, deletion with navigation)
- Test error handling (API failures, confirmation cancellation)
- Test edge cases (deleting active session, location-based navigation)
- Use existing testing stack (Vitest + React Testing Library)
- Mock RTK Query hooks and modal/notification hooks

**Non-Goals:**
- Test RTK Query API layer itself (covered in service tests if needed)
- Test notification/modal hook implementations
- Refactor hooks for testability (unless absolutely necessary)
- Add E2E tests (out of scope for unit test coverage)

## Decisions

**Testing Framework: Vitest + React Testing Library**
- Rationale: Already configured in frontend, consistent with existing `utils.test.ts`
- Alternative: Jest - Rejected (already migrated to Vitest)

**Mocking Strategy: MSW for API + Manual Hook Mocks**
- Rationale: RTK Query hooks are already generated with mock capabilities via `createApi`
- Manual mocks for custom hooks (`useShowError`, `useShowSuccess`, `useShowConfirmationModal`)
- Alternative: Full MSW server setup - Overkill for hook unit tests

**Test Structure: Group by Hook**
- Separate describe blocks for `useCreateSession` and `useDeleteSession`
- Test cases organized by scenario (success, error, edge cases)
- Shared setup in `beforeEach` where applicable

**Navigation Testing: Mock `useLocation`**
- Use `wouter`'s mock utilities to test navigation calls
- Verify correct routes are called with expected parameters

## Risks / Trade-offs

**Risk: Hook complexity makes testing difficult**
- Mitigation: Test public interface (returned functions), not internal implementation details

**Risk: RTK Query mocking can be verbose**
- Mitigation: Use `unwrap()` pattern consistently, mock at hook level not reducer level

**Risk: Async operations in tests**
- Mitigation: Use `vi.async` and proper `await` patterns, leverage Vitest's async test support

**Trade-off: Shallow vs Deep Testing**
- Decision: Shallow testing of hooks (mock dependencies) vs integration testing
- Rationale: Focus on hook logic, not dependency behavior

## Migration Plan

1. Create test file `frontend/src/hooks/session.test.ts`
2. Run tests with existing `pnpm test` command
3. Verify coverage reporting includes new tests
4. No deployment needed (tests only)
5. Add to CI pipeline automatically (already configured)

## Open Questions

- None - this is a straightforward test addition with clear scope
