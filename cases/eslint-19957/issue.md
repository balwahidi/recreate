# Bug: no-loss-of-precision rule incorrectly flags 9.000e+3

Reported by @Noah-Martinez on 2025-07-21

### Environment

Node version: v22.16.0
npm version: v11.4.1
Local ESLint version: v9.28.0 (Currently used)
Global ESLint version: Not found
Operating System: win32 10.0.26100


### What parser are you using?

Default (Espree)

### What did you do?

<details>
<summary>Configuration</summary>

```js
import eslint from "@eslint/js";
import stylisticPlugin from '@stylistic/eslint-plugin';
import angularEslint from "angular-eslint";
import { defineConfig } from "eslint/config";
import tsEslint from "typescript-eslint";

const stylisticRecommendedWarn = errorToWarn(stylisticPlugin.configs.recommended);

export default defineConfig([
  {
    files: ["**/*.ts"],
    ignores: [
      "**/node_modules",
      "**/dist",
      "**/documentation/compodoc",
    ],
    processor: angularEslint.processInlineTemplates,
    extends: [
      eslint.configs.recommended,
      // stylisticPlugin.configs.recommended,
      stylisticRecommendedWarn,
      ...tsEslint.configs.recommended,
      ...tsEslint.configs.stylistic,
      ...angularEslint.configs.tsRecommended,
    ],
    plugins: {
      "@stylistic": stylisticPlugin,
      "@typescript-eslint": tsEslint.plugin,
      "@angular-eslint": angularEslint.tsPlugin,
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          "argsIgnorePattern": "^_",
          "caughtErrorsIgnorePattern": "^_",
        }
      ],

      // angular config:
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "rt",
          style: "camelCase",
        },
      ],
      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "rt",
          style: "kebab-case",
        },
      ],
      "@angular-eslint/no-input-rename": "off",

      // style config:
      "@stylistic/member-delimiter-style": [
        "warn",
        {
          multiline: {
            delimiter: "semi",
            requireLast: true
          },
          singleline: {
            delimiter: "semi",
            requireLast: true
          },
        }
      ],
      "@stylistic/semi": ["error", "always"],
      "@typescript-eslint/no-inferrable-types": "warn",
      "@stylistic/no-extra-semi": "warn",
      "@stylistic/semi-spacing": "warn",
    },
  },
  {
    files: ["**/*.html"],
    ignores: [
      "**/node_modules",
      "**/dist",
      "**/documentation/compodoc",
    ],
    extends: [
      ...angularEslint.configs.templateRecommended,
      ...angularEslint.configs.templateAccessibility,
    ],
    rules: {},
  }
]);

function errorToWarn(config) {
  const errorRegex = /['"](error)['"]/gi;

  const configRulesText = JSON.stringify(config.rules);
  if (!errorRegex.test(configRulesText)) {
    return config;
  }

  const configRulesWarn = JSON.parse(configRulesText.replaceAll(errorRegex, `"warn"`));

  return {
    ...config,
    rules: configRulesWarn,
  };
}

```
</details>

```js
const test = 9.000e+3 // 9000
```

[ESLint Playground reproduction](https://eslint.org/play/#eyJ0ZXh0IjoiLyplc2xpbnQgbm8tbG9zcy1vZi1wcmVjaXNpb246IFwiZXJyb3JcIiovXG5cbi8vIHJlcG9ydGVkIGlzc3VlOlxuY29uc3QgdGVzdCA9IDkuMDAwZSszIC8vIDkwMDAiLCJvcHRpb25zIjp7InJ1bGVzIjp7fSwibGFuZ3VhZ2VPcHRpb25zIjp7InBhcnNlck9wdGlvbnMiOnsiZWNtYUZlYXR1cmVzIjp7fX19fX0=)


### What did you expect to happen?

I expected it to be a valid value (9000).

### What actually happened?

9.000e+3 got marked with the error no-loss-of-precision.

### Link to Minimal Reproducible Example

https://eslint.org/play/#eyJ0ZXh0IjoiLyplc2xpbnQgbm8tbG9zcy1vZi1wcmVjaXNpb246IFwiZXJyb3JcIiovXG5cbi8vIHJlcG9ydGVkIGlzc3VlOlxuY29uc3QgdGVzdCA9IDkuMDAwZSszIC8vIDkwMDAiLCJvcHRpb25zIjp7InJ1bGVzIjp7fSwibGFuZ3VhZ2VPcHRpb25zIjp7InBhcnNlck9wdGlvbnMiOnsiZWNtYUZlYXR1cmVzIjp7fX19fX0=

### Participation

- [ ] I am willing to submit a pull request for this issue.

### Additional comments

_No response_

---

**@snitin315** commented on 2025-07-24:

Looks like a bug to me. marking as accepted. [Playground Link](https://eslint.org/play/#eyJ0ZXh0IjoiLyplc2xpbnQgbm8tbG9zcy1vZi1wcmVjaXNpb246IFwiZXJyb3JcIiovXG5cbmNvbnN0IGZvbyA9IDkuMDAwZTMgLy8gZXJyb3JcbmNvbnN0IHRlc3QgPSA5LjAwMDBlNCAvLyBlcnJvclxuY29uc3QgYmFyID0gOS4wMDBlNCAvLyBva1xuY29uc3QgYmF6ID0gOS4wMDAwZTUgLy8gb2tcbiIsIm9wdGlvbnMiOnsicnVsZXMiOnt9LCJsYW5ndWFnZU9wdGlvbnMiOnsicGFyc2VyT3B0aW9ucyI6eyJlY21hRmVhdHVyZXMiOnt9fX19fQ==)

```js
/*eslint no-loss-of-precision: "error"*/

const foo = 9.000e3 // error
const test = 9.0000e4 // error
const bar = 9.000e4 // ok
const baz = 9.0000e5 // ok

```


---

**@SwetaTanwar** commented on 2025-07-24:

I'll work on a fix

---

**@crimsonjay0** commented on 2025-07-24:

@SwetaTanwar Wow, that was instant! @snitin315 Y’all coordinating this?

---

**@SwetaTanwar** commented on 2025-07-24:

@lordrovo Haha 😄 You just gotta be quick to grab the issues. Try turning on notifications — you’ll be instant too!

---

**@Gautam-Arora24** commented on 2025-08-04:

@SwetaTanwar Are you still working on this issue? If not, I can pick it up.

---

**@SwetaTanwar** commented on 2025-08-04:

> @SwetaTanwar Are you still working on this issue? If not, I can pick it up.

Yes, will be raising PR this weekend
