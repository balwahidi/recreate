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

---

**@Andarist** commented on 2024-11-24:

This ia **display-only** bug introduced by https://github.com/microsoft/TypeScript/pull/59282 . For type printing purposes it reuses here the assertion type but it misses the fact that this type can be processed by the template of a mapped type.

How do we know it's just a display-only bug? Just inspect this:
```ts
type Test2 = Unwrap<typeof value>["prop1"]
//       ^? type Test2 = "hello"
```

---

**@denk0403** commented on 2024-11-24:

You're right that my minimal reproduction is a display-only bug. But in a larger codebase, I am seeing a very similar example break type-inference and checking for a Zod schema. What's weirder is that the larger example displays correctly in my IDE, but only errors when running `tsc`.

I will try to refine my reproduction above to see if I can produce the type-checking regression.

---

**@Andarist** commented on 2024-11-24:

It would be appreciated because it should be a completely different bug. Fixing this display-only bug is just very unlikely to fix what you are describing above.
