# CHANGELOG

<!-- version list -->

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
