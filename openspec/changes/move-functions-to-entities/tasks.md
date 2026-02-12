## 1. Schema Changes

- [ ] 1.1 Move `functions` field from `EntityTypeDefinition` to `EntityDefinition` in `backend/llm_gamebook/schema/entity.py`
- [ ] 1.2 Remove `functions` field from `EntityTypeDefinition` class
- [ ] 1.3 Add `functions` field to `EntityDefinition` class with type `list[FunctionDefinition] | None = None`

## 2. GraphTrait Updates

- [ ] 2.1 Update `GraphTrait.get_tools()` to access `self.functions` instead of `self.entity_type.functions`
- [ ] 2.2 Verify tool generation logic remains unchanged
- [ ] 2.3 Test with existing location graph configuration

## 3. YAML Configuration Updates

- [ ] 3.1 Update `examples/broken-bulb/llm-gamebook.yaml` - move `functions` from `LocationGraph` to the `locations` entity
- [ ] 3.2 Add transition functions to Main and The Meeting story arc entities (`progress_main_story`, `progress_the_meeting_story`)
- [ ] 3.3 Verify YAML structure follows the new pattern

## 4. Testing

- [ ] 4.1 Add third step to `backend/tests/broken_bulb/test_story_flow.py` - player takes leaflet, model does story arc transition
- [ ] 4.2 Run linting: `uv run ruff check`
- [ ] 4.3 Run type checking: `uv run mypy llm_gamebook`
- [ ] 4.4 Run tests: `uv run pytest`
- [ ] 4.5 Verify no regressions in existing tests
