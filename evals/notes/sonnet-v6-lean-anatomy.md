# Where the tokens go (67 Sonnet runs, before v6)

Source: the evaluated agents' transcripts, measured with `evals/sonnet/anatomy.py` and two scratch variants of it.

The reported "tokens per run" is the final context size: the last turn's input (uncached, cache write and cache read) plus its output. For a 39-line run this was 57,007 by turn usage against 57,232 reported.

| Part | Median tokens | Notes |
|---|---|---|
| Starting context (harness system prompt and tools) | 43.4K | identical in every run (43,381 to 43,387); no skill can change it |
| Growth: no skill | 20.4K | |
| Growth: v3 | 17.9K | |
| Growth: v5 | 24.1K | |

About half of the growth is hidden reasoning. Thinking blocks are stored redacted, but they count in context. Visible-content estimate against growth:

| Arm | Visible (tokens) | Residual (tokens) | Turns |
|---|---|---|---|
| v3 | 8.9K | 8.8K | 26 |
| v5 | 10.8K | 12.4K | 30 |
| No skill | 9.5K | 10.7K | 24 |

Visible tool traffic, all runs:

| Kind | Share |
|---|---|
| Reading source through the shell (`sed -n`, `cat`, `head`) | 31.2% |
| `Read` tool (almost all of it the run's `task.md` prompt) | 18.8% |
| Writing scripts with heredocs | 14.6% |
| Test-runner output | 12.9% |
| `git` history | 6.6% |
| Running scripts | 4.5% |
| Search and listing | 3.7% |
| Installs | 1.5% |
| Agent prose (text blocks) | 0.2% |

v5 against v3 (reproduce runs, median characters per run):
- heredoc scripts: 5,683 vs 2,546;
- script runs: 1,346 vs 1,076;
- search: 338 vs 56;
- source reading: about equal (7.1K each).

So v5's extra cost comes from more turns and more reasoning around its pass-check, plus bigger check scripts. A terser report or output style can't change much: prose is 0.2% of the traffic.
