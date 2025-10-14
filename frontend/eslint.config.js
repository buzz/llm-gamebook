import js from '@eslint/js'
import pluginImport from 'eslint-plugin-import'
import pluginPrettierRecommended from 'eslint-plugin-prettier/recommended'
import pluginReactDom from 'eslint-plugin-react-dom'
import pluginReactHooks from 'eslint-plugin-react-hooks'
import pluginReactRefresh from 'eslint-plugin-react-refresh'
import pluginReactX from 'eslint-plugin-react-x'
import pluginSimpleImportSort from 'eslint-plugin-simple-import-sort'
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import tseslint from 'typescript-eslint'

const importRules = {
  // TypeScript provides the same checks
  // https://typescript-eslint.io/linting/troubleshooting/performance-troubleshooting#eslint-plugin-import
  'import/named': 'off',
  'import/namespace': 'off',
  'import/default': 'off',
  'import/no-named-as-default-member': 'off',

  // Import order setup
  'import/first': 'error',
  'import/newline-after-import': 'error',
  'import/no-duplicates': 'error',
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

  // Turn on errors for missing imports
  'import/no-unresolved': 'error',
}

export default defineConfig([
  globalIgnores(['dist']),
  pluginPrettierRecommended,
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      pluginReactX.configs['recommended-typescript'],
      pluginReactDom.configs.recommended,
      pluginReactHooks.configs['recommended-latest'],
      pluginReactRefresh.configs.vite,
      pluginImport.flatConfigs.recommended,
      pluginImport.flatConfigs.typescript,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      'simple-import-sort': pluginSimpleImportSort,
    },
    rules: {
      ...importRules,
    },
  },
])
