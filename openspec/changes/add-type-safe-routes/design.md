## Context

The frontend currently uses scattered template literals for route paths (e.g., `` `/gamebook/${project.id}` ``). This lacks type-safety and makes refactoring error-prone. The project already uses `wouter` (React router) which depends on `regexparam` for pattern matching.

**Constraints:**
- Must use existing `regexparam` dependency (no new packages)
- Must maintain wouter's existing API
- Must be a gradual refactor (no breaking changes)

## Goals / Non-Goals

**Goals:**
- Single source of truth for all route definitions
- Type-safe URL building with compile-time parameter validation
- Auto-generated wouter routes from central definitions
- Replace all template literal paths in components

**Non-Goals:**
- Adding new routing capabilities
- Changing wouter's behavior
- Runtime route validation (compile-time only)

## Decisions

### Decision: Use `regexparam` over `path-to-regexp`

**Why:** `regexparam` is already installed as a wouter dependency. It provides both `parse()` (for matching) and `inject()` (for building URLs), which covers all our needs.

**Alternatives considered:**
- `path-to-regexp`: More features, but adds 56KB dependency
- Custom solution: Would require re-implementing what `regexparam` already does

### Decision: Flat route structure with string keys

**Why:** Simple, minimal boilerplate. Route names like `'gamebook.view'` are type-safe and provide autocomplete.

**Structure:**
```typescript
export const routes = {
  home: '/',
  gamebook: {
    new: '/gamebook/new',
    view: '/gamebook/:namespace/:name',
  },
  // ...
} as const
```

**Alternatives considered:**
- Hierarchical builders: `routes.gamebook.view({ ns, name })` - requires manual type annotations
- Object with path+component: Adds complexity without benefit

### Decision: Manual wouterRoutes array (not auto-generated)

**Why:** While this adds some boilerplate, it's explicit and clear. The paths reference the central `routes` object, so they're in sync.

**Implementation:**
```typescript
export const wouterRoutes = [
  { path: routes.home, component: ProjectList },
  { path: parse(routes.gamebook.view).pattern, component: ProjectDetails },
  // ...
]
```

**Alternatives considered:**
- `Object.entries(routes).map(...)`: Would lose component mapping
- Code generation: Overengineering for this use case

### Decision: Simple `buildUrl()` helper function

**Why:** Minimal API, easy to understand. Parameters are `Record<string, string>` - type-safe route names, but params are not strongly typed per route.

**Usage:**
```typescript
buildUrl('gamebook.view', { namespace: 'foo', name: 'bar' })
```

**Trade-off:** We accept that parameter names aren't strongly typed (could use `Record<string, string>`) in exchange for zero boilerplate. Full param type safety would require manual type annotations per route.

## Risks / Trade-offs

**[Trade-off]** Parameter names not strongly typed  
→ **Mitigation:** IDE autocomplete helps, and tests catch runtime errors

**[Risk]** Manual wouterRoutes array could get out of sync  
→ **Mitigation:** Clear documentation, code review catches omissions

**[Risk]** Breaking change if route names used elsewhere  
→ **Mitigation:** Search codebase for hardcoded paths before merging

## Migration Plan

1. **Phase 1:** Create new `routes.ts` with centralized definitions
2. **Phase 2:** Add `buildUrl()` helper and `wouterRoutes` array
3. **Phase 3:** Refactor components one by one:
   - ProjectCard
   - Navbar
   - ModelConfigLink
   - ProjectList
   - etc.
4. **Phase 4:** Update tests to use new route structure
5. **Phase 5:** Remove old template literal patterns

**Rollback:** Revert `routes.ts` and component changes in single commit.

## Open Questions

- Should we add runtime validation for empty parameters, or trust TypeScript?
- Do we need a linting rule to prevent template literal paths in components?

</content>