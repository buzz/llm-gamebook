## 1. Core View Layer Infrastructure

- [x] 1.1 Create `story/template_view.py` with `EntityView` class (proxy for session-aware attribute access)
- [x] 1.2 Add `EntityView.__getattr__` with resolution order: session_field resolver → session state → entity default
- [x] 1.3 Add `EntityView._wrap_if_needed` to wrap nested BaseEntity and list[BaseEntity] results
- [x] 1.4 Create `TemplateContext` class as root view object with project-level field proxies
- [x] 1.5 Create `EntityTypeView` class wrapping EntityType with session-aware entity list

## 2. Trait Registry Decorators

- [x] 2.1 Add `session_field(field_name)` decorator function in `trait_registry.py`
- [x] 2.2 Add `reducer(action_name)` decorator function in `trait_registry.py`
- [x] 2.3 Update `TraitRegistryEntry` to include `session_fields: dict[str, str]` mapping
- [x] 2.4 Update `register()` to collect `@session_field` and `@reducer` decorated methods
- [x] 2.5 Export decorator functions in `__all__`

## 3. Trait Refactoring

- [x] 3.1 Update `GraphTrait` to import `StoryContext` only under `TYPE_CHECKING`
- [x] 3.2 Add `@session_field("current_node")` resolver method `_resolve_current_node` on GraphTrait
- [x] 3.3 Add `@session_field("current_node_id")` resolver method `_resolve_current_node_id` on GraphTrait
- [x] 3.4 Remove `get_template_context()` method from GraphTrait
- [x] 3.5 Remove `get_template_context()` method from GraphNodeTrait
- [x] 3.6 Update `DescribedTrait` to add `@session_field("enabled")` resolver for enabled field
- [x] 3.7 Remove `get_template_context()` method from DescribedTrait (if exists)

## 4. StoryContext Integration

- [x] 4.1 Update `StoryContext.get_system_prompt()` to create `TemplateContext(self)` for rendering
- [x] 4.2 Update `StoryContext.get_intro_message()` to create `TemplateContext(self)` for rendering
- [x] 4.3 Remove `StoryContext.get_template_context()` method
- [x] 4.4 Remove circular imports from `context.py` (no imports from traits at runtime)

## 5. Testing

- [x] 5.1 Add unit tests for `EntityView` attribute resolution order
- [x] 5.2 Add unit tests for `EntityView` wrapping of nested entities
- [x] 5.3 Add unit tests for `TemplateContext` project-level field access
- [x] 5.4 Add unit tests for `@session_field` decorator registration
- [x] 5.5 Add integration test verifying templates render correctly with view layer
- [x] 5.6 Verify no circular imports with Python import check

## 6. Cleanup

- [x] 6.1 Remove any unused imports from traits
- [x] 6.2 Run lint and typecheck on all modified files
- [x] 6.3 Update `story/__init__.py` exports if needed
