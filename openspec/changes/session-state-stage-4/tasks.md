## 1. Schema Updates

- [ ] 1.1 Add `TriggerDefinition` model in schema/entity.py (name: str, condition: str, args: dict)
- [ ] 1.2 Update `EntityTypeDefinition` to include optional `triggers: list[TriggerDefinition]`
- [ ] 1.3 Add validation for trigger condition (must be valid bool expression)

## 2. EntityType Runtime Updates

- [ ] 2.1 Add `triggers` attribute to EntityType class
- [ ] 2.2 Update `EntityType.from_definition()` to load triggers
- [ ] 2.3 Add `get_triggers()` method to EntityType

## 3. BoolExprEvaluator Integration

- [ ] 3.1 Update BoolExprEvaluator to accept effective field resolver function
- [ ] 3.2 Create resolver that checks session state first, then project defaults
- [ ] 3.3 Handle dynamic field references (=expressions) in trigger conditions

## 4. TriggerEval Middleware Implementation

- [ ] 4.1 Replace stub TriggerEval middleware with functional implementation
- [ ] 4.2 Implement trigger evaluation logic: iterate all triggers, evaluate conditions
- [ ] 4.3 Dispatch trigger actions when conditions are true
- [ ] 4.4 Pass effective fields to BoolExprEvaluator
- [ ] 4.5 Implement loop prevention: track dispatched action types, prevent re-dispatch

## 5. Trigger Execution Flow

- [ ] 5.1 Ensure triggers evaluate after user actions (order in middleware chain)
- [ ] 5.2 Handle multiple triggers firing in same step
- [ ] 5.3 Preserve trigger order from YAML

## 6. Testing

- [ ] 6.1 Add unit tests for trigger schema parsing
- [ ] 6.2 Add unit tests for EntityType triggers loading
- [ ] 6.3 Add unit tests for trigger condition evaluation with effective fields
- [ ] 6.4 Add unit tests for TriggerEval middleware
- [ ] 6.5 Add unit tests for multiple triggers firing
- [ ] 6.6 Add unit tests for loop prevention
- [ ] 6.7 Add integration test for full trigger flow

## 7. Error Handling

- [ ] 7.1 Handle invalid trigger condition syntax gracefully
- [ ] 7.2 Handle missing entity referenced in condition
- [ ] 7.3 Log trigger evaluation results for debugging
