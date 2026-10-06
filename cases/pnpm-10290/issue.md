# Relative storeDir path in pnpm-workspace should be relative to yaml file not to cwd

Reported by @pimlie on 2025-12-08

### Verify latest release

- [x] I verified that the issue exists in the latest pnpm release

### pnpm version

10.24

### Which area(s) of pnpm are affected? (leave empty if unsure)

Store

### Link to the code that reproduces this issue or a replay of the bug

_No response_

### Reproduction steps

Set `storeDir: ../.pnpm-store` in `pnpm-workspace.yaml`

### Describe the Bug

In root of mono repo:
```bash
/some/project/web $ pnpm config get store-dir
../.pnpm-store
/some/project/web $ pnpm store path
/some/project/.pnpm-store/v10
```

then go to a package in the mono repo:
```bash
/some/project/web/apps/website $ pnpm config get store-dir
../.pnpm-store
/some/project/web/apps/website $ pnpm store path
/some/project/web/apps/.pnpm-store/v10
```


### Expected Behavior

That both `pnpm store path` commands return the same store path

### Which Node.js version are you using?

25.1

### Which operating systems have you used?

- [ ] macOS
- [ ] Windows
- [x] Linux

### If your OS is a Linux based, which one it is? (Include the version if relevant)

_No response_
