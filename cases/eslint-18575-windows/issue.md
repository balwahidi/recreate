# Bug: files on a different drive are not ignored on Windows

Reported by @fasttime on 2024-06-09

### Environment

Node version: v20.14.0
npm version: v10.7.0
Local ESLint version: v9.4.0 (Currently used)
Global ESLint version: Not found
Operating System: win32 10.0.22631

### What parser are you using?

Default (Espree)

### What did you do?

On Windows, I tried to lint a file on a different drive than the working directory, and surprisingly, ESLint did not ignore that file.

---

Created a file **F:\foo.js**:

```js
foo();
```

Then in the PowerShell, from a directory on drive C:, run:

```shell
npx eslint --no-config-lookup F:\foo.js
```


### What did you expect to happen?

An warning message should be printed saying that file F:\foo.js is ignored.

### What actually happened?

The file was linted.

```console
C:\Project>npx eslint --no-config-lookup --rule "no-undef: error" F:\foo.js

F:\foo.js
  1:1  error  'foo' is not defined  no-undef

✖ 1 problem (1 error, 0 warnings)
```

### Link to Minimal Reproducible Example

https://github.com/fasttime/ESLint-Repro/actions/runs/9431260399/job/25979730143

### Participation

- [X] I am willing to submit a pull request for this issue.

### Additional comments

The `Linter` class is also affected. For instance:

```js
// C:\test.mjs
import { Linter } from "eslint";

const linter = new Linter({ configType: "flat" });
const results = linter.verify("foo()", { rules: { "no-undef": "error" } }, "F:\\foo.js");

console.log(results);
```

Running the above code with `node test.mjs` prints:

```console
[
  {
    ruleId: 'no-undef',
    severity: 2,
    message: "'foo' is not defined.",
    line: 1,
    column: 1,
    nodeType: 'Identifier',
    messageId: 'undef',
    endLine: 1,
    endColumn: 4
  }
]
```
