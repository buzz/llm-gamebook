# Design: dynamic-field-evaluation

## Context

The session-state design doc names **Dynamic Fields** a core concept, but only *trigger conditions* support the `=` expression prefix today. Current state:

- **Resolution**: `StoryContext.get_field(entity_id, field_name)` returns *session override → project default* (raw `getattr` on the entity). Defaults are static values.
- **Entity fields**: fields come from two places — pydantic fields declared by trait base classes (e.g. `current_node_id: str`) and arbitrary YAML attributes captured via `EntityDefinition.model_config = ConfigDict(extra="allow")`. Both are read with `getattr`.
- **Expression language**: `story/conditions/grammar.py` (pyparsing) defines literals, `DotPath` (`entity.field[...]`), `Comparison` (`== != < <= > >= in`), and boolean combinators (`not`/`and`/`or`). The grammar root is boolean; there is **no arithmetic**. `BoolExprEvaluator` evaluates ASTs, resolving dot paths *through `StoryContext.get_field`* when a context is bound — so expressions already see effective values.
- **Stored expressions**: `BoolExprDefinition` (in `story/schemas/expression.py`) is a pydantic model wrapping a parsed `g.BoolExpr`, with a `model_validator(mode="before")` that parses `=…` strings (or lists) at load. Trigger conditions use it and are parse-validated at project load (`story/schemas/project.py`).
- **Evaluation hot paths**: system prompt / intro templates render per step; trigger middleware evaluates conditions after every dispatched action; tools and `EntityView` template proxies read fields via `get_field`.

Constraints: no frontend impact (fields remain plain values); the existing trigger pipeline must keep working unchanged; project loading remains the place where authoring errors fail loudly.

## Goals / Non-Goals

**Goals:**
- Any entity field value may be `=expression`, evaluated at runtime against the current effective state.
- One shared expression grammar for conditions *and* fields (conditions become a boolean specialization).
- Expressions support dot paths, literals, comparisons, boolean combinators, and basic numeric arithmetic.
- Authoring errors (unparseable expression, circular dependency) fail at project load with actionable messages.
- Dynamic fields are derived: never persisted as session-state overrides or snapshots; restore/fork re-evaluate them.
- Zero behavior change for projects without `=` fields.

**Non-Goals:**
- String operations (concatenation, slicing) and index access (`entity.list[0]`).
- Function calls in field expressions (e.g. `=player.has_visited('village')`) — the function/tool system stays separate.
- Extending `=` to other YAML constructs (trait options, trigger args, prompt text).
- Memoization/caching of evaluations beyond reusing the parsed AST.
- UI changes (dynamic fields render as plain values in existing views).

## Decisions

### D1 — One unified expression grammar; `BoolExpr` becomes a specialization

Rebuild the grammar as a single `expr` (value) expression with pyparsing `infix_notation` levels, highest to lowest precedence:

1. primary: `dot_path | literal | ( expr )`
2. `* /` (left) — new `ArithExpr` node
3. `+ -` (left) — new `ArithExpr` node
4. comparisons `== != < <= > >= in` (non-associative) — existing `Comparison` node
5. `not` (right)
6. `and` (left), then `or` (left)

`bool_expr` is aliased to `expr`; `BoolExpr = Expr`. `parse_bool_expr` keeps its signature and behavior (optional leading `=` stripped, full-match parse) so trigger parsing is byte-for-byte compatible. A new `ValueExprDefinition` in `story/schemas/expression.py` wraps the parsed AST for field values (single expression; no list form — fields hold one value).

**Why**: conditions and fields are the same language at different root types; two grammars would drift. The existing `comparison` non-terminal is promoted to an infix level, which also makes mixed expressions like `=a.b + c.d > 5` parse naturally.
**Alternative considered**: keep the boolean grammar untouched and add a parallel value grammar — rejected: duplicate parse-action machinery, and trigger conditions lose the ability to use arithmetic (a feature authors will expect once fields have it).

### D2 — Arithmetic: numeric-only, strict typing

`ArithExpr` with operators `+ - * /` (no unary minus in v1). Type rules, checked at evaluation:

- `int op int` → `int` for `+ - *`; `/` → `float` (true division)
- any `float` operand → `float`
- `bool` or `str` operand, or entity/collection operand → `ExpressionEvalError` (arithmetic is numeric-only; comparisons remain the tool for mixed types)

