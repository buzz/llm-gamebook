---
description: Stage and commit a change to git
---

Stage and commit all files related to a change.

**Input**: Optionally specify a change name after `/opsx-commit-change` (e.g., `/opsx-commit-change add-auth`). If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec list --json` to get available changes sorted by most recently modified. Then use the **question tool** to let the user select which change to work on.

   Archived changes will not show. Check `git status` if you can't find the change.

   Present the top 3-4 most recently modified changes as options, showing:
   - Change name
   - Schema (from `schema` field if present, otherwise "spec-driven")
   - Status (e.g., "0/5 tasks", "complete", "no tasks")
   - How recently it was modified (from `lastModified` field)

   Mark the most recently modified change as "(Recommended)" since it's likely what the user wants to continue.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check current status**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand current state. The response includes:
   - `schemaName`: The workflow schema being used (e.g., "spec-driven")
   - `artifacts`: Array of artifacts with their status ("done", "ready", "blocked")
   - `isComplete`: Boolean indicating if all artifacts are complete

3. **Act based on artifact status**:

   **If artifacts are **not** complete (`isComplete: false`)**:
   - Explain that the change is not ready yet. Give a summary on the missing artifacts and suggest using `/opsx-continue`.
   - STOP execution.

4. **Check task completion status**

   Read the tasks file (typically `tasks.md`) to check for incomplete tasks.

   Count tasks marked with `- [ ]` (incomplete) vs `- [x]` (complete).

   **All tasks in `tasks.md` are INCOMPLETE:**
   - **Change is ready:** Commit as new change.
   - Proceed with **Step 5**.

   **All tasks in `tasks.md` are COMPLETE:**
   - This is a change that has been completed.
   - Check if it has been archived.
     - Change exists in `openspec/changes/<name>`: Suggest to use `/opsx-archive` and STOP execution.
     - Change exists in `openspec/changes/archive/YYYY-MM-DD-<name>`: Ready to commit as archived change proposal. Proceed with **Step 5**.

   **Mixed complete/incomplete tasks found:**
   - Artifacts are complete, but we're in the middle of implementing the change.
   - Suggest to use `/opsx-apply` or `/opsx-implement` and STOP execution.

5. **Stage and commit change files**

   Stage and commit if either
   - *no* tasks in `tasks.md` are complete: new change commit
   - *all* tasks in `tasks.md` are complete: archive change commit

   If *some* tasks are in `tasks.md` are complete: STOP execution.
   If change artifacts are incomplete: STOP execution.

   Run `git status` to find current changes. Decide if you need to stage the changes first (they might be staged already).

   **If this is a new change (only incompleted tasks AND change is in `openspec/changes/<name>`):**
   - `git add openspec/changes/<name>` to stage files.
   - `git commit -m 'chore(openspec): add <name> change'`

   **If this is an archived change (only completed tasks AND change is in `openspec/changes/archive/YYYY-MM-DD-<name>`):**
   - Stage change files.
     - `ls openspec/changes/archive/` to determine archived change directory name.
     - `git add openspec/changes/archive/YYYY-MM-DD-<name>` to stage archive change.
     - `git add openspec/changes/<name>` to stage removal of change directory.
   - Add specs (if applicable).
     - `ls openspec/changes/archive/YYYY-MM-DD-<name>/specs` to find all related spec names.
     - `git add openspec/specs/<spec-name>` for each spec name found.
   - `git commit -m 'chore(openspec): archive <name> change'`

**Output On Success (new change)**

```
## Commit Change Complete

**Change:** <change-name>
**Type:** new
**Commit message:** chore(openspec): add <name> change

Successfully commited new change.
```

**Output On Success (archived change)**

```
## Commit Change Complete

**Change:** <change-name>
**Type:** archive
**Commit message:** chore(openspec): archive <name> change

Successfully commited archived change.
```

**Output On Error**

```
## Commit Change Failed

**Change:** <change-name>

[Give reason for failure. Suggest commands to use.]
```
