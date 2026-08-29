> **Coordination:** backend-only change. Grammar work (section 1) must land before evaluator (2) and schema/load-time work (3); sections 4-5 build on all three. Verify against the full trigger/conditions test suite at every step — the grammar unification (design D1) must keep legacy condition strings parsing identically.

## 1. Unified expression grammar

- [ ] 1.1 Restructure `story/conditions/grammar.py` around a single `expr` parser (pyparsing `infix_notation`): primary = `dot_path | literal | ( expr )`, then levels `* /` (left, new `ArithExpr`), `+ -` (left, `ArithExpr`), comparisons `== != < <= > >= in` (non-associative, existing `Comparison`), `not` (right), `and` (left), `or` (left)
- [ ] 1.2 Keep `bool_expr` as an alias of `expr` and `BoolExpr` as an alias of the value-expr union; `parse_bool_expr` keeps its exact signature and behavior (optional leading `=` stripped, full-match parse)
- [ ] 1.3 Add `parse_value_expr(expression) -> Expr` (same parser, `=` prefix stripped, `ValueError` with parse details on failure)
- [ ] 1.4 Add `ArithExpr` AST node (left, operator, right; frozen dataclass) to the grammar module
- [ ] 1.5 Grammar unit tests in `tests/llm_gamebook/story/conditions/test_grammar.py`: precedence (`a + b * c`, `a + b < c`), parenthesization, arithmetic nodes, comparisons as value expressions, and a regression set asserting legacy condition strings (incl. `in`, `not`, nested `and`/`or`, dot paths, literals) parse to the same AST shape as before

## 2. Evaluator: value evaluation + arithmetic

- [ ] 2.1 Add `DynamicFieldEvalError` (field name + expression source) and a read-only-field error to `story/errors.py`
- [ ] 2.2 Add `eval_value(expr) -> EntityProperty` to `BoolExprEvaluator`: `ArithExpr` with design-D2 type rules (int/int→int for `+ - *`, `/`→float, float operand→float, str/bool/entity/collection operand→`ExpressionEvalError`), `Comparison`→bool, dot paths/literals via existing resolution; `eval` keeps its bool contract incl. the stored-`BoolExprDefinition` special case
- [ ] 2.3 Add a runtime evaluation depth cap (module constant, cf. store `MAX_DISPATCH_DEPTH`) raising `DynamicFieldEvalError` when exceeded
- [ ] 2.4 Evaluator unit tests in `tests/llm_gamebook/story/conditions/test_evaluator.py`: `eval_value` for dot paths, literals, comparisons-as-values, arithmetic (all D2 type cases), nested expressions; error cases identify field + expression source; `eval` bool behavior unchanged

## 3. Load-time: `ValueExprDefinition`, field conversion, cycle detection

- [ ] 3.1 Add `ValueExprDefinition` to `story/schemas/expression.py` (next to `BoolExprDefinition`): wraps the parsed AST, keeps the source string, `model_validator(mode="before")` parses `=`-prefixed strings via `parse_value_expr`
- [ ] 3.2 Convert dynamic fields at entity construction (design D3): in the entity build pipeline (`BaseEntity` `post_init` hook), scan declared model fields and `extra="allow"` attributes; replace any `str` starting with `=` with a parsed `ValueExprDefinition`; parse failure raises `ValueError` naming entity, field, and parse problem (project load fails)
- [ ] 3.3 Implement static cycle detection at project load: build the head-reference dependency graph over dynamic fields (edge A→B when A's AST contains a dot path whose head `(entity_id, field)` is dynamic field B); a cycle fails load naming the cycle path (e.g. `a.x → b.y → a.x`)
- [ ] 3.4 `ValueExprDefinition.__str__` returns the source expression (accidental string use is visibly wrong)
- [ ] 3.5 Load-time tests: dynamic field parsed and stored (trait-declared `str` field *and* extra attribute), unparseable field fails load with entity/field named, static strings (not prefixed with `=`) unchanged, self-cycle, indirect cycle with path, diamond dependency loads, legacy projects without `=` fields load identically

## 4. Resolution + write guard

- [ ] 4.1 `StoryContext.__init__` constructs the bound evaluator once (project + context); `get_field` gains the middle tier: default is `ValueExprDefinition` → `eval_value`, wrapped so failures raise `DynamicFieldEvalError` naming the field
- [ ] 4.2 Write guard (design D6): `SessionState` accepts an optional read-only field set (frozen `(entity_id, field_name)` pairs) injected by `StoryContext` from the project's dynamic fields; `set_field` raises the read-only error for those fields; `SessionState` without the injection behaves exactly as today
- [ ] 4.3 Verify all write paths (reducers, tools) route through `SessionState.set_field` (audit + assertion test if cheap)
- [ ] 4.4 Resolution tests in `tests/llm_gamebook/story/`: three-tier precedence (override > dynamic > static), override shadows dynamic, nested dynamic fields, re-evaluation after a state change, setting a dynamic field raises, unguarded `SessionState` unaffected

## 5. Engine integration

- [ ] 5.1 Runtime eval error surfaces via the existing engine error path: integration test — a dynamic field whose expression raises at runtime (type error / missing reference) fails the agent step with the field + expression in the error, no silent `None`
- [ ] 5.2 Trigger integration test: a trigger condition referencing a dynamic field fires with the evaluated value (spec: "Trigger conditions read dynamic fields transparently")
- [ ] 5.3 Snapshot/restore tests: a step that only changed dynamic fields stores no dynamic-field entries in the message state snapshot; restoring/forking to a historical state re-evaluates dynamic fields against the restored state
- [ ] 5.4 Audit read paths: confirm templates (`EntityView` in `story/template_view.py`), tools, and the evaluator all resolve fields via `StoryContext.get_field` so they pick up evaluated values; add a template-rendering test with a dynamic field

## 6. Example + docs

- [ ] 6.1 Extend the broken-bulb example story (`examples/llm-gamebook/broken-bulb/llm-gamebook.yaml`) with a dynamic field (and a trigger or function that reads it) exercised by the existing broken-bulb integration tests
- [ ] 6.2 `docs/session-state/architecture.md`: Dynamic Fields section → implemented (expression language, read-only semantics, override shadowing, load-time cycle detection)
- [ ] 6.3 `docs/session-state/steps-overview.md`: remove "Dynamic field evaluation (`=expression`)" from the not-implemented list; add a row/entry for this change

## 7. Verification

- [ ] 7.1 `ruff check backend/` and `ruff format --check backend/`
- [ ] 7.2 `mypy backend/`
- [ ] 7.3 `pytest backend/` full suite green (incl. full trigger/conditions regression from section 1)
