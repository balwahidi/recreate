"""Per-case environment for the Sonnet harness (evals/sonnet).

AGENT_SETUP prepares the agent's base checkout once (it never fetches the fix).
WORKSPACE_SETUP runs inside each run's copy before the agent starts.
RUN_PREFIX is prepended to the agent's run_command when grading.
"""
CASES = [
    "eslint-19957", "eslint-19924", "eslint-19637", "eslint-20209-fixed",
    "vue-13611", "urfave-cli-2176", "pydantic-11849", "ripgrep-3009", "ts-60573",
]

NPM = "npm install --ignore-scripts --no-audit --no-fund"
AGENT_SETUP = {
    "eslint-19957": NPM, "eslint-19924": NPM, "eslint-19637": NPM, "eslint-20209-fixed": NPM,
    "vue-13611": "pnpm i --frozen-lockfile",
    "urfave-cli-2176": "go mod download && go build ./... && go test -count=1 -run XXX_NONE ./... >/dev/null",
    "pydantic-11849": "true",
    "ripgrep-3009": "cargo build -q && cargo test -q -p ignore --lib --no-run",
    "ts-60573": "npm ci --ignore-scripts --no-audit --no-fund && npx hereby local",
}
WORKSPACE_SETUP = {
    "pydantic-11849": "python3 -m venv .venv && .venv/bin/pip install -q -e . pytest",
}
RUN_PREFIX = {
    "pydantic-11849": "source .venv/bin/activate && ",
}
# What the agent is told about its environment, per case.
ENV_NOTE = {
    "pydantic-11849": "A virtualenv with this checkout installed in editable mode (plus pytest) is at .venv; activate it with `source .venv/bin/activate`. Your run_command will be run from the repo root with it activated.",
    "ripgrep-3009": "Dependencies are fetched and a debug build plus the `ignore` crate's test binary are already compiled.",
    "ts-60573": "Dependencies are installed and `npx hereby local` has already built built/local.",
    "urfave-cli-2176": "Go modules are downloaded and the package builds.",
    "vue-13611": "Dependencies are installed with pnpm.",
}
DEFAULT_ENV_NOTE = "Dependencies are installed."
