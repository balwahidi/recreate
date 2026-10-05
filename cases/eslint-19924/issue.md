# Bug: running `--fix` throws EMFILE: too many open files

Reported by @cepix1234 on 2025-07-08

### Environment

Node version: 22.11.0
npm version: 10.9.0
Local ESLint version: 9.28.0
Global ESLint version: 9.28.0
Operating System: Windows


### What parser are you using?

Default (Espree)

### What did you do?

eslint ./ --fix

### What did you expect to happen?

All files with auto-fixable issues are fixed.

### What actually happened?

Running `--fix` command in a big repository with 106152 problems and 103.985 auto-fixable issues across ~9000 files. 
I constantly get EMFILE: too many open files error:
`at async open (node:internal/fs/promises:638:25)
    at async Object.writeFile (node:internal/fs/promises:1208:14)
    at async Promise.all (index 8189)
    at async ESLint.outputFixes (...\node_modules\eslint\lib\eslint\eslint.js:534:3)
    at async Object.execute (...\node_modules\eslint\lib\cli.js:642:4)
    at async main (...\node_modules\eslint\bin\eslint.js:175:19)`
https://github.com/eslint/eslint/blob/main/lib/eslint/eslint.js#L533 this happens here!

### Link to Minimal Reproducible Example

/

### Participation

- [ ] I am willing to submit a pull request for this issue.

### Additional comments

Is there a workaround I can set that will work on windows and linux. 
As a QA engineer, I am providing a list of rules and configurations for ESLint for different implementation teams within our company.  Which means all rules will be applied from 0 only once.

---

**@fasttime** commented on 2025-07-08:

I am able reproduce this error in ESLint v9.30.1 using the EMFILE handling test if the command is modified to include the `--fix` option and a fixable rule. For example, by changing [this line](https://github.com/eslint/eslint/blob/v9.30.1/tools/check-emfile-handling.js#L100) as shown below:

```diff
-	`node bin/eslint.js ${OUTPUT_DIRECTORY} -c ${CONFIG_DIRECTORY}/eslint.config.js`,
+	`node bin/eslint.js ${OUTPUT_DIRECTORY} --fix --no-config-lookup --rule "eol-last: [error, always]"`,
```

Running `npm run test:emfile` shows in the output:

```
ESLint: 9.30.1

Error: EMFILE: too many open files, open '.../eslint/tmp/emfile-check/file_92928.js'
    at async open (node:internal/fs/promises:640:25)
    at async Object.writeFile (node:internal/fs/promises:1214:14)
    at async Promise.all (index 92144)
    at async ESLint.outputFixes (.../eslint/lib/eslint/eslint.js:533:3)
    at async Object.execute (.../eslint/lib/cli.js:637:4)
    at async main (.../eslint/bin/eslint.js:175:19)
node:child_process:967
    throw err;
    ^
```

Here's a (_slow!_) StackBlitz repro: https://stackblitz.com/edit/stackblitz-starters-k8itggcp

I think this could be fixed using `@humanwhocodes/retry` to wrap the logic where the autofixed code is written:

https://github.com/eslint/eslint/blob/52a5fcaa4e0bb4e55c014c20ed47d6c93b107635/lib/eslint/eslint.js#L544

Something similar was done in #18313 to fix the very same error occurring with `fs.readFile`.

---

**@fasttime** commented on 2025-07-08:

> Is there a workaround I can set that will work on windows and linux.
> As a QA engineer, I am providing a list of rules and configurations for ESLint for different implementation teams within our company. Which means all rules will be applied from 0 only once.

Thanks for the issue @cepix1234. It's difficult to provide advice without knowing what you are doing. You could perhaps advise the implementation teams to fix parts of the codebase (i.e. the different directories) separately, to reduce the number of files and thus avoid the EMFILE error until the problem is fixed.

---

**@TKDev7** commented on 2025-07-08:

@fasttime Are you working on this? If not, I can take a look.

---

**@fasttime** commented on 2025-07-08:

@TKDev7 You are welcome to work on this. Thanks for asking.
