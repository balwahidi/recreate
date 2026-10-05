# Bug: [no-var] Fix causes ReferenceError

Reported by @mikko-ahlroth-vincit on 2025-10-13

### Environment

ESLint Playground (eslint version v9.37.0).

Also locally tested on eslint v8.57.1 with similar change of `var` to `let` without moving its location (tested on a more complicated setup though, not this minimised example).

### What parser are you using?

Default (Espree)

### What did you do?

### Playground Code
```js
export function a() {
    console.log(o);
    var o;
    return o;
}
```

### ESLint Configuration 
<details> 
 <summary> Tap to see full config </summary> 

```js
undefined
export default [
    {
        "rules": {
            "no-var": [
                "error"
            ]
        }
    }
];
```
 </details>

### ESLint Output
```
3:5 Unexpected var, use let or const instead. (no-var)
```

Now press "Fix".


### What did you expect to happen?

```js
export function a() {
    let o;
    console.log(o);
    return o;
}
```

### What actually happened?

```js
export function a() {
    console.log(o);
    let o;
    return o;
}
```

This code leads to a ReferenceError as the `let` is not moved above the usage point of `o`.

### Link to Minimal Reproducible Example

https://eslint.org/play/#eyJ0ZXh0IjoiZXhwb3J0IGZ1bmN0aW9uIGEoKSB7XG4gICAgY29uc29sZS5sb2cobyk7XG4gICAgdmFyIG87XG4gICAgcmV0dXJuIG87XG59Iiwib3B0aW9ucyI6eyJydWxlcyI6eyJuby12YXIiOlsiZXJyb3IiXX0sImxhbmd1YWdlT3B0aW9ucyI6eyJwYXJzZXJPcHRpb25zIjp7ImVjbWFGZWF0dXJlcyI6e319fX19

### Participation

- [ ] I am willing to submit a pull request for this issue.

### Additional comments

Similar old closed issue: https://github.com/eslint/eslint/issues/7950
