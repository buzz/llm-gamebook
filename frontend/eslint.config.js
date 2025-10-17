import js from '@eslint/js'
import tsParser from '@typescript-eslint/parser'
import importX from 'eslint-plugin-import-x'
import prettierRecommended from 'eslint-plugin-prettier/recommended'
import reactDom from 'eslint-plugin-react-dom'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import reactX from 'eslint-plugin-react-x'
import simpleImportSort from 'eslint-plugin-simple-import-sort'
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import tseslint from 'typescript-eslint'

const importRules = {
  // TypeScript provides the same checks
  // https://typescript-eslint.io/troubleshooting/typed-linting/performance#eslint-plugin-import
  'import-x/named': 'off',
  'import-x/namespace': 'off',
  'import-x/default': 'off',
  'import-x/no-named-as-default-member': 'off',

  'import-x/first': 'error',
  'import-x/newline-after-import': 'error',
  'import-x/no-duplicates': 'error',
  'import-x/no-unresolved': 'error',
  'import-x/exports-last': 'error',
  'import-x/newline-after-import': 'error',

  'simple-import-sort/imports': [
    'error',
    {
      // custom groups with type imports last in each group
      // https://github.com/lydell/eslint-plugin-simple-import-sort#custom-grouping
      groups: [
        ['^\\u0000'], // side-effects
        ['^node:', '^node:.*\\u0000$'], // node modules
        ['^@?\\w', '^@?\\w.*\\u0000$'], // 3rd party imports
        ['^#\\/', '^#\\/.*\\u0000$'], // internal paths
        ['(?<!\\u0000)$', '(?<=\\u0000)$'], // absolute imports
        ['^\\.', '^\\..*\\u0000$'], // relative imports
      ],
    },
  ],
  'simple-import-sort/exports': 'error',
}

const reactRefreshRules = {
  // https://reactrouter.com/explanation/hot-module-replacement#supported-exports
  'react-refresh/only-export-components': [
    'warn',
    {
      allowExportNames: [
        'loader',
        'clientLoader',
        'action',
        'clientAction',
        'ErrorBoundary',
        'HydrateFallback',
        'headers',
        'handle',
        'links',
        'meta',
        'shouldRevalidate',
      ],
    },
  ],
}

export default defineConfig([
  globalIgnores(['dist']),
  prettierRecommended,
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactX.configs['recommended-typescript'],
      reactDom.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
      importX.flatConfigs.recommended,
      importX.flatConfigs.typescript,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parser: tsParser,
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      'import-x': importX,
      'simple-import-sort': simpleImportSort,
    },
    rules: {
      ...importRules,
      ...reactRefreshRules,
    },
  },
])
