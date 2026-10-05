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

---

**@hi-ogawa** commented on 2025-09-08:

The change is due to https://github.com/vitejs/vite/pull/20376. Technically the behavior became more consistent since `curl http://localhost:5173/test` has been always serving `test.js`. I'm not sure if there's a workaround on user land. If this breakage is worse than original bug https://github.com/vitejs/vite/issues/17340, then maybe reverting might be an option. @sapphi-red What do you think?

---

**@sapphi-red** commented on 2025-09-10:

I think we need to add back this part and add a bit more code, otherwise I guess `/test` will serve `/test.js` when accessing the second time (I could be misremembering).
https://github.com/vitejs/vite/pull/20376/files#diff-5ac5675edd621a639999ba602b8795d985ca4bc7c9098473e6692d04e34291d9L273-L277
The changes I guess we need are:
- add `Vary: Accept`
- make `cachedTransformMiddleware` to handle `Accept: text/html`
- (optional) I guess we should use `Sec-Fetch-Dest: document`/`Sec-Fetch-Dest: frame`/`Sec-Fetch-Dest: iframe` instead of `Accept: text/html`


---

**@pi0** commented on 2025-09-25:

Facing the same limit with the Nitro Vite plugin + SSR rendering, conflicting with root files.

Added a temporary workaround: https://github.com/nitrojs/nitro/pull/3592/commits/f7d32d942e21414aa71ef370230505c6d620c5fb
