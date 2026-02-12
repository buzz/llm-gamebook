## ADDED Requirements

### Requirement: Entity functions field
The system SHALL allow entities to define their own Pydantic AI tool functions via a `functions` field in the entity definition.

#### Scenario: Function definition at entity level
- **GIVEN** an entity definition with a `functions` field
- **WHEN** the entity is instantiated
- **THEN** the entity SHALL have access to the specified function definitions
- **AND** the functions SHALL be available to the GraphTrait for tool generation

### Requirement: Entity-specific transition functions
The system SHALL allow each graph entity to define its own transition function with a unique name.

#### Scenario: Multiple story arc transitions
- **GIVEN** two story arc entities (Main, The Meeting) each with a transition function
- **WHEN** tools are registered with Pydantic AI
- **THEN** no consistency error SHALL be raised
- **AND** each entity's transition function SHALL operate on its own graph

#### Scenario: Main story arc transition
- **GIVEN** the Main story arc entity with a transition function named `main_transition`
- **WHEN** the LLM calls the function to advance the story
- **THEN** the system SHALL transition the Main entity to the specified node

#### Scenario: The Meeting story arc transition
- **GIVEN** The Meeting story arc entity with a transition function named `the_meeting_transition`
- **WHEN** the LLM calls the function to advance the story
- **THEN** the system SHALL transition The Meeting entity to the specified node

### Requirement: Backward compatibility with single-entity types
The system SHALL maintain compatibility with single-entity types that previously defined functions at the entity type level.

#### Scenario: Migration of LocationGraph configuration
- **GIVEN** a LocationGraph entity type with a single locations entity
- **WHEN** the functions are moved from entity type to entity
- **THEN** the system SHALL generate the same transition tools as before

### Requirement: GraphTrait accesses entity-level functions
The system SHALL update GraphTrait.get_tools() to access functions from the entity instance rather than the entity type.

#### Scenario: Tool generation from entity functions
- **GIVEN** an entity with a GraphTrait and a function definition
- **WHEN** get_tools() is called
- **THEN** the function specification SHALL be read from self.functions
- **AND** a tool SHALL be generated following the existing transition tool pattern
