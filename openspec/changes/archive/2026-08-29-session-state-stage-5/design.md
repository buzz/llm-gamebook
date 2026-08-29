## Context

With Stages 1-4 complete, Stage 5 implements history and undo functionality. The system already stores state with each response (from Stage 1). Stage 5 adds:
- Full state snapshots after each step (not just deltas)
- Traversal: walking back through message history
- Restore: returning to a previous state
- Fork: branching from any historical point
- Core actions: end-game, reset-game

## Goals / Non-Goals

**Goals:**
- Store complete state with each agent response (full snapshots)
- Implement state traversal: find previous states by walking messages
- Handle gaps: when messages have no state, continue walking back
- Add restore functionality via action
- Fork support: branch creates independent session
- Implement core/end-game action
- Implement core/reset-game action
- Add history cleanup to prevent unbounded growth

**Non-Goals:**
- Complex version control (not git-like)
- Real-time collaboration
- Cross-session fork (only within same session)

## Decisions

### 1. State stored per response, not per change

**Decision:** Full state snapshots stored with each response message, not incremental changes.

**Rationale:**
- Simpler restore: just load and apply one snapshot
- No replay needed: restore is direct
- Trade-off: more storage, but manageable (only overridden fields)

**Alternatives considered:**
- Incremental changes: Would need replay to restore, more complex

### 2. Traversal: walk messages oldest to newest

**Decision:** State traversal iterates messages from oldest to newest, finding most recent state.

**Rationale:**
- Natural order: messages are already in order
- Gaps handled: skip messages without state, continue looking

### 3. Fork creates new session

**Decision:** Forking from a historical state creates a new session with that state's content.

**Rationale:**
- Clean separation: forked sessions are independent
- Original session unchanged: user can return to original path

### 4. Core actions implemented as regular actions

**Decision:** end-game, reset-game are regular actions in the action system.

**Rationale:**
- Consistent: all state changes go through action system
- Testable: same pattern as other actions
- Extensible: can add more core actions easily

### 5. History cleanup: configurable limit

**Decision:** Keep last N state snapshots, cleanup older ones.

**Rationale:**
- Prevents unbounded growth
- Configurable: can adjust based on storage/performance
- Trade-off: older history is lost (acceptable for game use case)

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large state blobs | Store only overrides (not full entity); consider compression |
| Fork complexity | Keep simple: copy state to new session, continue from there |
| Reset loses progress | Confirm with user before reset; could add "soft reset" |
| History gap handling | Continue walking until state found or no more messages |

## Migration Plan

1. **Full state snapshots**: Always store complete state (not just changes)
2. **State traversal utility**: Function to find previous states
3. **Core actions**: Add EndGameAction, ResetGameAction, RestoreAction, ForkAction
4. **Reduces for core actions**: Handle state changes for each
5. **Session fork**: Create new session with copied state
6. **History cleanup**: Background task or on-load cleanup

## Open Questions

- How many snapshots to keep?
  - Default: 50, configurable
- Should fork preserve message history?
  - Current: fork starts fresh with state, no history copy
- Reset confirmation?
  - Frontend responsibility; backend just executes action
