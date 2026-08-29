## Why

With Stages 1-4 fully implemented (session state, action system, action-driven changes, triggers), the game needs to enable going back to previous states. Stage 5 implements history and undo, supporting save games, session branching, and core game actions (end-game, reset).

## What Changes

- Store complete serialized state with each agent response (full snapshots)
- Implement state traversal: walk back through message history to find previous states
- Handle gaps: responses without state changes (walk further back)
- Add restore functionality: action to restore to specific point
- Fork support: branch from any historical state (creates independent branch)
- Implement `core/end-game` action: mark session as ended
- Implement `core/reset-game` action: clear state and restart from defaults
- Add state history cleanup to prevent unbounded growth

## Capabilities

### New Capabilities

- `state-history`: State snapshots, traversal, restore, fork, and core game actions

### Modified Capabilities

- `action-system`: New actions: `core/end-game`, `core/reset-game`, `core/restore`, `core/fork`

## Impact

- **Session loading**: Restores from latest state or historical point
- **Message model**: Already has state field from Stage 1
- **Actions**: New core actions for game lifecycle
- **History**: State history management and cleanup
