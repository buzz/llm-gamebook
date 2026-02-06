# Story Projects Architecture

## Overview

This document describes the architecture for story and library management in the LLM Gamebook application.

## Core Concepts

### Stories and Libraries

Both stories and libraries use the same directory structure. They are distinguished by metadata:

- **Stories**: Complete gamebooks with entities, traits, graph nodes
- **Libraries**: Reusable components (entities, traits, templates, Python code)

### Naming System

Names use namespaces to prevent collisions: `@user/my-story` or `@foo/my-lib`

- **Namespace**: `@user`, `@foo`, etc. (1-39 alphanumeric/hyphen chars, starting with alphanumeric)
- **Project name**: `my-story`, `my-lib` (1-39 alphanumeric/hyphen chars, starting with alphanumeric)
- **Full name**: `@user/my-story` (namespace + `/` + name)

*Namespaces are mandatory.*

### Identity Mapping

Names are mapped to filesystem for storage:

- `@user/my-story` → (stored in `$USER_DATA_DIR/stories/@user/my-story/`)

## Directory Structure

```
~/.local/share/llm-gamebook/
├── stories/          # User's editable stories
├── imports/          # Imported stories (read-only mirrors)
├── libraries/        # Reusable libraries (read-only mirros)
├── user-libraries/   # User's editable libraries (less common, for library developers)
├── config.yaml       # Global configuration (sync settings, etc.)
└── llm-gamebook.db   # App state database

examples/             # Application-provided examples (read-only)
```

## Project Structure

Each story/library uses the same structure:

```
{project-id}/
├── llm-gamebook.yaml          # Main project definition
├── .{type}-meta.yaml          # Metadata (.story-meta.yaml or .library-meta.yaml)
├── python/                    # Optional: Python extensions
│   └── module_foo
│       ├── __init__.py
│       └── custom_trait.py
├── templates/                 # Optional: Jinja2 templates
│   ├── system_prompt.md.jinja2
│   └── intro_message.md.jinja2
├── imports/                   # Optional: Library dependencies
│   └── {library-id}/
└── assets/                    # Optional: Story assets
    └── ...
```

### Metadata Files

#### `.story-meta.yaml`

```yaml
type: story
name: '@user/foo'
version: x.y.z
source?:                        # Present for imported stories
  source_type: git|zip|directory
  source_url: https://github.com/user/repo.git
  imported_at: "2026-02-06T..."
  original_path: /path/to/original
forked_from?: id                # Present for forked stories
```

#### `.library-meta.yaml`

```yaml
type: library
name: '@user/bar'
version: x.y.z
is_reusable: true
dependencies?:
  "@foo/baz>=1.2.3"
  "@bar/quz>=6.0.0,<7.0.0"
```

## Lifecycle

```
1. Discovery
   ├─ examples/ (application)
   ├─ imports/ (external sources)
   └─ stories/ (user's personal)

2. Import (from external source)
   git clone / zip extract / copy directory
   ↓
   imports/{import-ns}/{import-id}/ with .import-meta.yaml

3. Fork/Clone (make editable)
   Copy files to stories/{ns}/{story-id}/
   ↓
   stories/{ns}/{story-id}/ with .story-meta.yaml

4. Edit (user modifies)
   llm-gamebook.yaml + assets

5. Play (create session)
   Database stores session state
```

### Additional Operations

- **Sync**: Update imported story from source (git pull / re-extract)
- **Delete**: Remove from `stories/` or `imports/`
- **Library import**: Copy library to `libraries/`

## Import Mechanisms

### Git

- Full repository clone (keeps history, allows updates)
- Supports URLs like `https://github.com/user/repo.git` or `git@github.com:user/repo.git`
- Stores full repo in `imports/{ns}/{import-id}/.git/`

### Zip

- Flat structure only (must contain `llm-gamebook.yaml` at root)
- Extracts to `imports/{ns}/{import-id}/`
- No metadata preserved beyond import info

### Directory

- Copy external directory to `imports/`
- Stores source path in `.import-meta.yaml`
- For read-only access or development

## API Endpoints

### Stories

```
GET    /api/stories
  └─ List all stories from all sources

GET    /api/stories/{id}
  └─ Get story details with metadata

POST   /api/stories/import
  └─ Import story from external source
  └─ Body: { source_type, source_url, name?, auth? }

POST   /api/stories/{id}/fork
  └─ Fork imported story into user stories

POST   /api/stories/{id}/sync
  └─ Sync imported story from source

DELETE /api/stories/{id}
  └─ Delete story from user data
```

### Libraries

Same endpoints as stories, but under `/api/libraries/`

### Sessions (Extended)

```
POST   /api/sessions
  └─ Body: { story_id, title?, model_id?, library_ids[] }
  └─ Create session with story + libraries
```

## Frontend Display

### Unified Story List

All stories from all sources displayed together:

- **Examples**: Application-provided, read-only
- **Imported**: From external source, read-only, syncable
- **My Stories**: User's editable stories

### Story Card

Each card shows:

- Name with namespace (e.g., `@user/my-story`)
- Source badge (examples/imported/local)
- Editable/read-only indicator
- Sync availability (for imports)
- Play button (for editable stories)
- Fork button (for read-only stories)

## Implementation Plan

### Phase 1: Foundation

- Backend: User data directory structure
- Backend: `story/importer/` (git/zip/dir support)
- Backend: `story/manager.py` (list, fork, delete)
- Backend: `story/metadata.py` (.story-meta.yaml, .import-meta.yaml)
- Frontend: `StoryList.tsx` (unified view)
- Frontend: `StoryCard.tsx` (individual card)
- API: `GET /api/stories`, `POST /api/stories/import`

### Phase 2: Import Mechanisms

- Backend: Git import (clone full repo, SSH auth)
- Backend: Zip import (extract flat)
- Backend: Directory import (copy/symlink)
- Frontend: `ImportModal.tsx` (source selection)
- API: `POST /api/stories/import` (full implementation)

### Phase 3: Forking & Syncing

- Backend: `story_fork.py` (copy to stories/)
- Backend: `story_sync.py` (git pull/re-extract)
- Backend: Metadata management
- Frontend: `ForkButton.tsx` (for imported stories)
- Frontend: `SyncButton.tsx` (for imports with source)
- API: `POST /api/stories/{id}/fork`, `POST /api/stories/{id}/sync`

### Phase 4: Libraries

- Backend: `library/manager.py` (similar to story_manager)
- Backend: `library/importer.py` (import libraries)
- Backend: `library/resolver.py` (resolve library dependencies)
- Frontend: `LibraryList.tsx`, `LibraryCard.tsx`
- API: Same endpoints as story_router

### Phase 5: Advanced Features

- Version tracking (git tags/commits)
- Template system
- Advanced library dependencies

## Future: Public Registries

The namespace system is designed to facilitate future public registries:

- `@user/...`, `@orga/....`

Registry integration would add:

- Remote listing: `GET /api/registry/stories`
- Remote search: `GET /api/registry/stories?q=keyword`
- Remote import: `POST /api/stories/import` with registry URL
- Version management: Track specific versions from registry
- Auto-fetch library dependencies
