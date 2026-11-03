# Changelog

## 3.0.0 — 2026-11-03

Skill:

- A cleanup or refactoring task covers the whole unit, types included; scope discipline protects the code outside it.
- Changes that a type checker, compiler or test suite can verify are made and verified instead of skipped out of caution.
- Untested code gets characterization tests, run against the original, before it is refactored.
- The final checklist asks for a test covering the new behavior or the fixed bug, and a new "Reporting back" section asks for a short report that claims only what was checked, with the commands run and their actual results.

On six held-out agentic tasks, a blind judge prefers 3.0.0 over 2.0.0 with Claude Sonnet 5.5 (12 wins, 4 ties, 2 losses) and Claude Opus 5.5 (9, 6, 3); with Claude Haiku 5.5 the direction is the same (10, 2, 6) but not significant. The single-turn suite was not rerun.

Evals:

- Agentic track: coding agents work with real tools in nine fixture repositories (three `dev`, six held-out `test` cases written without access to the skill), deterministic checks with stored evidence (hidden tests, diff scope, regression and characterization tests run against the original code, test runs after the last edit), a reference solution per case checked by `selftest_agentic.py`, a blind pairwise judge that judges both orders and gives reasons, and a report with bootstrap intervals per coder model.
- Every measured skill version is a frozen copy in `evals/skills/` (`v1`, `v2`, `v3a` = 3.0.0, and `v3b`, a condensed alternative), so a release never changes what earlier results measured.
- `report_agentic.py` draws the README charts; `report.py` and it share one chart theme in `charts.py`.

## 2.0.0 — 2026-11-02

First public release.

- Rewritten in English for use across agents and teams.
- Precedence order: correctness, then codebase conventions and language idioms, then Beck's rules, then the heuristics.
- New sections: scope discipline, when not to apply a rule, agent failure modes, review mode.
- New references: `language-idioms.md`, `agent-pitfalls.md`, `examples.md`; heuristics catalog translated.
- Eval suite with blind grading against no skill, sickn33/clean-code and v1.
- Packaged for skills.sh and as a Claude Code plugin marketplace.

## 1.0.0

Private German version (kept for comparison in `evals/skills/v1.md`).