**Why**: the flagship use cases are derived counters/health/flags (`=player.hp - player.injury_penalty`). String concat is deliberately excluded — ambiguous semantics (and `str * int`!) would complicate the type rules for little story value.
**Alternative considered**: no arithmetic in v1 (pure dot-path/literal/comparison reuse) — rejected: derived numerics are the most common "redundant stored field" this change exists to eliminate, and the infix levels are mechanical to add.

### D3 — Dynamic fields are converted to `ValueExprDefinition` at entity construction

New step in entity construction (`BaseEntity.post_init` hook, which already runs per entity): scan declared model fields **and** extra attributes; any value that is a `str` starting with `=` is parsed (full-match, D1) and replaced with a `ValueExprDefinition` instance holding the AST and the source string. Parse failure → `ValueError` naming the entity, field, and parse error — project load fails.

**Why**: converting at construction (post-validation) works uniformly for trait-declared `str` fields and `extra="allow"` attributes, with no pydantic schema machinery. The parsed AST is built once at load; evaluation is pure tree walking (pyparsing packrat already caches parse internals).
**Alternative considered**: a custom pydantic field type for dynamic fields — rejected: extra attributes have no declared field type to attach it to, so a schema-level approach would only cover half the fields.
**Consequence**: `getattr` on a dynamic field returns a `ValueExprDefinition`, not a string. All read paths must go through `get_field` (they do — `EntityView` template proxies, tools, and the evaluator all resolve via `get_field`); a task verifies this holds for every read path, and raw `model_dump()` of an entity with dynamic fields is considered internal/debug-only (the definition object serializes with its source string).

### D4 — Three-tier resolution in `StoryContext.get_field`

```
session override (plain value)  →  return as-is
default is ValueExprDefinition  →  evaluate against current effective state, return value
default is plain value          →  return as-is (unchanged)
```

`StoryContext.__init__` constructs the (generalized) evaluator once, bound to `project` and the context itself; `get_field` delegates evaluation to it. Because the evaluator resolves dot paths *through `get_field`*, nested dynamic references naturally see other dynamic fields' current values — no special wiring.

**Why per-access (lazy) evaluation**: effective state changes mid-step (a reducer may read a field after an earlier action mutated its inputs); a per-step pre-resolution pass would need a dependency ordering and could still be stale. Story-scale entity graphs make repeated tree-walks cheap.
**Alternative considered**: resolve all dynamic fields once per dispatch chain and cache — rejected as complexity without a demonstrated need; revisit only with profiling evidence.

### D5 — Evaluator: one class, two entry points

`BoolExprEvaluator` keeps its name and `eval(expr) -> bool` contract (the `trigger-system` spec references it) and gains `eval_value(expr) -> EntityProperty`:

- `eval_value` handles `ArithExpr` (D2 type rules) and otherwise resolves the same nodes `eval` does; a `Comparison` evaluates to its bool value, so comparisons are legal field values.
- Bool context keeps its existing special case: a field whose value is a stored `BoolExprDefinition` evaluates as a boolean expression. Value context returns such objects as-is (today's behavior).
- Both entry points share `_resolve_dot_path` / `_resolve_entity_property` (effective-value resolution unchanged).
- New error: `DynamicFieldEvalError` (subclass of `ExpressionEvalError`) carrying the field name and expression source, so failures identify *which field* broke.

### D6 — Read-only dynamic fields; overrides still win

- **Writes rejected**: `SessionState.set_field` (and anything routing through it — reducers, tools) targeting a field that is dynamic in the project raises a clear error (`DynamicFieldReadOnlyError` or a `ValueError` with an actionable message). If an author needs a mutable derived value, the pattern is: static field + trigger that updates it.
- **Existing overrides win**: if a saved session state contains an override for a field that the author later made dynamic, the override shadows the expression (state was explicitly set; no data loss, no migration). The read-only rule applies to *new* writes.

**Why**: allowing new writes would create a second source of truth that silently defeats the expression; the shadowing rule keeps restore/fork semantics simple (snapshot restores override the expression exactly as it overrides static defaults).
**Alternative considered**: allow overrides as a "freeze" escape hatch — rejected: two ways to say "this value is X" invite confusion about which wins when both exist.

### D7 — Cycle detection: static at load, depth cap at runtime

Dependencies of a dynamic field are syntactically fixed (the `DotPath` nodes in its AST), so cycles are detectable at project load:

- Build a graph whose nodes are dynamic fields; edge A→B if A's expression contains a dot path whose head `(entity_id, field)` is dynamic field B. (Deeper chains can't create new cycles — only the head field can be dynamic-and-recursive.)
- Cycle found → project load fails, naming the cycle path (`a.x → b.y → a.x`).

