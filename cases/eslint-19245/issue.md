# Bug: no-useless-assignment false positive in try-catch block

Reported by @kripod on 2024-12-15

### Environment

Node version: v22.11.0
npm version: v10.9.0
Local ESLint version: v9.17.0 (Currently used)
Global ESLint version: Not found
Operating System: darwin 24.1.0


### What parser are you using?

@typescript-eslint/parser

### What did you do?

<details>
<summary>Configuration</summary>

```
// eslint.config.js
export default [
  {
    rules: {
      "no-useless-assignment": "warn"
    },
  },
];
```
</details>

```js
async function fn() {
  let intermediaryValue;
  try {
    intermediaryValue = 42;
    unsafeFn();
    return { error: undefined };
  } catch {
    return { intermediaryValue };
  }
}

function unsafeFn() {
  throw new Error();
}
```


### What did you expect to happen?

The `intermediaryValue = 42` statement shouldn’t be flagged by the 'no-useless-assignment' rule, as it’s being used in the `catch` block.

### What actually happened?

`intermediaryValue = 42` was flagged as ‘not used in subsequent statements’ by mistake.

### Link to Minimal Reproducible Example

https://eslint.org/play/#eyJ0ZXh0IjoiLyplc2xpbnQgbm8tdXNlbGVzcy1hc3NpZ25tZW50OiBcIndhcm5cIiAqL1xuXG5hc3luYyBmdW5jdGlvbiBmbigpIHtcbiAgbGV0IGludGVybWVkaWFyeVZhbHVlO1xuICB0cnkge1xuICAgIGludGVybWVkaWFyeVZhbHVlID0gNDI7XG4gICAgdW5zYWZlRm4oKTtcbiAgICByZXR1cm4geyBlcnJvcjogdW5kZWZpbmVkIH07XG4gIH0gY2F0Y2gge1xuICAgIHJldHVybiB7IGludGVybWVkaWFyeVZhbHVlIH07XG4gIH1cbn1cblxuZnVuY3Rpb24gdW5zYWZlRm4oKSB7XG4gIHRocm93IG5ldyBFcnJvcigpO1xufVxuIiwib3B0aW9ucyI6eyJydWxlcyI6e30sImxhbmd1YWdlT3B0aW9ucyI6eyJzb3VyY2VUeXBlIjoibW9kdWxlIiwicGFyc2VyT3B0aW9ucyI6eyJlY21hRmVhdHVyZXMiOnt9fX19fQ==

### Participation

- [ ] I am willing to submit a pull request for this issue.

### Additional comments

_No response_
