## ADDED Requirements

### Requirement: Entity fields support dynamic expression values
The system SHALL treat an entity field value that is a string prefixed with `=` as a dynamic field: the remainder SHALL be parsed as a value expression when the project loads, and the parsed expression SHALL be stored on the field together with its source string. Field values not prefixed with `=` SHALL remain static values with unchanged behavior.

#### Scenario: Dynamic field is parsed at project load
- **GIVEN** a project YAML with an entity field `health: "=player.max_hp - player.injury"`
- **WHEN** the project is loaded
- **THEN** the field SHALL hold the parsed value expression
- **AND** the expression's source string SHALL be preserved for diagnostics

#### Scenario: Unparseable dynamic field fails project load
- **GIVEN** a project YAML with an entity field `health: "=player.max_hp player.injury"`
- **WHEN** the project is loaded
- **THEN** loading SHALL fail with an error naming the entity, the field, and the parse problem

#### Scenario: Static strings are unaffected
- **GIVEN** a project YAML with an entity field `mood: "restless"`
- **WHEN** the project is loaded and the field is read
- **THEN** the static value `"restless"` SHALL be returned unchanged

### Requirement: Value expression grammar
Value expressions SHALL support: dot paths (`entity.field` and deeper chains), literals (string, integer, float, boolean), comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`, `in`), boolean combinators (`not`, `and`, `or`), arithmetic (`+`, `-`, `*`, `/`), and parenthesized sub-expressions. Comparison and boolean operators SHALL be usable as field values, evaluating to a boolean. The expression language used by trigger conditions SHALL be the same grammar, so conditions gain the same arithmetic and parenthesization support.

#### Scenario: Dot path field value
- **GIVEN** a dynamic field `location_name: "=world.current_name"`
- **AND** `world.current_name` is `"The Village"` (effective value)
- **WHEN** the dynamic field is evaluated
- **THEN** the value SHALL be `"The Village"`

#### Scenario: Arithmetic field value
- **GIVEN** a dynamic field `total_kills: "=player.kills + player.boss_kills * 2"`
- **AND** `player.kills` is `3` and `player.boss_kills` is `1`
- **WHEN** the dynamic field is evaluated
- **THEN** the value SHALL be `5`

#### Scenario: Comparison as boolean field value
- **GIVEN** a dynamic field `is_danger: "=player.hp < 20"`
- **AND** `player.hp` is `15`
- **WHEN** the dynamic field is evaluated
- **THEN** the value SHALL be `true`

#### Scenario: Trigger condition uses arithmetic
- **GIVEN** a trigger condition `=player.score > player.target * 2`
- **WHEN** the condition is evaluated
- **THEN** it SHALL evaluate as the arithmetic comparison, not fail to parse

### Requirement: Arithmetic type rules
Arithmetic operators SHALL apply only to numeric operands. `int op int` SHALL produce an `int` for `+`, `-`, `*` and a `float` for `/` (true division). Any `float` operand SHALL produce a `float`. A `str`, `bool`, entity, or collection operand SHALL be an evaluation error.

#### Scenario: Integer division produces float
- **GIVEN** a dynamic field `share: "=player.loot / 2"`
- **AND** `player.loot` is `7`
- **WHEN** the dynamic field is evaluated
- **THEN** the value SHALL be `3.5`

#### Scenario: Mixed int and float produces float
- **GIVEN** a dynamic field `weighted: "=player.level + 0.5"`
- **AND** `player.level` is `3`
- **WHEN** the dynamic field is evaluated
- **THEN** the value SHALL be `3.5`

#### Scenario: String operand is an error
- **GIVEN** a dynamic field `bad: "=player.name + 1"`
- **WHEN** the dynamic field is evaluated
- **THEN** an evaluation error SHALL be raised identifying the field and its expression source

### Requirement: Dynamic fields evaluate against the effective state
A dynamic field SHALL be evaluated against the current effective state at the time of access: referenced fields SHALL resolve with the precedence session override > dynamic evaluation > static default. A dynamic field SHALL be able to reference other dynamic fields.

#### Scenario: Dynamic field sees session override
- **GIVEN** a dynamic field `remaining: "=world.total - player.done"`
- **AND** the session state overrides `player.done` to `4` (default `0`)
- **WHEN** `remaining` is evaluated
- **THEN** it SHALL use `4` for `player.done`

#### Scenario: Chained dynamic fields
- **GIVEN** dynamic field `a: "=b + 1"` and dynamic field `b: "=player.base * 2"`
- **AND** `player.base` is `5`
- **WHEN** field `a` is evaluated
- **THEN** the value SHALL be `11`

#### Scenario: Re-evaluation after state change
- **GIVEN** a dynamic field `double_hp: "=player.hp * 2"` with `player.hp` at `10`
- **WHEN** an action changes `player.hp` to `20` and the field is evaluated again
- **THEN** the value SHALL be `40`

### Requirement: Dynamic fields are read-only and derived
Dynamic fields SHALL NOT be writable: setting a session-state override for a field that is dynamic in the project SHALL raise an error identifying the field and explaining that dynamic fields are read-only. Dynamic fields SHALL NOT be written to session state or stored in message state snapshots. An override for a field that exists in previously saved session state SHALL shadow the dynamic expression (state wins). Restoring or forking to a historical state SHALL re-evaluate dynamic fields against the restored state.

#### Scenario: Setting a dynamic field is rejected
- **GIVEN** a project where field `x` is dynamic
- **WHEN** a reducer or tool sets field `x`
- **THEN** an error SHALL be raised identifying the field and that it is a read-only dynamic field

#### Scenario: Pre-existing override shadows dynamic field
- **GIVEN** a saved session state containing an override for field `x`
- **AND** the project now defines `x` as dynamic
- **WHEN** the effective value of `x` is read
- **THEN** the stored override SHALL be returned without evaluating the expression

#### Scenario: Snapshots never contain dynamic fields
- **GIVEN** a session in which only dynamic fields changed during a step
- **WHEN** the step's message state snapshot is stored
- **THEN** the snapshot SHALL NOT contain entries for dynamic fields

#### Scenario: Restore re-evaluates dynamic fields
- **GIVEN** dynamic field `total: "=player.a + player.b"`
- **AND** a historical state where `player.a` is `1` and `player.b` is `2`
- **WHEN** the session is restored to that state and `total` is read
- **THEN** the value SHALL be `3`

### Requirement: Circular dynamic field dependencies are rejected at project load
The system SHALL detect cycles among dynamic fields at project load by following field references in stored expressions. A circular dependency SHALL fail project loading with an error naming the cycle path.

#### Scenario: Self-reference fails load
- **GIVEN** a dynamic field `x: "=x + 1"`
- **WHEN** the project is loaded
- **THEN** loading SHALL fail with an error naming the cycle

#### Scenario: Indirect cycle fails load with path
- **GIVEN** dynamic field `a.x: "=b.y"` and dynamic field `b.y: "=a.x"`
- **WHEN** the project is loaded
- **THEN** loading SHALL fail with an error naming the cycle `a.x → b.y → a.x`

#### Scenario: Shared dependency without cycle loads
- **GIVEN** dynamic field `a.x: "=base.v"` and dynamic field `b.y: "=base.v"`
- **WHEN** the project is loaded
- **THEN** the project SHALL load successfully

### Requirement: Runtime evaluation errors fail loud
If a dynamic field's expression raises an error during evaluation (type error, missing reference), the system SHALL raise a dynamic-field evaluation error identifying the field and its expression source. In the engine, the error SHALL surface through the existing error path rather than being replaced by a silent fallback value.

#### Scenario: Runtime type error identifies the field
- **GIVEN** a dynamic field `bad: "=player.name * 2"`
- **WHEN** the field is evaluated during an agent step
- **THEN** the error SHALL name field `bad` and its expression source
- **AND** the error SHALL surface via the engine's error handling instead of returning a default value

### Requirement: Trigger conditions read dynamic fields transparently
Trigger conditions evaluated against effective field values SHALL resolve dynamic fields with their evaluated values, without any change to trigger definition or evaluation behavior.

#### Scenario: Trigger condition references a dynamic field
- **GIVEN** a dynamic field `is_ready: "=player.level >= 5"`
- **AND** a trigger with condition `=player.is_ready`
- **AND** `player.level` is `5`
- **WHEN** triggers are evaluated after an agent step
- **THEN** the trigger SHALL fire because the condition sees `is_ready` as `true`
