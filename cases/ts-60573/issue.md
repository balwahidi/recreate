# Type assertion regression in TypeScript 5.7

Reported by @denk0403 on 2024-11-23

### 🔎 Search Terms

"typescript 5.7", "type assertions", "casting", "regression", "zod", "tsc"

### 🕗 Version & Regression Information

- This changed between versions 5.6.3 and 5.7.2


### ⏯ Playground Link

https://www.typescriptlang.org/play/?ts=5.7.2#code/C4TwDgpgBA6gTgQzJOAeAKgPigXigbwCgoSoB9USALinUIF9DCAzAVwDsBjYASwHt2UAM7A4PdgHN4SFAAoAlDWnIIaEWMnYipKHAjBWcQfnKUINAEQWojRiw7d+gvgCMAVspQYoEAB7AIdgATISgAJQhOPjgg1HVxCQAaWEQVNAR2EExs2Vc3GnRFFJlVDC1iUj0DIwJTcHMoPJsGJij2ESgANwQAG1ZoPDzPVVltUjA4PjAARhp4yWG4BSgEUMXUCwALCB6evgtMBnkmMygAVXYAd1TvPwDgtdSvDKzsPHQAbQByCnqvgF0fP5AiFwpForF5klimlUC9slAKiQAPy1D4AaQgICg4igAGssXxmLRvr9IAD-jQLtckBhSWYARisf9sPREToCvS-v8TvVaBAOnhqTczESur1+ocAPRS0gAPWRQA

### 💻 Code

```ts
type Wrapper<T> = {
    _type: T
}

function stringWrapper(): Wrapper<string> {
    return { _type: "" }
}

function objWrapper<T extends Record<string, Wrapper<any>>>(obj: T): Wrapper<T> {
    return { _type: obj }
}

const value = objWrapper({
    prop1: stringWrapper() as Wrapper<"hello">
})

type Unwrap<T extends Wrapper<any>> = T['_type'] extends Record<string, Wrapper<any>> 
    ? { [Key in keyof T['_type']]: Unwrap<T['_type'][Key]> } 
    : T['_type']

type Test = Unwrap<typeof value>
```


### 🙁 Actual behavior

The type of `Test` is `{ prop1: Wrapper<"hello">; }` in v5.7. 

This is wrong because the `Unwrap` type should recursively extract the underlying type of each `Wrapper`.

### 🙂 Expected behavior

The type of `Test` should be `{ prop1: "hello"; }`, like it is in v5.6.

### Additional information about the issue

This issue seems related to the inline type assertion on line 14. The inference is corrected if the type assertion happens on a separate line, such as:
```ts
const strWrapper = stringWrapper() as Wrapper<"hello">;

const value = objWrapper({
    prop1: strWrapper
});

type Test = Unwrap<typeof value>
//   ^? type Test = { prop1: "hello"; }
```

This is a simplified version of an issue I'm seeing with some [Zod](https://github.com/colinhacks/zod) schemas after upgrading to TypeScript 5.7.
