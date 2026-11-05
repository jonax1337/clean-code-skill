<p align="center">
  <img src="docs/assets/banner.png" alt="Clean Code Skill — The right change. Right here." width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-284fba?labelColor=172740"></a>
  <a href="https://agentskills.io"><img alt="Agent Skills format" src="https://img.shields.io/badge/format-Agent%20Skills-284fba?labelColor=172740"></a>
  <a href="evals/README.md"><img alt="Evals: 28 tasks, blind-graded" src="https://img.shields.io/badge/evals-28%20tasks%2C%20blind--graded-284fba?labelColor=172740"></a>
  <a href="README.de.md"><img alt="Deutsch" src="https://img.shields.io/badge/lang-Deutsch-435573?labelColor=172740"></a>
</p>

**Clean Code Skill** is an [Agent Skill](https://agentskills.io) that teaches coding agents *Clean Code* (Robert C. Martin), including Beck's four rules of simple design and the full C1–T9 smell catalog, and adapts it to how agents actually fail.

Most clean-code skills restate the book. This one also tells the agent **when the book loses**: when the language has a different idiom, when the codebase has a convention, when the code is a hot path, or when "cleaning up" means touching code nobody asked about.

<p align="center">
  <img src="docs/assets/highlights.svg" alt="Results at a glance, 13 held-out tasks, blind pairwise judge: preferred over no skill in 94% of verdicts with Claude Sonnet 5.5 and 71% with Claude Opus 5.5; loaded on its own on 11 of 13 tasks, the other clean-code skills in 1 of 33 runs; with Claude Haiku 5.5 the effect was not measurable" width="880">
</p>

## Why another clean-code skill

An agent that applies the book literally, or does not get it at all, makes predictable mistakes. In the eval runs below:

- without a skill, and with ub-mode or sickn33 loaded, the agent added a `currency` parameter nobody asked for, in all three runs;
- with a book-summary skill loaded, the agent pulled the bit test of a per-packet hot loop into a helper method in all three runs, because "functions should be small", and left the vague exception as it was;
- without a skill, the agent added a feature with no test and never ran the tests after its last edit, and fixed a bug without a regression test, in all three runs;
- installed next to the code and never mentioned, the other clean-code skills loaded on their own in 1 of 33 runs, so in practice they were not used at all.

This skill addresses these with five additions on top of the book:

<p align="center">
  <img src="docs/assets/precedence.svg" alt="Precedence: 1 correct and verified, 2 the codebase and the language, 3 Beck's four rules, 4 heuristics C1–T9" width="760">
</p>

1. **A precedence order.** Correctness first, then the codebase's conventions and the language's idioms, then Beck's rules, then the heuristics. Every bent rule needs a one-line reason.
2. **Scope discipline and agent failure modes.** Search before writing, keep the diff to the task, no speculative abstractions or parameters, no swallowed errors, no narrating comments, no unverified "tests pass". When the task *is* a cleanup, the whole unit is in scope.
3. **Explicit exceptions.** Hot paths, generated code, throwaway scripts, legacy consistency, deep modules.
4. **Verified work, reported accurately.** Pin untested code with characterization tests before refactoring it, cover every fix and every visible behavior with a test, let the type checker and the tests decide what is safe, check the design against the numbers the task states, and end with a report that claims only what was checked.
5. **A description that makes it load.** It tells the agent to load the skill before its first edit on any coding task, so it is used without anyone asking for it.

## Results

Two benchmarks compare this skill as it is in the repository with no skill and with three other clean-code skills: [unclebob/ub-mode](https://github.com/unclebob/ub-mode) by Robert C. Martin, [sickn33/clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) (the clean-code skill with the most installs on skills.sh as of November 2026) and [ertugrul-dmr/clean-code-skills](https://github.com/ertugrul-dmr/clean-code-skills) (Python and TypeScript only). The agentic one is the main evidence: the agent works in a real repository with real tools, and 13 of its 20 tasks were held out while the skill was improved.

### Agentic track: real repositories, held-out tasks

The coding agent gets a fresh copy of a small repository in Python, TypeScript, JavaScript, Java or Rust and the tools Claude Code normally has: read, search, edit and a shell. Deterministic checks grade what it did: hidden tests, which files changed, whether its regression test fails on the old code, whether its tests catch planted bugs, whether it ran the tests after its last edit. A blind judge (Claude Opus 5.5) then reads two pull requests for the same task, once in each order, and says which one it would rather merge and which one is better on correctness, scope, design, readability, tests and the report.

The 13 held-out tasks were written by separate agents that never saw the skill. Each ran twice per coding agent and condition, and every pull request written with this skill was compared with the one written without a skill and with each other skill on the same task.

<p align="center">
  <img src="docs/assets/agentic-preference.svg" alt="Blind judge on 13 held-out tasks, this skill against each alternative. Sonnet: 24 wins of 26 against no skill (94%), 26 of 26 against ub-mode (100%), 20 against sickn33 (84%), 9 of 14 against ertugrul-dmr (79%). Opus: 18 against no skill (71%), 19 against ub-mode (81%), 18 against sickn33 (74%), 7 of 14 against ertugrul-dmr (59%, interval includes 50%). Haiku: 13 against no skill (54%) and 11 against ub-mode (46%), both intervals include 50%; 14 against sickn33 (63%), 10 of 14 against ertugrul-dmr (75%)" width="760">
</p>

| Coding agent | vs no skill | vs ub-mode | vs sickn33 | vs ertugrul-dmr (7 tasks) | Avg. cost per run: no skill → this skill |
|---|---|---|---|---|---|
| Claude Sonnet 5.5 | 24 / 1 / 1 · 94% | 26 / 0 / 0 · 100% | 20 / 5 / 1 · 84% | 9 / 4 / 1 · 79% | $0.09 → $0.17 |
| Claude Opus 5.5 | 18 / 1 / 7 · 71% | 19 / 4 / 3 · 81% | 18 / 3 / 5 · 74% | 7 / 3 / 4 · 59%\* | $0.24 → $0.33 |
| Claude Haiku 5.5 | 13 / 2 / 11 · 54%\* | 11 / 2 / 13 · 46%\* | 14 / 6 / 6 · 63% | 10 / 1 / 3 · 75% | $0.010 → $0.015 |

Wins / ties / losses for this skill and the judge's preference for it, a tie counting half. \* The 95% interval includes 50%, so that comparison is a trend, not a result.

What the numbers say:

- **With Sonnet and Opus the judge prefers this skill over every alternative,** and every interval but one stays above 50%. The lead is largest with Sonnet: 24 of 26 comparisons against no skill and all 26 against ub-mode.
- **With Haiku the skill does not measurably help** against no skill or ub-mode; it still wins against sickn33 and ertugrul-dmr. The small model follows the extra rules less reliably, so the skill pays off most with the larger models.
- **The lead comes mostly from the tests and the report, less from the production code.** Share of the judge's per-dimension verdicts that went to this skill against no skill:

  | Dimension | Sonnet | Opus | Haiku |
  |---|---|---|---|
  | Tests | 93% | 70% | 62% |
  | Report | 78% | 76% | 61% |
  | Readability | 78% | 42% | 50% |
  | Design | 62% | 52% | 46% |
  | Correctness | 57% | 53% | 46% |
  | Scope | 49% | 54% | 48% |

  With Sonnet the code itself also reads better. With Opus and Haiku correctness and design come out about even, and with Opus the code written without a skill even reads slightly better; there the pull request wins on its tests and on a report that says what was run and what was left alone.
- **The checks barely separate the skills on held-out tasks.** Every condition passes 94–99% of them there, so the judge decides. On the dev tasks, where the skill was tuned, they still do: no skill 82%, this skill 100%.
- **The skill costs more.** A run with it costs 35–82% more than without a skill and takes more turns (Sonnet: 12.8 instead of 9.3), mostly for writing and running tests.

<p align="center">
  <img src="docs/assets/agentic-checks.svg" alt="Checks passed with Sonnet. Dev tasks: no skill 82%, this skill 100%, ub-mode 95%, sickn33 88%, ertugrul-dmr 89%. Held-out tasks: no skill 96%, this skill 98%, ub-mode 97%, sickn33 99%, ertugrul-dmr 98%" width="760">
</p>

#### Does a skill load on its own?

The runs above put the skill into the system prompt. In real use it is installed next to the code, and the agent decides whether to load it. Claude Sonnet 5.5, held-out tasks, one run each:

| Installed as a project skill … | This skill | ub-mode | sickn33 | ertugrul-dmr |
|---|---|---|---|---|
| and nothing mentions it | **11 / 13** | 0 / 13 | 0 / 13 | 1 / 7 |
| with one line in `CLAUDE.md` ([below](#usage)) | 13 / 13 | 13 / 13 | 13 / 13 | 7 / 7 |

This skill loaded itself on every task except the pull-request review, where nothing is edited, and a performance task. ub-mode is meant to be switched on with `/ub-mode`, so it is not expected to load on its own. With the one line in `CLAUDE.md`, every skill loaded in every run. On five tasks without code (a poem, an email, a question about TCP, a README summary, a regex explanation) this skill never loaded.

Thirteen tasks with two runs per cell are a small sample, and the intervals describe these tasks, not tasks in general. The judge is Claude Opus, which also wrote one third of the code; it does not know which skill wrote which pull request but may prefer code that reads like its own. ub-mode was measured without its companion tools. After the final runs, one check turned out to misread commit messages as file writes, which only hurt ub-mode (the only skill that makes the agent commit); it was fixed and every run regraded. [`evals/README.md`](evals/README.md#limits) lists these limits in full; transcripts, diffs, checks with evidence and every verdict with its reasons are under [`evals/results/agentic/`](evals/results/agentic).

### Single-turn suite

The second benchmark asks for one reply without tools. Eight realistic coding tasks across Python, TypeScript, Java, Go, Kotlin, C# and JavaScript, each run three times per condition. Claude Sonnet 5.5 wrote the code; Claude Opus 5.5 graded all answers to each task at once under shuffled labels.

<p align="center">
  <img src="docs/assets/results-single-turn.svg" alt="Single-turn suite. Judge quality score: no skill 7.6, this skill 8.5, ub-mode 6.5, sickn33 7.2, ertugrul-dmr 6.7 on 3 of 8 tasks. Assertions passed: no skill 93.3%, this skill 99.2%, ub-mode 95.0%, sickn33 92.5%, ertugrul-dmr 88.9% on 3 of 8 tasks" width="760">
</p>

| Condition | Assertions passed | Judge quality (1–10) | Avg. cost per task |
|---|---|---|---|
| No skill | 93.3% | 7.6 | $0.012 |
| **This skill** | **99.2%** | **8.5** | $0.022 |
| unclebob/ub-mode | 95.0% | 6.5 | $0.023 |
| sickn33/clean-code | 92.5% | 7.2 | $0.018 |
| ertugrul-dmr/clean-code (3 of 8 tasks) | 88.9% | 6.7 | $0.022 |

What the numbers say:

- **A strong model is already good at this.** Without any skill, Sonnet passed 93.3% of the assertions. A clean-code skill has little room to help and plenty of room to hurt.
- **A skill can make things worse.** sickn33/clean-code dropped to 60% on the hot-path task, below no skill, and ertugrul-dmr to 80% on the pull-request review, where no skill passed everything. ub-mode passed more assertions than no skill but got the lowest quality score.
- **This skill passed at least as many assertions as no skill on every task** and raised the average quality score from 7.6 to 8.5. Its one miss: an unrequested `currency` parameter in one of three runs.

<p align="center">
  <img src="docs/assets/results-by-case.svg" alt="Assertions passed per case and condition" width="760">
</p>

Treat these as a sanity check, not a leaderboard: eight cases that were also used to improve the skill, and an LLM judge that sees the answers as written. Every reply and every verdict with its evidence is committed under [`evals/results/`](evals/results), and [`evals/README.md`](evals/README.md) explains both benchmarks and how to rerun them.

## Install

The skill uses the open [Agent Skills](https://agentskills.io) format, so any client that supports it can load it. The evals ran with Claude Code only.

**Via [skills.sh](https://skills.sh)** (installs into Claude Code, Codex, Cursor and other supported agents):

```bash
npx skills add jonax1337/clean-code-skill
```

**Claude Code plugin marketplace:**

```text
/plugin marketplace add jonax1337/clean-code-skill
/plugin install clean-code@clean-code-skill
```

**Manually:** copy `skills/clean-code` into your skills folder, for Claude Code `~/.claude/skills/` (personal) or `.claude/skills/` (per project).

```bash
git clone https://github.com/jonax1337/clean-code-skill
cp -r clean-code-skill/skills/clean-code ~/.claude/skills/
```

## Usage

The skill's description tells the agent to load it before its first edit, so it loads on its own whenever the agent writes, changes, fixes, refactors or tests code, and stays out of tasks without code. You can also call it directly:

```text
/clean-code src/billing/invoice.py      refactor a file or folder, behavior preserved
review this diff with /clean-code       findings ordered by impact, must-fix apart from suggestions
```

Installed as a Claude Code plugin, the skill is namespaced: use `/clean-code:clean-code` instead of `/clean-code`.

To make loading certain, for this skill or any other, add one line to your `CLAUDE.md` or `AGENTS.md`. In the trigger test above it made every measured skill load in every run, reviews included:

```markdown
Before writing, changing or reviewing code, load the clean-code skill and follow it.
```

## How it works

<p align="center">
  <img src="docs/assets/workflow.svg" alt="Six steps: read the surrounding code and find existing helpers; the smallest change that solves the task; test first, or pin untested code with characterization tests; refactor in small steps, tests stay green; final checklist against the own diff; report what changed, the commands run and their real results. A bent rule gets a one-line reason" width="880">
</p>

```text
skills/clean-code/
├── SKILL.md                      precedence, rules by chapter, exceptions, agent failure modes, checklist
└── references/
    ├── heuristics.md             the full C1–T9 catalog with symptoms and fixes
    ├── language-idioms.md        how the book's rules translate to Go, Rust, Kotlin, TS, Python, C#
    ├── agent-pitfalls.md         nine failure modes of coding agents, with what to do instead
    └── examples.md               before/after pairs, including where the book bends
```

`SKILL.md` stays under 200 lines so it is cheap to load on every coding task. The references are read only when needed.

## Other clean-code skills

Several good skills cover the same book with different goals (descriptions as of November 2026; the measured ones at the commits pinned in [`evals/harness.py`](evals/harness.py)):

| Skill | Approach | Measured here |
|---|---|---|
| [unclebob/ub-mode](https://github.com/unclebob/ub-mode) | Robert C. Martin's own short skill: make it work, make it right, follow practice. Meant to be switched on with `/ub-mode`; its companion tools (crapper, dryer, mutator) are installed separately | yes, the skill file without the tools |
| [sickn33/agentic-awesome-skills → clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) | Compact summary of the book in one file, with a note to follow repository conventions | yes |
| [ertugrul-dmr/clean-code-skills](https://github.com/ertugrul-dmr/clean-code-skills) | One main skill per language (Python, TypeScript) plus six topic skills: names, functions, comments, tests, general rules, boy scout | yes, on the Python and TypeScript tasks |
| [hatlesswizard/clean-code-skills](https://github.com/hatlesswizard/clean-code-skills) | 18 skills, one checker per book chapter, plus an orchestrator | no |
| [nghorbani/clean-code-skill](https://github.com/nghorbani/clean-code-skill) | On-demand knowledge base with glossary, patterns and the G1–G36 heuristics | no |
| [markoa/clean-code-skill](https://github.com/markoa/clean-code-skill) | A short, mandatory operating contract of 14 rules | no |
| **this repo** | Book plus precedence, scope discipline, agent failure modes and explicit exceptions, with a description that makes the agent load it before the first edit | yes |

Pick by what you need: a reference to look things up, a per-chapter checker, or a set of working rules for an agent that edits real codebases.

## Contributing

Issues and pull requests are welcome, especially new eval cases. A good case is a realistic task where a naive reading of the book produces a worse result. Add it to [`evals/cases/`](evals/cases) for a single reply, or to [`evals/cases-agentic/`](evals/cases-agentic) as a small repository with hidden tests, checks and a reference solution that `selftest_agentic.py` accepts. Rerun the evals and include the summary in the pull request.

## Credits

Logo, palette and visual guidelines: [Focus identity](docs/branding/README.md).

Based on *Clean Code: A Handbook of Agile Software Craftsmanship* by Robert C. Martin (Prentice Hall, 2008), and on Kent Beck's rules of simple design. This project is not affiliated with or endorsed by the authors. The skill paraphrases the ideas; for the reasoning and the examples behind them, read the book.

## License

[MIT](LICENSE)
