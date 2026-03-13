# CHANGELOG

<!-- version list -->

## v0.3.0 (2026-03-13)

### Bug Fixes

- Fix model message history
  ([`d37043a`](https://github.com/buzz/llm-gamebook/commit/d37043acac1f1737db35b9f53e616571db1e1585))

- Remove `id` field from `SessionUpdate`
  ([`3d3505d`](https://github.com/buzz/llm-gamebook/commit/3d3505d901141060b6c377bb9ebdd4b7589bd2f1))

- **backend**: Add validation and error handling for state operations
  ([`83d446d`](https://github.com/buzz/llm-gamebook/commit/83d446d0bfa690b0fc1f7c4ad8a217a832c5d612))

- **backend**: Allow @property decorator access in `_resolve_entity_property`
  ([`754eaee`](https://github.com/buzz/llm-gamebook/commit/754eaee0f2bf8d3c10fb2935ac37e10bc8966a03))

- **backend**: Allow engine model to be `None`, raise `HTTPException` on missing session
  ([`8283187`](https://github.com/buzz/llm-gamebook/commit/828318758e1e61471b49bcaec367c1e0503819e8))

- **backend**: Always send final chunk in `StreamRunner`, configurable debounce value
  ([`32acac1`](https://github.com/buzz/llm-gamebook/commit/32acac1c53cdb623c9a620176d8e943199a953a3))

- **backend**: Catch `KeyError` in `EntityType`
  ([`ab0a5e4`](https://github.com/buzz/llm-gamebook/commit/ab0a5e4fa1f35d87214a948ecfff0781f10bcff9))

- **backend**: Define grammar elements as dataclasses (not NamedTuple) so equality check works
  ([`7c4c886`](https://github.com/buzz/llm-gamebook/commit/7c4c8867ebc5b68fc47e59fff2e8a9eff5810234))

- **backend**: Don't overwrite attributes in `Part::from_model_parts()`
  ([`4598dd1`](https://github.com/buzz/llm-gamebook/commit/4598dd1999944ff238f0e6fa66629bc4ebf335d4))

- **backend**: Fix grammar to reject dot paths with whitespace like `foo_bar .current_node.id` and
  keywords
  ([`4495ff9`](https://github.com/buzz/llm-gamebook/commit/4495ff982177cf93fb9f5828781d51c4d797c696))

- **backend**: Fix message history
  ([`73d50d2`](https://github.com/buzz/llm-gamebook/commit/73d50d26868841203cda4725901dd7e95a1ee935))

- **backend**: Graceful shutdown database engine
  ([`c296a5c`](https://github.com/buzz/llm-gamebook/commit/c296a5c455f0ee7a7faecc788cea05b09e8b5dba))

- **backend**: Handle error in `GraphTrait::transition()`
  ([`b80e38c`](https://github.com/buzz/llm-gamebook/commit/b80e38c9b19468efd36047290390f937b6aeb142))

- **backend**: Improve `TraitDefinition::normalize()`
  ([`aa68628`](https://github.com/buzz/llm-gamebook/commit/aa6862863feff0085697407e813f81db7add9991))

- **backend**: Instantiate model and story state inside `EngineManager`
  ([`358e32f`](https://github.com/buzz/llm-gamebook/commit/358e32f13584313a21af5a8b7a8ed99b673eff8b))

- **backend**: Pass UUID to crud functions
  ([`c22b8c1`](https://github.com/buzz/llm-gamebook/commit/c22b8c122a6e4e0e109ea14df26763cf90f5cc74))

- **backend**: Properly determine IDs in `SessionAdapter::append_messages()`
  ([`6a6999d`](https://github.com/buzz/llm-gamebook/commit/6a6999dc6da5e55a42fb2ac1566a66119b2f1406))

- **backend**: Remove `UsageLimits` which seems to produce bogus errors
  ([`ddf4a41`](https://github.com/buzz/llm-gamebook/commit/ddf4a41cf2e3ea53ef53f6a593b1ae0044ae0086))

- **backend**: Resolve db models circular dependencies and type resolution
  ([`0181c93`](https://github.com/buzz/llm-gamebook/commit/0181c936c485d32a5d236f96204488635ea4c89d))

- **backend**: Serialize ToolCallPart args before storing to DB
  ([`b539f9c`](https://github.com/buzz/llm-gamebook/commit/b539f9c88a77afef6d9e0c1ef6a71148597b2ed3))

- **backend**: Support more than 2 operands in `bool_expr` infix_notation
  ([`fdfc5b4`](https://github.com/buzz/llm-gamebook/commit/fdfc5b4e6e2fce57965bd9bb007ad36a8c5c0a62))

- **backend**: Use proper types in `llm_gamebook.story.types`
  ([`0920445`](https://github.com/buzz/llm-gamebook/commit/09204450988fd84b47dd19908d71c545ea7b8a34))

- **backend**: Use property decorator for `GraphTrait::current_node_id`
  ([`465a898`](https://github.com/buzz/llm-gamebook/commit/465a898b90453213f5bf2d581dc281471ce83d2a))

- **backend**: Use Pydantic AI's dynamic instructions, so we get dynamic system prompt within agent
  runs
  ([`218b6d5`](https://github.com/buzz/llm-gamebook/commit/218b6d55ab640504dc6b3b4e6abcd20fceae09f4))

- **frontend**: Add proper mime type for project image endpoint
  ([`68ed330`](https://github.com/buzz/llm-gamebook/commit/68ed330b548747b999d07f9a5e7ead8b7ae31755))

- **frontend**: Navigate to home when model config does not exist
  ([`54a48f9`](https://github.com/buzz/llm-gamebook/commit/54a48f9227556d9cc5051d718c7d04a8f3ac0591))

- **frontend**: Set `deltaSecs` to `null` if not streaming
  ([`929a2ea`](https://github.com/buzz/llm-gamebook/commit/929a2ea63f90fc8267a916a6ec4670a42c03e29c))

- **frontend**: Set stream status to false initially and update in reducer
  ([`8cc8e76`](https://github.com/buzz/llm-gamebook/commit/8cc8e769e4946a5c64c3d4a31e23ffbed7457199))

- **frontend**: Sort message in ascending order
  ([`8dabe0c`](https://github.com/buzz/llm-gamebook/commit/8dabe0c08dc7c76f616a34c3ac6d8907277df5ff))

### Chores

- Add add-storyengine-integration-tests change
  ([`55a9c9d`](https://github.com/buzz/llm-gamebook/commit/55a9c9dcbf57214ca25ff5baf92038f96fe76c23))

- Auto-fix ruff issues is VSCode
  ([`ce71497`](https://github.com/buzz/llm-gamebook/commit/ce71497cbbf878ed8ac7096f1143d85d6872927f))

- Exclude common folders in VSCode search
  ([`dac4ee0`](https://github.com/buzz/llm-gamebook/commit/dac4ee03ff578e3560b4ca45a51081afb6b1e0aa))

- Install OpenSpec
  ([`12bf170`](https://github.com/buzz/llm-gamebook/commit/12bf17007471a6abd21b6963320484f76f1d56bb))

- Temporarily exclude `llm_gamebook.tui` from mypy check
  ([`39447ca`](https://github.com/buzz/llm-gamebook/commit/39447ca79ca62865a29603d96366cad81e1154ea))

- Update AGENTS.md
  ([`d3012a5`](https://github.com/buzz/llm-gamebook/commit/d3012a59158cba197ce14fa9a3dfcd504d3eb3d8))

- **backend**: Fix mypy issues
  ([`0a99e3f`](https://github.com/buzz/llm-gamebook/commit/0a99e3ff822a19aae5eed8a229909bfc8be217f1))

- **backend**: Fix ruff issues
  ([`ddad228`](https://github.com/buzz/llm-gamebook/commit/ddad228c80fb2da594de3ef2fbffa3dcf2a8ddb0))

- **backend**: Minor change in log formatting
  ([`2221df2`](https://github.com/buzz/llm-gamebook/commit/2221df222620f138141055d560d15d0d25208a7c))

- **backend**: Strict mypy, add Pydantic mypy plugin
  ([`8f9d153`](https://github.com/buzz/llm-gamebook/commit/8f9d15343db2eb0ef1ba3b9b6b58acf78751ed9d))

- **backend**: Upgrade packages
  ([`0541f71`](https://github.com/buzz/llm-gamebook/commit/0541f71bcba50576a4db5e18a6650040dd36cbbe))

- **examples**: Fix property access
  ([`6aa44a7`](https://github.com/buzz/llm-gamebook/commit/6aa44a7979fbc40b9ee8c0b588ab8a60ddd4ba0c))

- **examples**: Use namespaced project folder structure
  ([`778350f`](https://github.com/buzz/llm-gamebook/commit/778350f6d21b047b3f2254b6f311d59bbecb44a4))

- **frontend**: Add prettier scripts
  ([`f583820`](https://github.com/buzz/llm-gamebook/commit/f583820f0edca4919824af5f530f530e870fbb37))

- **frontend**: Add typescript-plugin-css-modules
  ([`5f834c1`](https://github.com/buzz/llm-gamebook/commit/5f834c1f561a05001e485345801aadcd4b78692f))

- **frontend**: Fix lint issues
  ([`e0e0f1a`](https://github.com/buzz/llm-gamebook/commit/e0e0f1aa43c0e7e9716acc8da97d9bc804705cbf))

- **frontend**: Minor code formatting
  ([`6f88236`](https://github.com/buzz/llm-gamebook/commit/6f882368615df267fedaab056503ca8aab240a62))

- **frontend**: Upgrade packages, add eslint-plugin-unicorn
  ([`dd4a260`](https://github.com/buzz/llm-gamebook/commit/dd4a2604937029455c1a87da4b6e16de7150fe41))

### Code Style

- **frontend**: Adjust message line-height for readability
  ([`a583934`](https://github.com/buzz/llm-gamebook/commit/a583934cea4b636083c8f60f379580c7a5d69088))

- **frontend**: Improve Player component layout with CSS module
  ([`25c74b9`](https://github.com/buzz/llm-gamebook/commit/25c74b97c3b50d8812dd432f54079af24193e145))

### Documentation

- Add `editor.md`
  ([`e18a174`](https://github.com/buzz/llm-gamebook/commit/e18a174fe8c9d4c42f4b20d1ca3df1379deda49b))

- Add `session-state` documents
  ([`ce1bd93`](https://github.com/buzz/llm-gamebook/commit/ce1bd9387c6640422cb06c2b1b7ffb551506b8b8))

- Add `story-projects.md`
  ([`76f2037`](https://github.com/buzz/llm-gamebook/commit/76f2037bad1b6dfca46b8567711ab1ed5fcb1b0a))

- Add links of similar projects to `notes.md`
  ([`e8c9d16`](https://github.com/buzz/llm-gamebook/commit/e8c9d16c5d2f0fd498b51c9752c01e9cc41f3d4a))

- Add more node libraries to `notes.md`
  ([`d6b260d`](https://github.com/buzz/llm-gamebook/commit/d6b260d1d46f82fe876de27d493413c7cadf325c))

- Update `todos.md`
  ([`ebd37b5`](https://github.com/buzz/llm-gamebook/commit/ebd37b51666179bc1c617d50e0f49cd34d6572d5))

- Update `todos.md`
  ([`b881e66`](https://github.com/buzz/llm-gamebook/commit/b881e66b9ab254a9dd6ca88def96940b08d2737b))

- Update docs/story-projects.md
  ([`478c2f1`](https://github.com/buzz/llm-gamebook/commit/478c2f1cc1b0395324c0d0553a9505708125bde3))

### Features

- Add model config selection
  ([`cb87757`](https://github.com/buzz/llm-gamebook/commit/cb8775762cfe7630d0922b8c1c482a854abb38b9))

- Move entity functions to entity-level enabling per-entity tool definitions
  ([`57f587d`](https://github.com/buzz/llm-gamebook/commit/57f587d8be7ca21139ea39c645d524aec38bf638))

- Persist and display thinking time
  ([`d803ff9`](https://github.com/buzz/llm-gamebook/commit/d803ff9ec24ee0269c8e9087f1e0427683792c4c))

- **backend**: Action-driven state changes (add store to StoryContext)
  ([`a43a64e`](https://github.com/buzz/llm-gamebook/commit/a43a64e095aa8a34ffbab678eae59d34c2bd989b))

- **backend**: Action-driven state changes (GraphTrait refactor)
  ([`98ab0e6`](https://github.com/buzz/llm-gamebook/commit/98ab0e6b89050b0cfc4907c0dd078cd4ef0910d6))

- **backend**: Add dev mode with auto-reload to web command
  ([`f9e2b3b`](https://github.com/buzz/llm-gamebook/commit/f9e2b3b3733aa19d2a5d20dec4d49b7791f8c1c1))

- **backend**: Add message count to sessions and project filtering
  ([`e0606b5`](https://github.com/buzz/llm-gamebook/commit/e0606b57f2ceb5f5316cd13579ca4836d16799c6))

- **backend**: Add project image
  ([`5f63704`](https://github.com/buzz/llm-gamebook/commit/5f63704bb12a8bda8817117a4e23355aa2827b14))

- **backend**: Add Redux-inspired action system with typed payloads
  ([`3abdec5`](https://github.com/buzz/llm-gamebook/commit/3abdec5e2945985d4fdc4de4bff31af58a73fcbc))

- **backend**: Add SessionState with persistence
  ([`88600a4`](https://github.com/buzz/llm-gamebook/commit/88600a4a9460bcb1bb0513bbb1f8bdb57852d5f4))

- **backend**: Extend BoolExprDefinition to support raw booleans and mixed-type lists
  ([`de8b83a`](https://github.com/buzz/llm-gamebook/commit/de8b83abc59c15f03f7d714e8123304f6e86c875))

- **backend**: Implement `in` operator in comparison
  ([`e484365`](https://github.com/buzz/llm-gamebook/commit/e484365e5720aab8888ef5ee1b16d3edee473f62))

- **backend**: Lazy project/model initialization
  ([`21ef057`](https://github.com/buzz/llm-gamebook/commit/21ef0573382e6fae30e35d2d8ddb024df87b54f2))

- **backend**: Persist `ModelRequest.instructions` field
  ([`7839eac`](https://github.com/buzz/llm-gamebook/commit/7839eacdb60efcd9c8b1c31e09fcc3acebafffb9))

- **backend**: Session-aware template view layer
  ([`784777b`](https://github.com/buzz/llm-gamebook/commit/784777b21d6817c12d32f7222bdb5e01264e2859))

- **backend**: Store database in USER_DATA_DIR
  ([`469a551`](https://github.com/buzz/llm-gamebook/commit/469a5511d8c9250651c4e6db8475b97771675e64))

- **backend**: Support project directories
  ([`ccf29e7`](https://github.com/buzz/llm-gamebook/commit/ccf29e78e3c5c55b9ea1d3a3608d53f98290f345))

- **frontend**: Add custom theme with Spectral font and warm dark color palette
  ([`2d25255`](https://github.com/buzz/llm-gamebook/commit/2d25255700a8871d38d282b941ac2af5e2aad8a6))

- **frontend**: Add portal system for header toolbar
  ([`6ba4d37`](https://github.com/buzz/llm-gamebook/commit/6ba4d37b6d301c75f884262759ac6010f8b5db8f))

- **frontend**: Add project management UI components
  ([`d6c0d8c`](https://github.com/buzz/llm-gamebook/commit/d6c0d8c31101aac34b2e8cb300370a7a28b6d3af))

- **frontend**: Add project-filtered sessions to project details
  ([`e919169`](https://github.com/buzz/llm-gamebook/commit/e91916906ff0a2389566894c8f7cac2df58d0306))

- **frontend**: Add ProjectForm
  ([`ada2bf2`](https://github.com/buzz/llm-gamebook/commit/ada2bf2e3f01c964d41c5ebf5a2c306f99a99263))

- **frontend**: Add time formatting hooks and live duration display
  ([`8013b43`](https://github.com/buzz/llm-gamebook/commit/8013b43a77d08bfa954a4233c9e371e3538fa643))

- **frontend**: Implement type-safe named routes
  ([`0810241`](https://github.com/buzz/llm-gamebook/commit/08102412b593fb205d7a67c16c5544edc756dca9))

- **frontend**: Improve PageShell layout and show actual project title
  ([`087c873`](https://github.com/buzz/llm-gamebook/commit/087c8736d61ffe09ae9117c63d8807144d0c6a82))

- **frontend**: Improve player controls with keyboard shortcut and right-align user messages
  ([`5baa585`](https://github.com/buzz/llm-gamebook/commit/5baa585daf4c01772606b533d9049388413cc494))

- **frontend**: Project image
  ([`50ad71f`](https://github.com/buzz/llm-gamebook/commit/50ad71f3820f0ac81af40f786dfc9b25f57f3568))

- **frontend**: Replace BasicNavLink with CollapsibleNavLink supporting auto-expand on route match
  ([`0ce4515`](https://github.com/buzz/llm-gamebook/commit/0ce451575b9f5e1081ba6398d4e45f0574887631))

### Performance Improvements

- **frontend**: Optimize ModelConfigForm and InputSlider with memoization
  ([`33c564c`](https://github.com/buzz/llm-gamebook/commit/33c564c891d8931eff3c90e5dccca7f793756a40))

### Refactoring

- **backend**: Add StreamResult dataclass for type-safe streaming
  ([`8ef4d02`](https://github.com/buzz/llm-gamebook/commit/8ef4d02379225d63824f74cd58f61879057e3f16))

- **backend**: Code clean-up, types, renaming
  ([`3cfead9`](https://github.com/buzz/llm-gamebook/commit/3cfead949f8eb8a6dc952b4ca421e813b437a50a))

- **backend**: Extract `StreamRunner` into own package
  ([`e0892be`](https://github.com/buzz/llm-gamebook/commit/e0892bec226124ae58e85cf9c95ae9e751d801ed))

- **backend**: Improve database creation logging to show whether existing database is used
  ([`fc63f0e`](https://github.com/buzz/llm-gamebook/commit/fc63f0e3af5af634eace2ed1c15871750000d34e))

- **backend**: Merge `llm_gamebook.schemas` into `llm_gamebook.story.schemas`
  ([`129cee9`](https://github.com/buzz/llm-gamebook/commit/129cee9dca5c3b2c90ee038c07890f48945c7ad9))

- **backend**: Move utils function to tui
  ([`73929c7`](https://github.com/buzz/llm-gamebook/commit/73929c7c534dd14a8317ef9a53a21d3dbd26c5ef))

- **backend**: Refactor streaming to use granular messages
  ([`30d6096`](https://github.com/buzz/llm-gamebook/commit/30d609649a64b3678903fc9151652e6872578cbc))

- **backend**: Refine story module structure
  ([`ed99db5`](https://github.com/buzz/llm-gamebook/commit/ed99db517e732dfb83c3d70e86fcae91edce23e3))

- **backend**: Remove load_trait_reducers argument on Store
  ([`f228fcb`](https://github.com/buzz/llm-gamebook/commit/f228fcb8de46a92391488affe6df99a505f6210a))

- **backend**: Remove streaming parameter, always use streaming
  ([`8f9a3fb`](https://github.com/buzz/llm-gamebook/commit/8f9a3fbdcef7d79b8a44881644c2daf01c8e5320))

- **backend**: Rename `StoryContext::get_effective_field`->`get_field`
  ([`0ff8590`](https://github.com/buzz/llm-gamebook/commit/0ff8590f6ff27e67423fa3ce7b57ca8300117c3c))

- **backend**: Reorganize dependencies
  ([`4fec02a`](https://github.com/buzz/llm-gamebook/commit/4fec02ae27d6e35455aa132b30e8693b39957a76))

- **backend**: Standardize module name `schema`->`schemas`
  ([`0746b80`](https://github.com/buzz/llm-gamebook/commit/0746b80eefb5393ce1bb72b7e48bd2c33e413bc3))

- **backend**: Use `inspect.iscoroutinefunction()`
  ([`750e2ee`](https://github.com/buzz/llm-gamebook/commit/750e2eea3cb824dd779ffc2e4c17f1c781ab75a8))

- **backend**: Use dataclasses as bus message topics instead of strings
  ([`087d31c`](https://github.com/buzz/llm-gamebook/commit/087d31c37b2c1f2e43ce010ba4007d7efb0e808a))

- **backend**: Use explicit exceptions and decorator-based reducers
  ([`a64c3a0`](https://github.com/buzz/llm-gamebook/commit/a64c3a070b4db46d271cf50496b92a5e67ec5aaa))

- **frontend**: Consolidate player new page into gamebook view page
  ([`4962770`](https://github.com/buzz/llm-gamebook/commit/4962770416330da7e2de98f1c0c6e501e3cc74f0))

- **frontend**: Migrate to data-driven routing configuration
  ([`0cf4dc5`](https://github.com/buzz/llm-gamebook/commit/0cf4dc506d4a5f2b3d506486b71ecd7a08bb8f97))

- **frontend**: Refactor streaming to use granular messages
  ([`abd10d5`](https://github.com/buzz/llm-gamebook/commit/abd10d579c6e36f2791ac3f10832edca0d210b1b))

- **frontend**: Restructure components and add PageShell layout
  ([`1e1c2df`](https://github.com/buzz/llm-gamebook/commit/1e1c2dfcca153bcc8aeb2b5ba2e58a9c2ee3937c))

- **frontend**: Update route name `model-config.view`->`model-config.edit`
  ([`d48344c`](https://github.com/buzz/llm-gamebook/commit/d48344cd48912a1e464e42d7e2752814a687e043))

- **frontend**: Use consistent variable naming for `navigate`
  ([`ff3b088`](https://github.com/buzz/llm-gamebook/commit/ff3b088feff3b9b579c48b6ba36664aca6f6423c))

- **frontend**: Use context-based parent expansion for collapsible nav items
  ([`b009259`](https://github.com/buzz/llm-gamebook/commit/b009259fd9fd6a74d1bdfbc7ef1afb442cc3e0fa))

### Testing

- **backend**: Add `llm_gamebook.db.crud.message` tests
  ([`5cc0a65`](https://github.com/buzz/llm-gamebook/commit/5cc0a650306b7a0bff7278fe72e3f8233e02df00))

- **backend**: Add `llm_gamebook.engine._model_factory` tests
  ([`f8e2c31`](https://github.com/buzz/llm-gamebook/commit/f8e2c318d393ee8ef724d2d0e5faba9397642098))

- **backend**: Add `llm_gamebook.engine.message` tests
  ([`92473fe`](https://github.com/buzz/llm-gamebook/commit/92473fea9115bb97374d6e01ef66a4a86df578a6))

- **backend**: Add `llm_gamebook.engine.story_engine` tests
  ([`c846d70`](https://github.com/buzz/llm-gamebook/commit/c846d70ae7890cda51846686ee29609ac08a581c))

- **backend**: Add `llm_gamebook.web.schema.session` tests
  ([`b640769`](https://github.com/buzz/llm-gamebook/commit/b640769fc2bf0dace81ff90f44d28676ac87447e))

- **backend**: Add `llm_gamebook.web.websocket.handler` tests
  ([`222453b`](https://github.com/buzz/llm-gamebook/commit/222453bd32f619b516971d26da42166aa2fc39e7))

- **backend**: Add `llm_gamebook.web.websocket.router` tests
  ([`688f859`](https://github.com/buzz/llm-gamebook/commit/688f859181a94317d81e6b22247cf35434d0fd9b))

- **backend**: Add `model_config_router` tests
  ([`d7826b8`](https://github.com/buzz/llm-gamebook/commit/d7826b8c5394f5b0bff5ca067ebe25647047175f))

- **backend**: Add `session_router` tests
  ([`b996232`](https://github.com/buzz/llm-gamebook/commit/b996232637f42aed2451a04f8f48c7fcc59492c8))

- **backend**: Add and update tests for granular messages refactor
  ([`b19e27f`](https://github.com/buzz/llm-gamebook/commit/b19e27fd9f08a5e922749cfa99e9875ae1e57224))

- **backend**: Add many tests and test stubs
  ([`e5ace88`](https://github.com/buzz/llm-gamebook/commit/e5ace88613d5a75bf4b13b70afecdc484156501b))

- **backend**: Add more test stubs
  ([`2edb082`](https://github.com/buzz/llm-gamebook/commit/2edb082c64c959620c1956847c49653da4f5f31c))

- **backend**: Add more tests
  ([`26ab078`](https://github.com/buzz/llm-gamebook/commit/26ab078684d3e2583e96d7417e55e3a1c4450653))

- **backend**: Add remaining tests for `llm_gamebook.web.schema.websocket.message`
  ([`1e80c05`](https://github.com/buzz/llm-gamebook/commit/1e80c05ac5f865bed1ff880c77be6d1b20543326))

- **backend**: Add session_adapter session_id test
  ([`0977a29`](https://github.com/buzz/llm-gamebook/commit/0977a29e0904482259f02e2e535dd888c885366d))

- **backend**: Add some more session state tests
  ([`3454e31`](https://github.com/buzz/llm-gamebook/commit/3454e31caa157145c936f334ae5cd9899d0a2d45))

- **backend**: Add tests for `llm_gamebook.schema.validators`
  ([`cb5a236`](https://github.com/buzz/llm-gamebook/commit/cb5a236c680756cba76f777cc5383b1a657be9f7))

- **backend**: Add tests for `llm_gamebook.story.trait_registry`
  ([`ffd45ea`](https://github.com/buzz/llm-gamebook/commit/ffd45ea2aa0b7a30b1f8f006a80e99167c6cdbb1))

- **backend**: Add tests for `llm_gamebook.story.traits.described`
  ([`3355201`](https://github.com/buzz/llm-gamebook/commit/3355201ddb0f856b6128a740c2c9d0d82dc30d61))

- **backend**: Add tests for `llm_gamebook.utils`
  ([`a988499`](https://github.com/buzz/llm-gamebook/commit/a988499c70d63bc76f234acd915168302c145a66))

- **backend**: Add tests for `llm_gamebook.web.schema.websocket._convert_part`
  ([`6710f6f`](https://github.com/buzz/llm-gamebook/commit/6710f6f834b7d4b53f2c75630e072b90970fc58a))

- **backend**: Add tests for message persistence in story engine
  ([`437cf28`](https://github.com/buzz/llm-gamebook/commit/437cf28f0c0324d1ed96a1ed90c53ab728c74657))

- **backend**: Consolidate and add test fixtures
  ([`1f39a0d`](https://github.com/buzz/llm-gamebook/commit/1f39a0dde5e3c55cc35884bc5daa456e21781c0b))

- **backend**: Enable broken_bulb test by adding streaming support to MockModel
  ([`b4d5bba`](https://github.com/buzz/llm-gamebook/commit/b4d5bba1c06eb8304d435eef44a0e3a3731d41ed))

- **backend**: Expand BoolExprDefinition test coverage and conditional node fixtures
  ([`bcc16da`](https://github.com/buzz/llm-gamebook/commit/bcc16dae54140bbe3bf504c802d7122baaf03344))

- **backend**: Fix `EngineManager` tests
  ([`e9affea`](https://github.com/buzz/llm-gamebook/commit/e9affeafa776e3c6f0e0ebc41d2e64eba97363e7))

- **backend**: Project image
  ([`3322fe2`](https://github.com/buzz/llm-gamebook/commit/3322fe2d642512edb300245bd2bf0aa15f154ddd))

- **backend**: Rename `test_story_engine.py` -> `test_runner.py`, consolidate fixtures
  ([`6edf100`](https://github.com/buzz/llm-gamebook/commit/6edf1008b85895449b188a4bc97868604d69ecef))

- **backend**: Test complete Broken Bulb story flow using mock model
  ([`7dbbeed`](https://github.com/buzz/llm-gamebook/commit/7dbbeed476a357be4858f6497a43155482d167cb))

- **backend**: Update session tests for message count and project filtering
  ([`0067e28`](https://github.com/buzz/llm-gamebook/commit/0067e28a5773e10131fbbbfc8d15b8730a756937))


## v0.2.0 (2025-10-23)

### Chores

- Move Python code to `backend` folder
  ([`c25b47d`](https://github.com/buzz/llm-gamebook/commit/c25b47d83dc86137441283f534ce886c0b0cc09d))

- Prevent vscode from sorting imports
  ([`754d5e2`](https://github.com/buzz/llm-gamebook/commit/754d5e290496e37ab152e3fb889bf76f5cbe01f4))

- **frontend**: Minor renamings and refactoring
  ([`28e5ec5`](https://github.com/buzz/llm-gamebook/commit/28e5ec5c41e72cfe42b8b6f8d40a1ecf086314b4))

### Documentation

- Update todos
  ([`87a41b5`](https://github.com/buzz/llm-gamebook/commit/87a41b5c6dbf388733c38c3b57a2f3b8c3ac4939))

### Features

- **backend**: Add basic websocket endpoint
  ([`a76bff4`](https://github.com/buzz/llm-gamebook/commit/a76bff42d90984ec907fa095f7b45cc8f16cffcc))

- **backend**: Add delete chat route
  ([`56b06ff`](https://github.com/buzz/llm-gamebook/commit/56b06ff2902e952120e3c32fc0c65b6305be6963))

- **backend**: Add FastAPI, SQLModel
  ([`a076e16`](https://github.com/buzz/llm-gamebook/commit/a076e169beeb84bf123bcd15e9e48dc7d238512e))

- **backend**: Redesign DB models to be closer to Pydantic AI data stuctures
  ([`4e56ab0`](https://github.com/buzz/llm-gamebook/commit/4e56ab02e96b5ac56d5f0b081521bed10921d59b))

- **backend**: Use sync sqlite driver, add `EngineManager`
  ([`3b1531d`](https://github.com/buzz/llm-gamebook/commit/3b1531da4761b030f0822e7b7956a629db5c06ea))

- **frontend**: Add frontend project scaffold
  ([`9bb5c2c`](https://github.com/buzz/llm-gamebook/commit/9bb5c2c0607607bb20e511c0bbc67339a2fb9284))

- **frontend**: Add Redux Toolkit
  ([`105b2ac`](https://github.com/buzz/llm-gamebook/commit/105b2ac9982159161625a3c13c0de6d83f5309f2))

- **frontend**: Add wouter
  ([`345ea15`](https://github.com/buzz/llm-gamebook/commit/345ea153035295ec53297636d1a009b8a1b8dfd0))

- **frontend**: Generate types from OpenAPI
  ([`f39e532`](https://github.com/buzz/llm-gamebook/commit/f39e5328fdd86f6f3720df88df53e534340973de))

- **frontend**: Message streaming
  ([`8eeb030`](https://github.com/buzz/llm-gamebook/commit/8eeb030f4defef2ccc85bc29a8752ae46ed4c525))


## v0.1.0 (2025-10-23)

### Chores

- Add LICENSE.txt
  ([`ee31f8f`](https://github.com/buzz/llm-gamebook/commit/ee31f8f1cfb35023e610c5d82e01f1a3f4c3c09c))

- Add log files to `.gitignore`
  ([`1beccd2`](https://github.com/buzz/llm-gamebook/commit/1beccd2332eb3abc00740a5a6ac25e3890a62c89))

- Add python-semantic-release
  ([`0cc03bc`](https://github.com/buzz/llm-gamebook/commit/0cc03bc5915dab6bbfd39b917e2d5dd40810a8be))

- Fix type errors
  ([`cb72c0d`](https://github.com/buzz/llm-gamebook/commit/cb72c0d2f7220251812bd2cbf48857b4368337c0))

- Migrate to pydantic-ai
  ([`da62387`](https://github.com/buzz/llm-gamebook/commit/da62387b506d6fba8d5b1e5ef27d0a6013ac3805))

- Organize imports on save in vscode
  ([`e4af0f3`](https://github.com/buzz/llm-gamebook/commit/e4af0f34efb7d585e0181e77738379371153fb59))

- Update info.md
  ([`6bfa7ac`](https://github.com/buzz/llm-gamebook/commit/6bfa7aca249136da9dd9e1206202a06a80fbe74b))

- Upgrade Python packages
  ([`12207fd`](https://github.com/buzz/llm-gamebook/commit/12207fd93ee3af5e84ab0b971ba26ec4012be487))

- Use `pydantic_ai.models.openai.OpenAIChatModel` over deprecated `OpenAIModel`
  ([`7c19e0e`](https://github.com/buzz/llm-gamebook/commit/7c19e0e7ef0f323943457b7775126f37f256244a))

### Documentation

- Add `todos.md`, add projectaon.org link
  ([`8cd9fe0`](https://github.com/buzz/llm-gamebook/commit/8cd9fe02ab200c345e3212a85968c6a5c944397c))

- Add preliminary `README.md` and `architecture.md`
  ([`2bee8fb`](https://github.com/buzz/llm-gamebook/commit/2bee8fb08958a89c6d50e53c7206bfc4775523ec))

- Extend `architecture.md`
  ([`17d1a30`](https://github.com/buzz/llm-gamebook/commit/17d1a30dc5eb61c1ffa08b81b93cc4faa7faa1a3))

### Features

- Add `TextUserInterface`
  ([`9fd9ea8`](https://github.com/buzz/llm-gamebook/commit/9fd9ea89e43891ca8569d18e79392cda950bd11f))

- Add conditions
  ([`eccbda4`](https://github.com/buzz/llm-gamebook/commit/eccbda42e56604c1d7b7f716ae10463e7e0d7c0e))

- Add jinja2 for system prompt templating
  ([`4a27b53`](https://github.com/buzz/llm-gamebook/commit/4a27b53c2ffb0b9b61005a8c86f7813fcb6c0b7e))

- Add Textual UI
  ([`de68b36`](https://github.com/buzz/llm-gamebook/commit/de68b361ee7705b1c7e98ff2d778edd33ce06d45))

- Add typer argument parsing
  ([`7358d87`](https://github.com/buzz/llm-gamebook/commit/7358d87dac2d4745f1a37b54ce2a0869fd2a8377))

- Allow general declarative function calling
  ([`825882c`](https://github.com/buzz/llm-gamebook/commit/825882c726811ebb73f77720327f8fbcaf9dd361))

- Boolean expression parser/evaluator
  ([`b1114ca`](https://github.com/buzz/llm-gamebook/commit/b1114ca101dc7d4ed35887305fcc5022054d9a57))

- Make model parameters configurable using env vars
  ([`9449a39`](https://github.com/buzz/llm-gamebook/commit/9449a3904d6055239d4c41dd518ae4f60de552d6))

- Multiple story arcs instead of single story line
  ([`7535df0`](https://github.com/buzz/llm-gamebook/commit/7535df0c49984fc9c3a6ff734ec56891a265655c))

- Refined message handling
  ([`84b36c8`](https://github.com/buzz/llm-gamebook/commit/84b36c88836776258dff2b1fd71c39eb94cd7557))

- Support YAML gamebook format
  ([`8cb15a8`](https://github.com/buzz/llm-gamebook/commit/8cb15a848661acf5e7db9cbf32d3bbb9500a1c9a))

### Refactoring

- Add .editorconfig, formatting
  ([`f42e2bd`](https://github.com/buzz/llm-gamebook/commit/f42e2bda06aeb339ea0788eb0cded87d138d613e))

- Game->story, rename some template vars
  ([`8fd13ad`](https://github.com/buzz/llm-gamebook/commit/8fd13ad0b82d37d3738ff57b9060b393eaf59aff))

- Runtime state uses Pydantic models/sub-classes from schema
  ([`2c3f5c6`](https://github.com/buzz/llm-gamebook/commit/2c3f5c62cf5e07e9847d1d8a51f49834799388ea))

- Use snake_case instead of slugs for entities, PascalCase for entity types
  ([`d1042a3`](https://github.com/buzz/llm-gamebook/commit/d1042a3207ca4ffd0f1cd110b1f4b2e0b1d14de2))

### Testing

- Add simple test for YAMLLoader
  ([`7b878dd`](https://github.com/buzz/llm-gamebook/commit/7b878ddb2bae92f38c3a6f47954e94a362ee74b9))


## v0.0.0 (2025-10-14)

- Initial Release
