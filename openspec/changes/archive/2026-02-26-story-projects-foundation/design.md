## Context

Currently, the example story ("broken-bulb") is hard-coded at `engine/manager.py:94`:
```python
project_path = Path(Path.home() / "llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
```

This prevents users from playing different stories or creating their own.

## Goals / Non-Goals

**Goals:**
- Enable story discovery from examples and user stories directories
- Provide API for listing stories and creating empty stories
- Build frontend UI for browsing stories
- Remove hard-coded story path from engine manager

**Non-Goals:**
- Import mechanisms (git/zip) - future phase
- Separate metadata files - name derived from path
- Library management - future phase
- Story editing UI

## Decisions

### D1: Directory Structure

```
USER_DATA_DIR/
├── stories/          # User's stories (editable)
└── llm-gamebook.db

examples/             # Bundled examples (read-only)
├── buzz/
│   └── broken-bulb/  # -> name: buzz/broken-bulb
```

**Rationale**: Two directories - bundled examples (read-only) and user stories (editable). Name derived from `{namespace}/{story}` path structure.

### D2: Story Identification

Story name is derived from directory path:
- `examples/buzz/broken-bulb/` → name: `buzz/broken-bulb`, source: `example`
- `USER_DATA_DIR/stories/user/my-story/` → name: `user/my-story`, source: `user`

**Rationale**: Single source of truth. No separate name field needed.

### D3: Story Source Enum

```python
class StorySource(str, enum.StrEnum):
    EXAMPLE = "example"  # Bundled, read-only
    USER = "user"        # User's stories, editable
```

### D4: No Separate Metadata File

All story info comes from `llm-gamebook.yaml`.

**Rationale**: Simplicity. Name derived from path. Version/dependencies not needed yet.

### D5: API Design

```
GET     /api/stories           # List all stories
GET     /api/stories/{id}      # Delete story
DELETE  /api/stories/{id}      # Get story details
POST    /api/stories           # Create empty story
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Examples directory path | Use `__file__` relative path |
| Concurrent file access | Filesystem is source of truth |
