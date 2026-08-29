# Proposal: dynamic-field-evaluation

## Why

The session-state architecture design (`docs/session-state/architecture.md`) names **Dynamic Fields** a core concept — any entity field can be static or an `=expression` evaluated at runtime — but only *trigger conditions* support the `=` prefix today (Stage 4). Derived values (e.g. `total_kills: =player.kills + player.bonus_kills`, `location_name: =world.nodes[player.current_node_id].name`) currently require redundant stored fields plus reducer logic to keep in sync. Making fields dynamically evaluable removes that boilerplate and completes the last unimplemented core concept of the session-state design.

## What Changes

- **YAML schema**: any entity field value may be a string prefixed with `=` (a value expression), in addition to static values. Expressions reference entity fields via dot paths and literals.
- **Expression grammar**: extend the pyparsing condition grammar (`story/conditions/`) with value-producing expressions (dot paths, literals, arithmetic/comparison operators) so an expression evaluates to a field value, not just a bool. Reuse existing literal/dot-path primitives; the boolean grammar becomes a specialization.
- **Load-time validation**: `=expression` field values are parsed and validated when the project loads (parse errors and unknown entity/field references fail project loading, consistent with trigger conditions).
- **Effective field resolution**: `StoryContext.get_field` gains a middle tier — **session override > dynamic evaluation > static default**. Dynamic fields are evaluated against the *current effective state* (overrides + other effective fields), never against raw defaults.
- **No storage for derived values**: dynamic fields are never written to `SessionState` overrides and never appear in message state snapshots; restore/fork re-evaluate them against the restored state. Setting a dynamic field (tool/reducer) is rejected with a clear error.
- **Runtime evaluation errors**: a dynamic field whose expression fails at runtime (e.g. missing reference, type error) is a defined, logged error — not a silent default (exact semantics in design.md).
- **Documentation**: mark Dynamic Fields as implemented in `docs/session-state/architecture.md` / `steps-overview.md`; extend the broken-bulb example (or docs) with a dynamic field demonstration.

No breaking changes: projects without `=expression` fields behave exactly as before.

## Capabilities

### New Capabilities

- `dynamic-fields`: `=expression` entity field values — value-expression syntax, load-time validation, runtime evaluation semantics (evaluation order, error handling, circular references), and the rule that dynamic fields are derived (never persisted as overrides or snapshots).

### Modified Capabilities

- `session-state`: the "StoryContext integrates session and project state" requirement is modified — effective field resolution becomes three-tier (session override > dynamic evaluation > static default) and setting a dynamic field is an error.

Not modified: `trigger-system` — conditions already evaluate against *effective* field values, so they transparently pick up dynamic fields without requirement changes (covered by a test scenario).

## Impact

- `story/conditions/grammar.py`, `story/conditions/evaluator.py` (or a new `story/expressions/` module): value-expression grammar + evaluator
- `story/schemas/entity.py`, project loading: accept and validate `=expression` field values
- `story/context.py` (`get_field`): dynamic evaluation tier; reject writes to dynamic fields
- `story/state/` (`SessionState`, store): guard against persisting dynamic fields; interaction with state snapshots (restore/fork re-evaluation)
- Tools/prompts/templates read fields via `get_field`/EntityView proxies → pick up dynamic values with no changes
- Tests: grammar/evaluator unit tests, resolution-order tests, dynamic-field-in-trigger-condition integration, snapshot/restore behavior, error cases
- Docs: `docs/session-state/architecture.md`, `docs/session-state/steps-overview.md`, example story
