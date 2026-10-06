# Synchronous watchers can fail to fire

Reported by @maxbogue on 2024-10-29

### Vue version

3.5.12

### Link to minimal reproduction

https://play.vuejs.org/#eNp9UctOwzAQ/JWVL2mlKhGCU0kjHuoBDoCAoy8h3TRpHduy121RlH/HcZpSJNTb7s7Membdsnut451DNmepLUytCSyS0xmXdaOVIWhhn1NRQQelUQ1EnhzdnqEGyz8Yl1wWSlqCXS4cwqJnTMpcWJxyGXZNuIQBnfXVZAqLDNq+PI7jURpkPdAFZgulcLaaQ2S/ZRFBx6XfmSaDc+/ZN4SNFjmh7wDS6ipr26OTrksT34f5lyNSEu4KURfbBWfjg2QccpYRWkqTgeQFaXK2lc0YWZ+wrNfxxirpTxe8c1aoRtcCzaum2l+As/mYirNcCLV/DrP+jRAnaCostv/MN/bQzzh7M2jR7LyrE0a5WSMN8PLjBQ++PoGNWjnh2RfAd7RKuN7jQHtwcuVtn/GC26fwxbVcf9rlgVDaMVQ40ulT/PEcPl6I/mv3Or4JOi471v0AsRDTXw==

### Steps to reproduce

Click the "test" button. The value stays false because the watcher runs. Click the "test" button again and the value changes to true because the watcher does not run.

### What is expected?

The watcher should run every time the value changes.

### What is actually happening?

The watcher seems to remember the value as being "true" when the value is set to "false" within its watch callback.

### System Info

_No response_

### Any additional comments?

Finally upgrading to Vue 3 and this behavior change caused a bug. In our usage, the watch callback is an edge trigger only when the value switches from true to false in some circumstances, so the watch function being called within itself was expected and handled correctly. I'm guessing this is some known trade-off for a performance optimization but wanted to call it out just in case.

The [docs](https://vuejs.org/guide/essentials/watchers.html#sync-watchers) contain this warning:

> Sync watchers do not have batching and triggers every time a reactive mutation is detected. It's ok to use them to watch simple boolean values, but avoid using them on data sources that might be synchronously mutated many times, e.g. arrays.

But that doesn't mention anything about cases where the watcher could fail to fire on a valid change.

---

**@maxbogue** commented on 2024-10-29:

A co-worker of mine discovered that it behaves correctly with `shallowRef` in place of `ref`. That surprises me since I didn't think those would behave differently for primitives, but it's also unhelpful as the boolean I'm working with in real code is the result of a `computed`.

---

**@edison1105** commented on 2024-10-30:

The reproduction link failed to load.

---

**@maxbogue** commented on 2024-10-30:

Sorry about that; I've fixed the link.
