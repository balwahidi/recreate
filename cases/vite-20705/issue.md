# devserver serves source files instead of index.html since v7.0.5

Reported by @schiller-manuel on 2025-08-31

### Describe the bug

Since version 7.0.5, vite devserver serves source files instead of index.html when the url path matches the basename of a file inside the project.

originally reported here: https://github.com/TanStack/router/issues/5052

### Reproduction

https://stackblitz.com/edit/vitejs-vite-sfcqpwnb

### Steps to reproduce

1. go to https://stackblitz.com/edit/vitejs-vite-sfcqpwnb
2. click on "open preview in new tab"
3. click on "click me" that opens the dev server at `/test`
4. you will see the contents of `test.js` served from `/test`

here is the same project with vite 7.0.4 that works as expected:
https://stackblitz.com/edit/vitejs-vite-tgbe56vv

### System Info

```shell
starts happening since vite 7.0.5
```

### Used Package Manager

npm

### Logs

_No response_

### Validations

- [x] Follow our [Code of Conduct](https://github.com/vitejs/vite/blob/main/CODE_OF_CONDUCT.md)
- [x] Read the [Contributing Guidelines](https://github.com/vitejs/vite/blob/main/CONTRIBUTING.md).
- [x] Read the [docs](https://vite.dev/guide).
- [x] Check that there isn't [already an issue](https://github.com/vitejs/vite/issues) that reports the same bug to avoid creating a duplicate.
- [x] Make sure this is a Vite issue and not a framework-specific issue. For example, if it's a Vue SFC related bug, it should likely be reported to [vuejs/core](https://github.com/vuejs/core) instead.
- [x] Check that this is a concrete bug. For Q&A open a [GitHub Discussion](https://github.com/vitejs/vite/discussions) or join our [Discord Chat Server](https://chat.vite.dev/).
- [x] The provided reproduction is a [minimal reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) of the bug.
