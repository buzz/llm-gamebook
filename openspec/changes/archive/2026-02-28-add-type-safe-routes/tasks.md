## 1. Core Route Infrastructure

- [x] 1.1 Create new `frontend/src/routes.ts` with centralized route definitions using `regexparam`
- [x] 1.2 Export `routes` array with hierarchical names (e.g., `gamebook.view`, `editor.edit`)
- [x] 1.3 Implement `buildUrl(routeName, params)` helper function
- [x] 1.4 Create `wouterRoutes` array derived from single source of truth
- [x] 1.5 Update main app router to use `wouterRoutes`

## 2. Component Refactoring

- [x] 2.1 Refactor `ProjectCard.tsx` - replace template literals with `buildUrl()`
- [x] 2.2 Refactor `Navbar.tsx` - replace hardcoded paths with `buildUrl()`
- [x] 2.3 Refactor `ModelConfigLink.tsx` - replace template literals with `buildUrl()`
- [x] 2.4 Refactor `ProjectList.tsx` - replace template literals with `buildUrl()`
- [x] 2.5 Find and refactor all other components using hardcoded paths (ProjectDetails, ProjectLink, NewStory)

## 3. Testing

- [ ] 3.1 Update existing tests that reference hardcoded paths
- [ ] 3.2 Add unit tests for `buildUrl()` function
- [ ] 3.3 Test type-safety by verifying TypeScript catches incorrect params

## 4. Cleanup

- [ ] 4.1 Remove old `PROJECT_ID_PATTERN` and `MODEL_CONFIG_ID` constants if no longer needed
- [ ] 4.2 Update documentation to reflect new routing approach
- [ ] 4.3 Add linting rule to prevent template literal paths in components (optional)

## 5. Verification

- [x] 5.1 Run type check: `pnpm typecheck`
- [x] 5.2 Run linter: `pnpm lint`
- [ ] 5.3 Run tests: `pnpm test`
- [ ] 5.4 Manual testing: Verify all navigation works correctly
