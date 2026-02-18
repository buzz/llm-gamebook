## Context

The session-state integration (stage 3) revealed architectural flaws: entities directly accessed `StoryContext`, creating circular imports and mixing data concerns with rendering. Templates received raw entities but needed session-aware values. This design introduces a proper view layer that cleanly separates:
- **Entity layer**: Pure data holders with project defaults
- **View layer**: Session-aware proxies for template rendering
- **Resolution layer**: Decorator-marked methods that bridge the two

Current state has `GraphTrait` and `DescribedTrait` with methods like `get_effective_current_node(ctx)` that import `StoryContext` at runtime.

## Goals / Non-Goals

**Goals:**
- Clean separation: entities don't know about templates or views
- No circular imports: one-way dependency direction
- Extensible: new dynamic fields just add `@session_field` decorator
- Templates stay dumb: plain attribute access works identically

**Non-Goals:**
- Changing the template files themselves (attribute access syntax unchanged)
- Modifying how Jinja2 environment is configured
- Changing the action system or Store implementation

## Decisions

### D1: Proxy-based view objects (EntityView, TemplateContext)

**Decision**: Use Python proxy objects that intercept `__getattr__` rather than pre-computing resolved values.

**Rationale**: 
- Lazy evaluation: only resolve fields that templates actually access
- Simpler than building complete resolved context upfront
- Works naturally with nested entity access (e.g., `entity.current_node.name`)

**Alternatives considered**:
- Pre-computed context dict: loses entity identity, harder to extend
- Entity subclasses with session awareness: violates entity purity, circular imports

### D2: Decorator-based session field registration

**Decision**: Use `@session_field("field_name")` decorator on trait methods, tracked in trait_registry.

**Rationale**:
- Explicit: dynamic fields are visible in code
- Decoupled: registry knows about methods, methods don't know about registry
- Extensible: any trait can add session fields without base class changes

**Alternatives considered**:
- Convention-based (`_resolve_<field>`): implicit, harder to discover
- Configuration dict in trait class: more boilerplate, less colocation

### D3: Resolution order: session_field → session state → entity default

**Decision**: When accessing `entity.field` through EntityView:
1. Check for `@session_field` resolver on any trait
2. Check session state for direct field override
3. Fall back to entity attribute (project default)

**Rationale**:
- Resolvers can compute derived values (e.g., `current_node` from `current_node_id`)
- Direct overrides for simple fields don't need resolvers
- Entity defaults are the final fallback

### D4: TYPE_CHECKING imports for StoryContext in traits

**Decision**: Traits import `StoryContext` only under `TYPE_CHECKING` block, use string annotation in method signatures.

**Rationale**:
- Avoids circular imports at runtime
- Type checkers still validate signatures
- Methods receive `ctx` at runtime, don't import the class

## Risks / Trade-offs

**Risk: Performance overhead from proxy indirection**
→ Mitigation: Proxy is lightweight; resolution is cached by template context lifecycle. Profile if needed.

**Risk: Debugging complexity - templates see proxies not entities**
→ Mitigation: `EntityView.__repr__` shows wrapped entity info. Add logging in `__getattr__` for debugging.

**Risk: Forgetting to add `@session_field` for dynamic fields**
→ Mitigation: Document clearly; missing resolver just falls back to default (graceful degradation).

## Open Questions

- None - design is based on documented architecture in `docs/session-state/view-layer.md`