Runtime backstop: an evaluation depth cap (e.g. 32, module constant next to the store's `MAX_DISPATCH_DEPTH`); exceeding it raises `DynamicFieldEvalError`. With static detection this is unreachable in practice — it guards against future grammar features that make dependencies dynamic.

**Why both**: static detection gives authors a precise, early error; the cap makes the evaluator safe by construction rather than by invariant.

### D8 — Runtime evaluation errors fail loud

A dynamic field whose expression raises at runtime (type error, missing reference) raises `DynamicFieldEvalError` through the normal read path. In the engine, this surfaces via the existing error path (engine error → `ResponseErrorMessage` to the client) — a broken story definition is a definition bug, not a player-facing state, and a silent fallback (e.g. `None`) would propagate into prompts and comparisons in ways that are far harder to debug.

**Why not fall back to a default**: dynamic fields have no static default — the expression *is* the definition. There is no sensible value to invent.
**Alternative considered**: log-and-`None` with a warning — rejected: `None` in a numeric comparison or prompt line masks the bug for the rest of the session.

### D9 — Module layout: stay in `story/conditions` + `story/schemas/expression`

- `story/conditions/grammar.py`: unified `expr` parser, `ArithExpr`, `parse_bool_expr` (unchanged signature) + `parse_value_expr` (same parser, `=` prefix handling).
- `story/conditions/evaluator.py`: `eval_value` + arithmetic on `BoolExprEvaluator`.
- `story/schemas/expression.py`: `ValueExprDefinition` next to `BoolExprDefinition`.
- `story/schemas/entity.py`: conversion step (D3) + cycle detection (D7) in the entity/entity-type build pipeline.
- `story/context.py`: evaluator instance + `get_field` tier (D4).
- `story/errors.py`: `DynamicFieldEvalError`, read-only error.

**Why**: `story/conditions` is the established home of the expression language (triggers already depend on it); a new `story/expressions/` package would be churn with no boundary benefit. The archon boundary tests should keep passing unchanged.

## Risks / Trade-offs

- **[Grammar unification regresses trigger parsing]** → `parse_bool_expr` keeps its exact contract; the full existing trigger/conditions test suite must pass unchanged; add explicit tests that legacy condition strings (incl. `in`, parentheses, lists in `BoolExprDefinition`) parse identically.
- **[Evaluation cost on hot paths]** (system prompt renders every step; `get_field` is called per template variable) → AST parsed once at load; evaluation is a tree walk over story-scale graphs. No caching added; measure in the broken-bulb integration test if a regression appears.
- **[Raw `getattr` reads of dynamic fields outside `get_field`]** (debug dumps, future code) → task verifies all read paths (templates, tools, evaluator, EntityView) route through `get_field`; `ValueExprDefinition`'s `__str__` returns the source expression so accidental string use is visibly wrong, not silently a value.
- **[Author confusion: expression vs. literal string starting with `=`]** → any static string starting with `=` is now an expression and will fail to parse at load with a message explaining the `=` convention; documented in the change's docs update.
- **[Load-time cycle detection is head-reference only]** → documented limitation in D7; deeper dynamic chains cannot form cycles (static fields terminate recursion), so head-only edges are complete.
- **[Rollback breaks projects that adopted `=` fields]** → author-facing and expected; rollback note in the archive summary.

## Migration Plan

1. No data migration: state snapshots store overrides only (D6), schema unchanged.
2. Ship as a pure addition — projects without `=` fields are byte-for-byte unaffected (verified by the existing suite).
3. Docs: mark Dynamic Fields implemented in `docs/session-state/architecture.md` and `steps-overview.md`; extend the broken-bulb example story (or docs) with a dynamic field + a trigger that reads it.
4. Rollback: revert the merge; only projects using `=` fields are affected (load failure with a clear parse/feature error).

## Open Questions

- Should `ValueExprDefinition` be introspectable via the API/frontend (e.g. show the expression source in a story editor)? — assumed no for now; the field value is what consumers see.
- Parenthesized sub-expressions: planned as part of the unified `expr` primary (D1) — confirm no authoring use case needs `#`-style named groups (none known).
- Precedence of `in` relative to arithmetic: treated as comparison-level (`a + b in coll`) — confirm acceptable.
