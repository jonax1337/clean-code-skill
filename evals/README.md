# Evals

Two reproducible benchmarks that check whether a clean-code skill makes a coding agent produce better changes, and whether it avoids the ways "clean code" advice goes wrong in practice. Both compare this repository's skill as it is now against no skill and against other published clean-code skills. Results are in the main [README](../README.md#results); every run, check and verdict is committed under [`results/`](results).

## Conditions

| Name | What the agent gets |
|---|---|
| `none` | no skill |
| `this-repo` | [`skills/clean-code`](../skills/clean-code) as it is in the working tree; every run records a fingerprint of its files, and a run whose skill has changed since is run again |
| `ub-mode` | [`unclebob/ub-mode`](https://github.com/unclebob/ub-mode) by Robert C. Martin, `SKILL.md` only (what `npx skills add` installs). Its companion tools (crapper, dryer, mutator) are installed separately and are not part of the measurement |
| `sickn33` | [`sickn33/agentic-awesome-skills` → `skills/clean-code`](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) |
| `ertugrul-dmr` | [`ertugrul-dmr/clean-code-skills`](https://github.com/ertugrul-dmr/clean-code-skills): the language's main skill (`python-clean-code` or `typescript-clean-code`) with the track's six topic skills as files. It only exists for Python and TypeScript, so it runs on those tasks only |

The other skills are pinned to a commit in [`harness.py`](harness.py) and downloaded into `evals/.cache/` on first use, so a later change upstream does not change what was measured. Skill drafts can be measured as `candidate-<name>` by putting them into `evals/candidates/<name>/SKILL.md`; that folder and its results are git-ignored, so drafts never show up in published numbers.

## Single-turn suite

Eight coding tasks in [`cases/`](cases), each with a realistic prompt and five pass/fail assertions. Five of the eight, marked with ●, target situations where applying the book literally makes the result worse:

| Case | What it checks |
|---|---|
| ● Reuse existing helper (Python) | Searches before writing, keeps the diff in scope |
| ● Refactor a function with many callers (TypeScript) | Preserves behavior and the public signature, names magic numbers, no over-engineering |
| ● Clean up hot-path code (Java) | Readability without allocations, virtual calls or helper splitting in a hot loop |
| ● Error handling in Go | Idiomatic `error` values instead of exception-style patterns |
| ● Nullability in Kotlin | Keeps `T?` instead of forcing "never return null" |
| Review a pull request (Python) | Finds the real bugs first, orders findings by impact |
| Follow codebase conventions (C#) | Keeps the `I` prefix and existing patterns |
| Minimal bugfix with regression test (JavaScript) | Root-cause fix, test, minimal diff |

- **Isolation.** Each reply comes from a fresh `claude -p` process in an empty temp directory with no tools, no MCP servers, no slash commands, no user or local settings and `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`, so the user's own setup cannot leak in. The skill's `SKILL.md` is appended to the system prompt; reference files are not injected, which holds every condition to the same budget.
- **Blind grading.** For each case and repetition, one judge call sees the replies of every condition that applies under shuffled letters and grades every assertion plus an overall 1–10 quality score. A grade is redone when any of the replies it saw changes.
- **Repetitions.** Three runs per case and condition, because single runs of a language model are noisy.

```bash
python evals/run.py --reps 3 --model sonnet   # coding runs; existing, current replies are kept
python evals/judge.py --model opus            # blind judge calls
python evals/report.py                        # results/summary.md + docs/assets/results-*.svg
```

## Agentic track

A single reply cannot show the habits that matter most in an agent: searching the codebase, running the tests, adding a regression test, keeping the diff small. The agentic track gives the agent real tools in a throwaway copy of a small repository and grades what it actually did.

Cases live in two splits. `dev` cases may shape the skill; `test` cases are held out and only measure it. All cases were written by separate agents that never saw the skill, against one standard: what a strict senior reviewer would accept. A second set of agents reviewed every new case for false alarms and loopholes before it was used.

| Split | Case | What it checks |
|---|---|---|
| dev | Feature that needs helpers from other modules (Python) | Finds the money helpers elsewhere (a reimplementation gets the per-line VAT rounding wrong), leaves the messy legacy file alone, adds a test |
| dev | Bugfix in a legacy module with a sibling bug (Python) | Root-cause fix, a regression test that fails on the old code, the sibling bug fixed or reported, no drive-by cleanup |
| dev | Refactor untested code with many callers (TypeScript) | Behavior preserved, callers still type-check, `any` replaced, constants named, characterization tests that pass on the old code |
| dev | Clean up an unreadable report module (JavaScript) | Output and callers unchanged, copy-pasted regional blocks consolidated, magic numbers named, dead code removed, no function over 40 lines, characterization tests that pass on the old code |
| dev | Student discount next to the loyalty discount (Java) | No new abstraction layers or duplicated price calculation, larger discount wins without stacking, money stays `BigDecimal` with one rounding, student tests |
| dev | Retry a flaky carrier API (Python) | Only transient failures retried, gives up with the original error, creates without an idempotency key and pickups never repeated, waiting injectable and never real in tests |
| dev | Tests for an untested rates module (TypeScript) | A suite where the runner finds it that passes on the unchanged code, kills hidden mutants (rounding modes, minor units, fee limits, error cases) and leaves the source untouched |
| test | Split an expense by percentage (Python) | Reuses the cent-exact allocation helper, rejects invalid input without saving, updates README and tests |
| test | CSV import fails on blank lines (Python) | Fixes the parser without making it lenient: malformed rows still fail with the right line number |
| test | Remove a deprecated CLI flag (Rust) | Removes alias, help text, dead code (no compiler warnings), tests and README row; adds a changelog entry; keeps shared helpers |
| test | Refund command for the order service (Java) | Refund limited by what was actually paid minus earlier refunds, exact `BigDecimal` money, bad input rejected, no console output |
| test | Invoice export crashes for some customers (JavaScript) | Customers from both source systems get their own name, an unknown customer still fails loudly and is named in the error, export format unchanged |
| test | Review a pull request (Python) | Finds the SQL injection, the wrong page count and the swallowed audit error; adds only the review and leaves the code untouched |
| test | Add a subscription pause event (TypeScript) | Reducer, audit log and notifier all handle the new event, the type check passes, no other files change |
| test | Clean up a hot-path tokenizer (Rust) | Token stream and public API unchanged, no allocation in the tokenizer, short functions, the repeated blank test folded, clippy clean |
| test | Make configuration errors visible (Java) | Malformed values fail naming key and value, missing required keys and an unreadable file fail, valid and optional settings keep working |
| test | Pull the user validation into one place (JavaScript) | Create unchanged, update stays partial, invite keeps its documented differences, the accidental email drift fixed or reported |
| test | Duration parser switches to milliseconds (TypeScript) | Adapts every caller, including the three that never multiplied and still compile |
| test | Speed up the contact merge (TypeScript) | Linear instead of quadratic while keeping exact old semantics (first match wins, normalized keys, no mutation) |
| test | Split up the checkout function (Python) | Behavior-preserving refactor of a long function whose odd details are deliberate; the neighboring function stays untouched |

- **Runs.** `run_agentic.py` copies `cases-agentic/<split>/<id>/repo/` into a temporary git repository and runs `claude -p` there with Read, Grep, Glob, Edit, Write and Bash, the default Claude Code system prompt and the isolation flags above. Each run stores its transcript (without rate-limit events, which describe the account rather than the run), the exact diff against the fixture's commit (so an agent that commits is graded on everything it changed), a diff for reading, the final report and metadata in `results/agentic/<model>/runs/`. A session that ends on an API, login or usage-limit error is discarded and run again.
- **Three ways to get the skill.** `--mode appended` (default) appends `SKILL.md` to the system prompt, so the skill is always active; this is what the main comparison measures. `--mode installed` installs it as a project skill in `.claude/skills/` with the Skill tool available and mentions it nowhere, so the agent has to decide on its own to load it, as in real use. `--mode instructed` adds the one line a project would put into `CLAUDE.md`: "Before writing, changing or reviewing code, load the … skill and follow it." Both installed modes record which skills the agent loaded; `--setting-sources project` keeps the user's own skills out, so only Claude Code's built-in skills compete.
- **Deterministic checks.** `grade_agentic.py` rebuilds the repository from the fixture plus the diff, adds the hidden tests from `hidden/` and runs the case's `checks.py`: hidden tests, which files changed, AST comparisons of code that must stay untouched, the agent's own tests run against the original code (a regression test must fail there, a characterization test must pass), mutation tests for test-writing tasks, and whether the transcript shows a successful test run after the last edit. Every check stores its evidence. Java cases build with the JDK alone through [`cases-agentic/_java/RunTests.java`](cases-agentic/_java/RunTests.java) and the JUnit console launcher, which the harness downloads once.
- **Function metrics.** `metrics.py` runs [lizard](https://github.com/terryyin/lizard) on the changed source files before and after the change: function length, cyclomatic complexity and parameter count, and how many functions cross 30 lines, complexity 10 or 4 parameters. They are reported next to the checks, not graded, because a longer function is sometimes the right call (hot paths, deep modules).
- **Case self-test.** Every case ships a `reference/` solution. `selftest_agentic.py` grades it (it must pass every check) and the untouched fixture (to show which checks discriminate). It costs nothing; run it after changing a case or `checklib.py`.
- **Pairwise judge.** `judge_pairwise.py` shows the judge (Claude Opus with high effort) the repository, two diffs and two final reports, once in each order, so position bias cancels out. Heuristic codes, skill mentions and reference-file paths are removed first. It asks which pull request the judge would rather merge, why, and which one is better on each of six dimensions: correctness, scope, design, readability, tests and report. By default this repo's runs are compared with every other condition; a verdict is reused until one of its runs changes.
- **Statistics.** `report_agentic.py` writes `results/agentic/summary.md` per coder model and split, with 95 % bootstrap intervals that resample runs within each case and weight cases equally, deltas against no skill and against this repo, the judge's preference per dimension, the function metrics and the trigger results, plus `rationales.md` with every verdict's reasons and the README charts `docs/assets/agentic-*.svg`.

```bash
python evals/selftest_agentic.py                                    # free: every case's reference passes
python evals/run_agentic.py --split test --model sonnet --reps 2    # all conditions, skill appended
python evals/run_agentic.py --split test --model sonnet --reps 1 --mode installed
python evals/run_agentic.py --split test --model sonnet --reps 1 --mode instructed
python evals/grade_agentic.py                                       # free, regrades every run
python evals/judge_pairwise.py --split test                         # this repo against every other condition
python evals/report_agentic.py
```

The TypeScript and JavaScript cases need Node.js (the first run installs TypeScript and `@types/node` into `evals/.cache/node`), the Rust cases need cargo, the Java cases a JDK 17 or newer, and the metrics `uvx` (from [uv](https://docs.astral.sh/uv/)).

## Limits

- **An LLM judge is not a human reviewer.** Assertions and checks are written to be checkable from the output alone, and every verdict stores its evidence and reasons so you can audit it. The judge is Claude Opus, which also wrote the code in one of the three coder runs; it does not know which condition wrote which pull request, but it may prefer code that reads like its own.
- **The grading is only partly blind.** Cues are removed before the pairwise judge sees a change, but a skill also changes style (longer reports, more tests), and a judge can pick that up. In the single-turn suite answers are shown as written.
- **Small samples.** Eight single-turn tasks with three runs, thirteen held-out agentic tasks with two runs per model. The intervals describe these tasks, not tasks in general, and with few runs per cell they are optimistic. ertugrul-dmr is measured on the Python and TypeScript tasks only, so its numbers rest on fewer tasks.
- **Home advantage on dev.** The skill was improved on the dev tasks and on the single-turn suite. Only the held-out test tasks say how it does on work it was not tuned for; read the dev numbers as a check that tuning worked, not as evidence.
- **Checks encode judgment calls** (for example `any_replaced` in the dev refactor, the 30-line limit in the checkout refactor, the changelog entry in the flag removal, the README row that must change with a CLI). Each one is justified by the prompt or the repository and applies to every condition alike; the pairwise judge is the counterweight. Checks were fixed when a false alarm was found, always for every condition, followed by a regrade of every run. One such fix came after the final runs: the detector for shell commands that write files read the `>` in commit messages (for example the closing `>` of `<noreply@anthropic.com>`) as a redirect, so for an agent that commits its work, the commit looked like an edit after the last test run. Only ub-mode makes the agent commit, so only its numbers changed (with Opus from 89 % to 94 % of checks passed).
- **Other skills are measured as their authors ship them,** without tools or setup they recommend elsewhere. ub-mode is meant to be switched on with `/ub-mode`, so it is not expected to load on its own in the installed mode; its tools were not installed.
- **The agent runs with `--permission-mode dontAsk`** and unrestricted Bash in a temporary directory. Environment variables whose names look like secrets (`*_TOKEN`, `*_API_KEY`, `*_SECRET`, …) are removed first, but the agent still has your user account, network access and read access outside the workspace. Run larger studies in a container or VM.
