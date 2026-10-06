# Bug: `no-lonely-if` has incorrect fix when nested inside parent `if` without `BlockStatement`

Reported by @abrahamguo on 2024-10-18

### Environment

Local ESLint version: 9.12.0


### What parser are you using?

Default (Espree)

### What did you do?

```js
/* eslint no-lonely-if: "error" */
if (true)
	if (false) {}
	else { if (false) {} }
	//     ^ Unexpected if as the only statement in an else block.
else throw Error('This `else` should have been unreachable!');
```


### What did you expect to happen?

Autofix should not be unsafe.

Should it maybe autofix by adding curly braces to the outer `if`? Not sure.

### What actually happened?

```js
/* eslint no-lonely-if: "error" */
if (true)
	if (false) {}
	else if (false) {}
else throw Error('This `else` should have been unreachable!');
```

The `else` block is now reachable when it used to be unreachable.

### Link to Minimal Reproducible Example

https://eslint.org/play/#eyJ0ZXh0IjoiLyogZXNsaW50IG5vLWxvbmVseS1pZjogXCJlcnJvclwiICovXG5pZiAodHJ1ZSlcblx0aWYgKGZhbHNlKSB7fVxuXHRlbHNlIHsgaWYgKGZhbHNlKSB7fSB9XG5lbHNlIHRocm93IEVycm9yKCdUaGlzIGBlbHNlYCBzaG91bGQgaGF2ZSBiZWVuIHVucmVhY2hhYmxlIScpOyIsIm9wdGlvbnMiOnsicnVsZXMiOnt9LCJsYW5ndWFnZU9wdGlvbnMiOnsicGFyc2VyT3B0aW9ucyI6eyJlY21hRmVhdHVyZXMiOnt9fX19fQ==

### Participation

- [x] I am willing to submit a pull request for this issue.

### Additional comments

FYI, this case is already handled correctly by the `curly` rule:

```js
/* eslint curly: ["error", "multi"] */
if (true) {
	//^ Unnecessary { after 'if' condition.
	if (false) {}
	else { if (false) {} }
	//   ^ Unnecessary { after 'else'
}
else throw Error('This `else` should have been unreachable!');
```

Two errors are reported by the `curly` rule, but autofixing either one results in the other error no longer being reported.

https://eslint.org/play/#eyJ0ZXh0IjoiLyogZXNsaW50IGN1cmx5OiBbXCJlcnJvclwiLCBcIm11bHRpXCJdICovXG5pZiAodHJ1ZSkge1xuXHRpZiAoZmFsc2UpIHt9XG5cdGVsc2UgeyBpZiAoZmFsc2UpIHt9IH1cbn1cbmVsc2UgdGhyb3cgRXJyb3IoJ1RoaXMgYGVsc2VgIHNob3VsZCBoYXZlIGJlZW4gdW5yZWFjaGFibGUhJyk7Iiwib3B0aW9ucyI6eyJydWxlcyI6e30sImxhbmd1YWdlT3B0aW9ucyI6eyJwYXJzZXJPcHRpb25zIjp7ImVjbWFGZWF0dXJlcyI6e319fX19
