# nil pointer dereference due to HelpFlag when running in parallel

Reported by @G-Rath on 2025-08-07

## My urfave/cli version is

v3.3.8

## Checklist

- [x] Are you running the latest v3 release? The list of releases is [here](https://github.com/urfave/cli/releases).
- [x] Did you check the manual for your release? The v3 manual is [here](https://cli.urfave.org/v3/getting-started/)
- [x] Did you perform a search about this problem? Here's the [GitHub guide](https://help.github.com/en/github/managing-your-work-on-github/using-search-to-filter-issues-and-pull-requests) about searching.

## Dependency Management

<!--
  Delete any of the following that do not apply:
-->

- My project is using go modules.
- My project is automatically ~downloading~ updating to the latest version.

## Describe the bug

The `HelpFlag` has a self-described hack using a global which can result in a nil pointer dereference if run in parallel

https://github.com/urfave/cli/blob/c1855736d81861a94d9a61f838ea73de96200e43/command_setup.go#L203-L211

## To reproduce

```go
// debug_test.go
package debug_test

import (
	"context"
	"fmt"
	"os"
	"testing"

	"github.com/urfave/cli/v3"
)

func RunCli(args []string) {
	cmd := &cli.Command{
		Name:     "debug",
		Usage:    "make an explosive entrance",
		Action: func(_ context.Context, cmd *cli.Command) error {
			return nil
		},
	}

	if err := cmd.Run(context.Background(), args); err != nil {
		fmt.Printf("%s\n", err)
	}
}

type Case struct {
	Name string
	Args []string
	Exit int
}

func Test_run(t *testing.T) {
	t.Parallel()

	tests := []Case{
		{
			Name: "hello_world",
			Exit: 0,
		},
		{
			Name: "hello_sunshine",
			Exit: 0,
		},
	}
	for _, tt := range tests {
		t.Run(tt.Name, func(t *testing.T) {
			t.Parallel()

			defer func() {
				if r := recover(); r != nil {
					t.Errorf("unexpected panic - '%s' passing %s", r, tt.Args)
				}
			}()

			RunCli(tt.Args)
		})
	}
}
```

```
❯ go test ./cmd/osv-scanner/debug/... -count 100000 -failfast
--- FAIL: Test_run (0.00s)
    --- FAIL: Test_run/hello_world (0.00s)
        debug_test.go:59: unexpected panic - 'runtime error: invalid memory address or nil pointer dereference' passing []
FAIL
FAIL    github.com/google/osv-scanner/v2/cmd/osv-scanner/debug  3.111s
FAIL
```

## Observed behavior

A nil pointer dereference

## Expected behavior

No error

## Additional context

We found this in `osv-scanner` and our understanding is that it only impacts our test suite since CLI users will only run through this code path once; it's also uncommon, but still common enough that we do have CI failures from it maybe about once a week and it can be more common when running the test suite locally (likely because dev machines tend to have more CPU cores and threads available).

Setting `HideHelp: false` does avoid the issue which we might be able to use as a workaround, but I figured since there's a "TODO" about this already in the code might as well open an official issue for it either way

## Want to fix this yourself?

I'm happy to help, though not sure if I'll be able to tackle this one by myself

## Run `go version` and paste its output here

```
go version go1.24.4 linux/amd64
```

## Run `go env` and paste its output here

```
AR='ar'
CC='gcc'
CGO_CFLAGS='-O2 -g'
CGO_CPPFLAGS=''
CGO_CXXFLAGS='-O2 -g'
CGO_ENABLED='1'
CGO_FFLAGS='-O2 -g'
CGO_LDFLAGS='-O2 -g'
CXX='g++'
GCCGO='gccgo'
GO111MODULE=''
GOAMD64='v1'
GOARCH='amd64'
GOAUTH='netrc'
GOBIN=''
GOCACHE='/home/jones/.cache/go-build'
GOCACHEPROG=''
GODEBUG=''
GOENV='/home/jones/.config/go/env'
GOEXE=''
GOEXPERIMENT=''
GOFIPS140='off'
GOFLAGS=''
GOGCCFLAGS='-fPIC -m64 -pthread -Wl,--no-gc-sections -fmessage-length=0 -ffile-prefix-map=/tmp/go-build3604199268=/tmp/go-build -gno-record-gcc-switches'
GOHOSTARCH='amd64'
GOHOSTOS='linux'
GOINSECURE=''
GOMOD='/home/jones/workspace/projects-oss/osv-scanner/go.mod'
GOMODCACHE='/home/jones/go/1.24.2/pkg/mod'
GONOPROXY=''
GONOSUMDB=''
GOOS='linux'
GOPATH='/home/jones/go/1.24.2'
GOPRIVATE=''
GOPROXY='https://proxy.golang.org,direct'
GOROOT='/home/jones/go/1.24.2/pkg/mod/golang.org/toolchain@v0.0.1-go1.24.4.linux-amd64'
GOSUMDB='sum.golang.org'
GOTELEMETRY='local'
GOTELEMETRYDIR='/home/jones/.config/go/telemetry'
GOTMPDIR=''
GOTOOLCHAIN='auto'
GOTOOLDIR='/home/jones/go/1.24.2/pkg/mod/golang.org/toolchain@v0.0.1-go1.24.4.linux-amd64/pkg/tool/linux_amd64'
GOVCS=''
GOVERSION='go1.24.4'
GOWORK=''
PKG_CONFIG='pkg-config'
```


---

**@dearchap** commented on 2025-08-16:

@G-Rath yes generally this library isnt thread safe and we make not guarantees for it. There is no real reason to get rid of the hack for now. We will keep it in mind for the next major version of the library.
