# Tries to stat sass.js.EXE when creating bin on Windows

Reported by @nuintun on 2025-11-21

### Verify latest release

- [x] I verified that the issue exists in the latest pnpm release

### pnpm version

v10.23.0

### Which area(s) of pnpm are affected? (leave empty if unsure)

_No response_

### Link to the code that reproduces this issue or a replay of the bug

https://github.com/nuintun/rspack-antd-builder

### Reproduction steps

pnpm i



### Describe the Bug

Since v10.20.0

<img width="1554" height="133" alt="Image" src="https://github.com/user-attachments/assets/d7dc4120-5362-418b-9672-7f1261acafaf" />

### Expected Behavior

No warn

### Which Node.js version are you using?

v25.2.1

### Which operating systems have you used?

- [ ] macOS
- [x] Windows
- [ ] Linux

### If your OS is a Linux based, which one it is? (Include the version if relevant)

_No response_

---

**@nuintun** commented on 2025-12-09:

Lost files in path: `.pnpm\sass-loader@16.0.6_@rspack+_6208cd24e7336cc233eb6459bbe28580\node_modules\sass-loader\node_modules\.bin`

pnpm <= 10.19.0

<img width="236" height="204" alt="Image" src="https://github.com/user-attachments/assets/16edfa45-8891-46e8-b7fb-d0faab6bb910" />

pnpm > 10.19.0

<img width="262" height="138" alt="Image" src="https://github.com/user-attachments/assets/b5d6969c-84e6-4095-b988-dbf70fdbd640" />
