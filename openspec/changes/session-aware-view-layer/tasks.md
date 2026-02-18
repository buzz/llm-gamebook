## 1. Core View Layer Infrastructure

- [ ] 1.1 Create `story/template_view.py` with `EntityView` class (proxy for session-aware attribute access)
- [ ] 1.2 Add `EntityView.__getattr__` with resolution order: session_field resolver → session state → entity default
- [ ] 1.3 Add `EntityView._wrap_if_needed` to wrap nested BaseEntity and list[BaseEntity] results
- [ ] 1.4 Create `TemplateContext` class as root view object with project-level field proxies
- [ ] 1.5 Create `EntityTypeView` class wrapping EntityType with session-aware entity list

## 2. Trait Registry Decorators

- [ ] 2.1 Add `session_field(field_name)` decorator function in `trait_registry.py`
- [ ] 2.2 Add `reducer(action_name)` decorator function in `trait_registry.py`
- [ ] 2.3 Update `TraitRegistryEntry` to include `session_fields: dict[str, str]` mapping
- [ ] 2.4 Update `register()` to collect `@session_field` and `@reducer` decorated methods
- [ ] 2.5 Export decorator functions in `__all__`

## 3. Trait Refactoring

- [ ] 3.1 Update `GraphTrait` to import `StoryContext` only under `TYPE_CHECKING`
- [ ] 3.2 Add `@session_field("current_node")` resolver method `_resolve_current_node` on GraphTrait
- [ ] 3.3 Add `@session_field("current_node_id")` resolver method `_resolve_current_node_id` on GraphTrait
- [ ] 3.4 Remove `get_template_context()` method from GraphTrait
- [ ] 3.5 Remove `get_template_context()` method from GraphNodeTrait
- [ ] 3.6 Update `DescribedTrait` to add `@session_field("enabled")` resolver for enabled field
- [ ] 3.7 Remove `get_template_context()` method from DescribedTrait (if exists)

## 4. StoryContext Integration

- [ ] 4.1 Update `StoryContext.get_system_prompt()` to create `TemplateContext(self)` for rendering
- [ ] 4.2 Update `StoryContext.get_intro_message()` to create `TemplateContext(self)` for rendering
- [ ] 4.3 Remove `StoryContext.get_template_context()` method
- [ ] 4.4 Remove circular imports from `context.py` (no imports from traits at runtime)

## 5. Testing

- [ ] 5.1 Add unit tests for `EntityView` attribute resolution order
- [ ] 5.2 Add unit tests for `EntityView` wrapping of nested entities
- [ ] 5.3 Add unit tests for `TemplateContext` project-level field access
- [ ] 5.4 Add unit tests for `@session_field` decorator registration
- [ ] 5.5 Add integration test verifying templates render correctly with view layer
- [ ] 5.6 Verify no circular imports with Python import check

## 6. Cleanup

- [ ] 6.1 Remove any unused imports from traits
- [ ] 6.2 Run lint and typecheck on all modified files
- [ ] 6.3 Update `story/__init__.py` exports if needed
