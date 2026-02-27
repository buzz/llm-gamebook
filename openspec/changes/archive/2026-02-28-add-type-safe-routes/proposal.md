## Why

The frontend currently constructs route paths using template literals scattered throughout components (e.g., `` `/gamebook/${project.id}` ``). This approach lacks type-safety: typos in path strings go undetected, there's no autocomplete for route names, and refactoring is fragile. We need a centralized, type-safe routing system.

## What Changes

- **Single source of truth**: ONE array defining routes with `{ name, path, component }`
- **Hierarchical route names**: `'gamebook.view'`, `'modelConfig.edit'` (dot-separated)
- **Type-safe URL building** via `buildUrl(routeName, params)` using route name lookup
- **Auto-generated wouter routes** derived from the same array using `parse()` for regex conversion
- **Replace all template literal paths** in components with calls to `buildUrl()`
- **No breaking changes** - wouter's API remains unchanged

## Capabilities

### New Capabilities
- `type-safe-routes`: Centralized route definitions with type-safe URL construction for all frontend routes

### Modified Capabilities
- (none - this is infrastructure, no existing requirements change)

## Impact

**Files changed:**
- `frontend/src/routes.ts` - Complete refactor of route definitions
- `frontend/src/components/**/*` - All components using `Link` components (ProjectCard, Navbar, ModelConfigLink, ProjectList, etc.)

**Dependencies:**
- No new dependencies - uses `regexparam` already installed via wouter

**Testing:**
- Update tests that reference hardcoded paths
- Add tests for `buildUrl()` function
