module.exports = {
  parserOptions: {
    sourceType: 'module'
  },
  extends: ['plugin:vue/essential'],
  plugins: ['prettier', 'html'],
  ignorePatterns: ['node_modules/**', '**/static/**'],
  rules: {
    indent: 'off',
    'prettier/prettier': 'error',
    'space-before-function-paren': [
      'error',
      {
        anonymous: 'always',
        named: 'never',
        asyncArrow: 'always'
      }
    ]
  }
}
