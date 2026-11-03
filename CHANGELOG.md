# Changelog

## Unreleased

Docs:

- New visual identity: an ink-and-mint palette, a reworked icon (also the plugin icon), banner, precedence diagram, a results-at-a-glance card and a workflow diagram in place of the Mermaid flowchart. Every graphic has its own light and dark theme.
- The eval charts share the new theme from `charts.py`: the preference chart lists Sonnet, Opus and Haiku in the order of the README tables and marks 50%, the condition under test is labelled "This skill" and highlighted, the heatmap ramp has its own dark-mode steps, and `report.py` draws quality score and assertions passed as one two-panel chart (`results-single-turn.svg`) instead of two half-width ones.

## 4.0.0 — 2026-11-03

Skill:

- The description now says first when to load the skill: before the first edit whenever the agent writes, changes, fixes, refactors, tests or reviews code. Installed and never mentioned, it loaded on its own on 11 of 13 held-out tasks, and never on tasks without code.
- Reviews state each problem in plain words (a catalog code may follow in parentheses, the skill's own sections are never cited), separate what must change from suggestions, put style nits in one line, ask instead of assuming facts they cannot see, and name the tests that would catch the bugs they found.
- Tests cover behavior where users see it, test a rule that differs per category for each category at its boundaries, keep their inputs in the test instead of reading sample files, and mark pinned behavior that is plainly a bug as such.
- Smaller rules: string literals that carry meaning get names; a function written or substantially changed fits on one screen; each rule, format and constant lives in one place, also within the diff; new enum members and fields keep the existing order; a parameter with a default that no caller changes counts as speculative; hot-path limits do not excuse vague errors; the design is checked against the numbers the task states.
- Reports copy numbers such as test counts from the tool output, mention incidental details only when they were checked, and suggest follow-ups only when they hold against the code and the docs.

Evals:

- Both benchmarks now compare the skill as it is in the repository with no skill and with three other clean-code skills, each pinned to a commit: unclebob/ub-mode, sickn33/clean-code and ertugrul-dmr/clean-code-skills (Python and TypeScript only). Frozen copies of earlier versions of this skill and their results were removed; the git history keeps them.
- Agentic track: 20 tasks in Python, TypeScript, JavaScript, Java and Rust (7 dev, 13 held out and written by agents that never saw the skill), run with Claude Sonnet, Opus and Haiku; the blind judge also rates six dimensions; function metrics from lizard; a trigger track that measures whether an installed skill loads on its own and with one line in `CLAUDE.md`.
- Harness: sessions that end on a login or usage-limit error are discarded and run again; commit messages no longer count as file edits in the "tests after the last edit" check; agents commit under a repository-local identity; the skill fingerprint ignores the `version:` line, so a release bump does not invalidate measured runs.

## 3.0.0 — 2026-11-03

Skill:

- A cleanup or refactoring task covers the whole unit, types included; scope discipline protects the code outside it.
- Changes that a type checker, compiler or test suite can verify are made and verified instead of skipped out of caution.
- Untested code gets characterization tests, run against the original, before it is refactored.
- The final checklist asks for a test covering the new behavior or the fixed bug, and a new "Reporting back" section asks for a short report that claims only what was checked, with the commands run and their actual results.

Evals:

- Agentic track: coding agents work with real tools in fixture repositories, split into `dev` cases and held-out `test` cases written without access to the skill; deterministic checks with stored evidence (hidden tests, diff scope, regression and characterization tests run against the original code, test runs after the last edit), a reference solution per case checked by `selftest_agentic.py`, a blind pairwise judge that judges both orders and gives reasons, and a report with bootstrap intervals per coder model.
- `report_agentic.py` draws the README charts; `report.py` and it share one chart theme in `charts.py`.

## 2.0.0 — 2026-11-02

First public release.

- Rewritten in English for use across agents and teams.
- Precedence order: correctness, then codebase conventions and language idioms, then Beck's rules, then the heuristics.
- New sections: scope discipline, when not to apply a rule, agent failure modes, review mode.
- New references: `language-idioms.md`, `agent-pitfalls.md`, `examples.md`; heuristics catalog translated.
- Eval suite with blind grading against no skill and sickn33/clean-code.
- Packaged for skills.sh and as a Claude Code plugin marketplace.

## 1.0.0

Private German version.
