## Why

The example story is currently hard-coded in the source code, making it impossible for users to play different stories or create their own. This change enables story discovery and selection from multiple directories.

## What Changes

- Backend: Story discovery from two directories (examples bundled with app, user stories in `USER_DATA_DIR/stories/`)
- Backend: API endpoints for story listing and creating empty stories
- Frontend: Story list page with source badges and play action
- Remove hard-coded story path from engine manager

## Capabilities

### New Capabilities

- `story-discovery`: List stories from examples and user stories directories, deriving name from path
- `story-api`: API endpoints for story listing, deleting, creating empty stories (`GET /api/stories`, `POST /api/stories`, ...)
- `story-list-ui`: Frontend story list with source badges

### Modified Capabilities

- `user-data-directory`: Add `STORIES_DIR` and `EXAMPLES_DIR` constants

## Impact

**Backend**:
- New module: `story_project/` with `discovery.py`, `manager.py`
- New API router: `story_router`
- Extend `constants.py` for story directory paths

**Frontend**:
- New components: `StoryList.tsx`, `StoryCard.tsx`, `StorySourceBadge.tsx`
- New route: `/stories`

**No database changes** - stories are fully file-based.
**No metadata files** - name derived from directory path.
