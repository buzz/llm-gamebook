> **Coordination:** backend-only change. Grammar work (section 1) must land before evaluator (2) and schema/load-time work (3); sections 4-5 build on all three. Verify against the full trigger/conditions test suite at every step — the grammar unification (design D1) must keep legacy condition strings parsing identically.

## 1. Unified expression grammar

- [x] 1.1 Restructure `story/conditions/grammar.py` around a single `expr` parser (pyparsing `infix_notation`): primary = `dot_path | literal | ( expr )`, then levels `* /` (left, new `ArithExpr`), `+ -` (left, `ArithExpr`), comparisons `== != < <= > >= in` (non-associative, existing `Comparison`), `not` (right), `and` (left), `or` (left)
- [x] 1.2 Keep `bool_expr` as an alias of `expr` and `BoolExpr` as an alias of the value-expr union; `parse_bool_expr` keeps its exact signature and behavior (optional leading `=` stripped, full-match parse)
- [x] 1.3 Add `parse_value_expr(expression) -> Expr` (same parser, `=` prefix stripped, `ValueError` with parse details on failure)
- [x] 1.4 Add `ArithExpr` AST node (left, operator, right; frozen dataclass) to the grammar module
- [x] 1.5 Grammar unit tests in `tests/llm_gamebook/story/conditions/test_grammar.py`: precedence (`a + b * c`, `a + b < c`), parenthesization, arithmetic nodes, comparisons as value expressions, and a regression set asserting legacy condition strings (incl. `in`, `not`, nested `and`/`or`, dot paths, literals) parse to the same AST shape as before

## 2. Evaluator: value evaluation + arithmetic

- [x] 2.1 Add `DynamicFieldEvalError` (field name + expression source) and a read-only-field error to `story/errors.py`
- [x] 2.2 Add `eval_value(expr) -> EntityProperty` to `BoolExprEvaluator`: `ArithExpr` with design-D2 type rules (int/int→int for `+ - *`, `/`→float, float operand→float, str/bool/entity/collection operand→`ExpressionEvalError`), `Comparison`→bool, dot paths/literals via existing resolution; `eval` keeps its bool contract incl. the stored-`BoolExprDefinition` special case
- [x] 2.3 Add a runtime evaluation depth cap (module constant, cf. store `MAX_DISPATCH_DEPTH`) raising `DynamicFieldEvalError` when exceeded
- [x] 2.4 Evaluator unit tests in `tests/llm_gamebook/story/conditions/test_evaluator.py`: `eval_value` for dot paths, literals, comparisons-as-values, arithmetic (all D2 type cases), nested expressions; error cases identify field + expression source; `eval` bool behavior unchanged

## 3. Load-time: `ValueExprDefinition`, field conversion, cycle detection

- [x] 3.1 Add `ValueExprDefinition` to `story/schemas/expression.py` (next to `BoolExprDefinition`): wraps the parsed AST, keeps the source string, `model_validator(mode="before")` parses `=`-prefixed strings via `parse_value_expr`
- [x] 3.2 Convert dynamic fields at project load (design D3): scan declared model fields and `extra="allow"` attributes of every entity; replace any `str` starting with `=` with a parsed `ValueExprDefinition`; parse failure raises `ValueError` naming entity, field, and parse problem (project load fails). Implemented in the `Project.from_definition` load pipeline (`convert_dynamic_fields` in `story/schemas/project.py`) rather than a `BaseEntity.post_init` hook: trait `post_init` overrides do not call super (so the base hook does not reliably run) and `entity.py` cannot import the expression module (import cycle via `conditions.evaluator`)
- [x] 3.3 Implement static cycle detection at project load: build the head-reference dependency graph over dynamic fields (edge A→B when A's AST contains a dot path whose head `(entity_id, field)` is dynamic field B); a cycle fails load naming the cycle path (e.g. `a.x → b.y → a.x`)
- [x] 3.4 `ValueExprDefinition.__str__` returns the source expression (accidental string use is visibly wrong)
- [x] 3.5 Load-time tests: dynamic field parsed and stored (trait-declared `str` field *and* extra attribute), unparseable field fails load with entity/field named, static strings (not prefixed with `=`) unchanged, self-cycle, indirect cycle with path, diamond dependency loads, legacy projects without `=` fields load identically

## 4. Resolution + write guard

- [x] 4.1 `StoryContext` constructs the bound evaluator once (cached `evaluator` property, project + context); `get_field` gains the middle tier: `ValueExprDefinition` → `eval_value`, wrapped so failures raise `DynamicFieldEvalError` naming the field
- [x] 4.2 Write guard (design D6): `SessionState` accepts an optional read-only field set (frozen `(entity_id, field_name)` pairs) derived by `StoryContext` from the project's dynamic fields; `set_field` raises `DynamicFieldReadOnlyError` for those fields; the set survives state cloning (`Store._clone_state`), the reset reducer, and `CoreActionExecutor._restore`; `SessionState` without the injection behaves exactly as today
- [x] 4.3 Write-path audit: the only mutator of session state is `SessionState.set_field` (guarded); the only reducer writing state (`graph/transition`) and the only whole-state replacement (`store.set_state` in `_restore`) both route through the guarded API — covered by a reducer dispatch test
- [x] 4.4 Resolution tests in `tests/llm_gamebook/story/test_dynamic_resolution.py`: three-tier precedence, override shadows dynamic expression inputs, nested dynamic fields, re-evaluation after a state change, setting a dynamic field raises, guard survives dispatch + reset, unguarded `SessionState` unaffected, eval errors name field + source

## 5. Engine integration

- [x] 5.1 Runtime eval error surfaces via the existing engine error path: `ExpressionEvalError` (incl. `DynamicFieldEvalError`) added to the engine's `generate_response` except tuple; integration test — a dynamic field whose expression raises at runtime fails the agent step with the field + expression in the `ResponseErrorMessage`, no silent `None`
- [x] 5.2 Trigger integration test: a trigger condition referencing a dynamic field (`main.at_end` = `=main.current_node_id == 'end'`) fires with the evaluated value after a graph transition (spec: "Trigger conditions read dynamic fields transparently")
- [x] 5.3 Snapshot/restore tests: state snapshots store only stored (non-dynamic) overrides — dynamic fields never enter session state; restoring a historical snapshot re-evaluates dynamic fields against the restored state and keeps the write guard in force
- [x] 5.4 Audit read paths: `EntityView` (story/template_view.py) now resolves via `StoryContext.get_field` (session > dynamic > entity default) instead of raw session + `getattr`; evaluator, session-field resolvers, and templates all pick up evaluated values; EntityView + system-prompt template-rendering tests with dynamic fields

## 6. Example + docs

- [x] 6.1 Extend the broken-bulb example story (`examples/llm-gamebook/broken-bulb/llm-gamebook.yaml`) with a dynamic field (and a trigger or function that reads it) exercised by the existing broken-bulb integration tests
- [x] 6.2 `docs/session-state/architecture.md`: Dynamic Fields section → implemented (expression language, read-only semantics, override shadowing, load-time cycle detection)
- [x] 6.3 `docs/session-state/steps-overview.md`: remove "Dynamic field evaluation (`=expression`)" from the not-implemented list; add a row/entry for this change

## 7. Verification

- [x] 7.1 `ruff check backend/` and `ruff format --check backend/`
- [x] 7.2 `mypy backend/`
- [x] 7.3 `pytest backend/` full suite green (incl. full trigger/conditions regression from section 1)
