# `no-unused-expressions` started to trigger on `'use strict'` in 9.25.0

Reported by @zloirock on 2025-04-18

### Environment

Node version: 23.10.0
npm version: 11.3.0
Local ESLint version: 9.25.0
Global ESLint version: -
Operating System: MacOS 15.5 Beta


### What parser are you using?

Default (Espree)

### What did you do?

`no-unused-expressions` started to trigger on `'use strict'` in 9.25.0

### What did you expect to happen?

No errors.

### What actually happened?

<img width="752" alt="Image" src="https://github.com/user-attachments/assets/36e5110d-a22d-4522-b7ba-7f55e959b8ef" />

### Additional comments

You could check it on `core-js` repo.

Config: https://github.com/zloirock/core-js/blob/master/tests/eslint/eslint.config.js
`package.json`: https://github.com/zloirock/core-js/blob/master/tests/eslint/package.json

`npm run lint` in the root.
