## Why

The initial session-state integration had entities directly accessing `StoryContext` through methods like `get_effective_current_node(story_context)`, creating circular imports, violating separation of concerns, and intertwining template rendering with entity logic. A proper view layer architecture is needed to separate entity data (project defaults) from session-aware template rendering.

## What Changes

- Introduce `EntityView` proxy class that wraps entities for session-aware template access
- Introduce `TemplateContext` as the root view object passed to Jinja2 templates
- Add `@session_field` decorator to mark methods that resolve session-aware values
- Add `@reducer` decorator to mark methods that handle action state transitions
- Update `trait_registry` to track session field resolvers and reducers per trait
- Remove `get_template_context()` methods from entities (rendering moves to view layer)
- **BREAKING**: Templates now access entities through view wrappers, not raw entity objects
- Clean import structure: no circular imports between `context.py`, `template_view.py`, `trait_registry.py`

## Capabilities

### New Capabilities

- `template-view-system`: Session-aware view layer for Jinja2 template rendering with EntityView, TemplateContext, and session field decorators

### Modified Capabilities

- `session-state`: Entity field access now flows through view layer; templates receive EntityView proxies instead of raw entities

## Impact

- **New files**: `story/template_view.py` (EntityView, TemplateContext, EntityTypeView)
- **Modified files**: `story/context.py` (creates TemplateContext), `story/trait_registry.py` (decorators, registry entries)
- **Traits**: Add `@session_field` resolvers, remove `get_template_context()` methods
- **Templates**: No changes needed - attribute access works identically on EntityView
- **Import structure**: Clean one-way dependencies, TYPE_CHECKING imports for StoryContext in traits
