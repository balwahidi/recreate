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

---

**@fasttime** commented on 2024-12-16:

Thanks for the report @kripod. I can reproduce the problem, we'll have to look into this.

Noting that the false positive also occurs with previous versions of ESLint, so this doesn't seem to be a regression related to #19200.


---

**@aladdin-add** commented on 2024-12-17:

seems a bug to me. and I confirmed that this problem also exists in eslint v9.16.0.

---

**@Tanujkanti4441** commented on 2024-12-19:

seems like a bug to me also.

let's take some other opinions too, @eslint/eslint-team should we consider this?

---

**@fasttime** commented on 2024-12-19:

I also think this is a bug; marking as accepted. The problem is that when a try block contains a `return` or `break` statement, the rule doesn't consider segments in the `catch` block as possible subsequents of the current segment.

In the above example, the statement `return { intermediaryValue }` is not considered a subsequent of `intermediaryValue = 42`, and since there are no other usages of `intermediaryValue`, the rule flags the assignment as useless.

The [code path graph](https://explorer.eslint.org/#eslint-explorer=IntcInN0YXRlXCI6e1widG9vbFwiOlwicGF0aFwiLFwiY29kZVwiOntcImphdmFzY3JpcHRcIjpcImFzeW5jIGZ1bmN0aW9uIGZuKCkge1xcbiAgbGV0IGludGVybWVkaWFyeVZhbHVlO1xcbiAgdHJ5IHtcXG4gICAgaW50ZXJtZWRpYXJ5VmFsdWUgPSA0MjtcXG4gICAgdW5zYWZlRm4oKTtcXG4gICAgcmV0dXJuIHsgZXJyb3I6IHVuZGVmaW5lZCB9O1xcbiAgfSBjYXRjaCB7XFxuICAgIHJldHVybiB7IGludGVybWVkaWFyeVZhbHVlIH07XFxuICB9XFxufVxcblwiLFwianNvblwiOlwiLyoqXFxuICogVHlwZSBvciBwYXN0ZSBzb21lIEpTT04gaGVyZSB0byBsZWFybiBtb3JlIGFib3V0XFxuICogdGhlIHN0YXRpYyBhbmFseXNpcyB0aGF0IEVTTGludCBjYW4gZG8gZm9yIHlvdS5cXG4gKlxcbiAqIFRoZSB0YWJzIGFyZTpcXG4gKlxcbiAqIC0gQVNUIC0gVGhlIEFic3RyYWN0IFN5bnRheCBUcmVlIG9mIHRoZSBjb2RlLCB3aGljaCBjYW5cXG4gKiAgIGJlIHVzZWZ1bCB0byB1bmRlcnN0YW5kIHRoZSBzdHJ1Y3R1cmUgb2YgdGhlIGNvZGUuIFlvdVxcbiAqICAgY2FuIHZpZXcgdGhpcyBzdHJ1Y3R1cmUgYXMgSlNPTiBvciBpbiBhIHRyZWUgZm9ybWF0LlxcbiAqXFxuICogWW91IGNhbiBjaGFuZ2UgdGhlIHdheSB0aGF0IHRoZSBKU09OIGNvZGUgaXMgaW50ZXJwcmV0ZWRcXG4gKiBieSBjbGlja2luZyBcXFwiSlNPTlxcXCIgaW4gdGhlIGhlYWRlciBhbmQgc2VsZWN0aW5nIGRpZmZlcmVudFxcbiAqIG9wdGlvbnMuXFxuICpcXG4gKiBUaGlzIGV4YW1wbGUgaXMgaW4gSlNPTkMgbW9kZSwgd2hpY2ggYWxsb3dzIGNvbW1lbnRzLlxcbiAqL1xcblxcbntcXG4gICAgXFxcImtleTFcXFwiOiBbdHJ1ZSwgZmFsc2UsIG51bGxdLFxcbiAgICBcXFwia2V5MlxcXCI6IHtcXG4gICAgICAgIFxcXCJrZXkzXFxcIjogWzEsIDIsIFxcXCIzXFxcIiwgMWUxMCwgMWUtM11cXG4gICAgfVxcbn1cIixcIm1hcmtkb3duXCI6XCI8IS0tXFxuVHlwZSBvciBwYXN0ZSBzb21lIE1hcmtkb3duIGhlcmUgdG8gbGVhcm4gbW9yZSBhYm91dFxcbnRoZSBzdGF0aWMgYW5hbHlzaXMgdGhhdCBFU0xpbnQgY2FuIGRvIGZvciB5b3UuXFxuXFxuVGhlIHRhYnMgYXJlOlxcblxcbi0gQVNUIC0gVGhlIEFic3RyYWN0IFN5bnRheCBUcmVlIG9mIHRoZSBjb2RlLCB3aGljaCBjYW5cXG5iZSB1c2VmdWwgdG8gdW5kZXJzdGFuZCB0aGUgc3RydWN0dXJlIG9mIHRoZSBjb2RlLiBZb3VcXG5jYW4gdmlldyB0aGlzIHN0cnVjdHVyZSBhcyBKU09OIG9yIGluIGEgdHJlZSBmb3JtYXQuXFxuXFxuWW91IGNhbiBjaGFuZ2UgdGhlIHdheSB0aGF0IHRoZSBNYXJrZG93biBjb2RlIGlzIGludGVycHJldGVkXFxuYnkgY2xpY2tpbmcgXFxcIk1hcmtkb3duXFxcIiBpbiB0aGUgaGVhZGVyIGFuZCBzZWxlY3RpbmcgZGlmZmVyZW50XFxub3B0aW9ucy5cXG5cXG5UaGlzIGV4YW1wbGUgaXMgaW4gQ29tbW9uTWFyayBtb2RlLlxcbi0tPlxcblxcbiMgRVNMaW50IE1hcmtkb3duIEV4YW1wbGVcXG5cXG5UaGlzIGlzIGFuIGV4YW1wbGUgb2YgYSBNYXJrZG93biBmaWxlIHRoYXQgY2FuIGJlIHBhcnNlZFxcbmJ5IEVTTGludC4gTWFya2Rvd24gaXMgYSBzaW1wbGUgbWFya3VwIGxhbmd1YWdlIHRoYXQgaXNcXG5vZnRlbiB1c2VkIGZvciBkb2N1bWVudGF0aW9uLlxcblxcbiMjIEZlYXR1cmVzXFxuXFxuLSBNYWtlIHRoaW5ncyAqaXRhbGljKiwgKipib2xkKiosIG9yIGBjb2RlYFxcbi0gQ3JlYXRlIFtsaW5rc10oaHR0cHM6Ly9lc2xpbnQub3JnKVxcbi0gU3VwcG9ydHMgSFRNTCA8c3BhbiBzdHlsZT1cXFwiY29sb3I6IHJlZDtcXFwiPmVsZW1lbnRzPC9zcGFuPlxcbi0gTGlzdHNcXG4gIC0gTmVzdGVkIGxpc3RzXCIsXCJjc3NcIjpcIi8qKlxcbiAqIFR5cGUgb3IgcGFzdGUgc29tZSBDU1MgaGVyZSB0byBsZWFybiBtb3JlIGFib3V0XFxuICogdGhlIHN0YXRpYyBhbmFseXNpcyB0aGF0IEVTTGludCBjYW4gZG8gZm9yIHlvdS5cXG4gKlxcbiAqIFRoZSB0YWJzIGFyZTpcXG4gKlxcbiAqIC0gQVNUIC0gVGhlIEFic3RyYWN0IFN5bnRheCBUcmVlIG9mIHRoZSBjb2RlLCB3aGljaCBjYW5cXG4gKiAgIGJlIHVzZWZ1bCB0byB1bmRlcnN0YW5kIHRoZSBzdHJ1Y3R1cmUgb2YgdGhlIGNvZGUuIFlvdVxcbiAqICAgY2FuIHZpZXcgdGhpcyBzdHJ1Y3R1cmUgYXMgSlNPTiBvciBpbiBhIHRyZWUgZm9ybWF0LlxcbiAqXFxuICogWW91IGNhbiBjaGFuZ2UgdGhlIHdheSB0aGF0IHRoZSBDU1MgY29kZSBpcyBpbnRlcnByZXRlZFxcbiAqIGJ5IGNsaWNraW5nIFxcXCJDU1NcXFwiIGluIHRoZSBoZWFkZXIgYW5kIHNlbGVjdGluZyBkaWZmZXJlbnRcXG4gKiBvcHRpb25zLlxcbiAqL1xcblxcbkBpbXBvcnQgdXJsKCdodHRwczovL2ZvbnRzLmdvb2dsZWFwaXMuY29tL2NzczI%2FZmFtaWx5PVJvYm90bzp3Z2h0QDQwMDs3MDAmZGlzcGxheT1zd2FwJyk7XFxuXFxuYm9keSB7XFxuXFx0Zm9udC1mYW1pbHk6IHNhbnMtc2VyaWY7XFxufVxcblxcbmgxIHtcXG5cXHRjb2xvcjogIzMzMztcXG59XFxuXFxucCB7XFxuXFx0bWFyZ2luOiAxZW0gMDtcXG59XCJ9LFwibGFuZ3VhZ2VcIjpcImphdmFzY3JpcHRcIixcImpzT3B0aW9uc1wiOntcInBhcnNlclwiOlwiZXNwcmVlXCIsXCJzb3VyY2VUeXBlXCI6XCJtb2R1bGVcIixcImVzVmVyc2lvblwiOlwibGF0ZXN0XCIsXCJpc0pTWFwiOnRydWV9LFwianNvbk9wdGlvbnNcIjp7XCJqc29uTW9kZVwiOlwianNvbmNcIn0sXCJjc3NPcHRpb25zXCI6e1wiY3NzTW9kZVwiOlwiY3NzXCJ9LFwibWFya2Rvd25PcHRpb25zXCI6e1wibWFya2Rvd25Nb2RlXCI6XCJjb21tb25tYXJrXCJ9LFwid3JhcFwiOnRydWUsXCJ2aWV3TW9kZXNcIjp7XCJhc3RWaWV3XCI6XCJ0cmVlXCIsXCJzY29wZVZpZXdcIjpcImZsYXRcIixcInBhdGhWaWV3XCI6XCJncmFwaFwifSxcInBhdGhJbmRleFwiOntcImluZGV4XCI6MSxcImluZGV4ZXNcIjoyfX0sXCJ2ZXJzaW9uXCI6MH0i) shows no reachable connection from the `Literal (42)` segment to `CatchClause:enter`, but that doesn't mean that execution couldn't jump from the try block into the catch block if an error occurs. This is a peculiarity of code path analysis that the rule doesn't currently account for.

---

**@Tanujkanti4441** commented on 2024-12-22:

I'll take this.

---

**@nzakas** commented on 2024-12-30:

Note: The code path analysis makes some performance tradeoffs when dealing with `try-catch` statements, as any expression in the `try` block could potentially branch to the `catch` block, and creating all of those links would take up a lot of memory.

---

**@nzakas** commented on 2025-01-29:

@Tanujkanti4441 are you still working on this?

---

**@Tanujkanti4441** commented on 2025-01-30:

> [@Tanujkanti4441](https://github.com/Tanujkanti4441) are you still working on this?

Sorry! didn't get enough time this issue requires, its better to remove the assignment for now in case if anyone want to take this.
