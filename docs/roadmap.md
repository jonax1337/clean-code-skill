# Roadmap

Issue drafts for work that came out of the evaluation of November 2026. None of it is built yet. Each change to the skill is measured as its own condition before it ships (`evals/candidates/<name>/`, see [`evals/README.md`](../evals/README.md#conditions)), on Sonnet and Opus, against this repo's current skill and the `CLAUDE.md` baseline.

## Design rules from btseee for a reference file

**Why.** With Opus as the coding agent, btseee/clean-code-skills beat this skill on design and readability in the blind comparison (this skill got 38% of the verdicts on both), while losing overall. Its rules for where code goes and how little of it to write are concrete where this skill is general.

**What.** A reference file the skill links to for new code and new files, with these rules in this skill's own words:

- a ladder before writing code: not needed, write nothing; already in the codebase, reuse it; the standard library or an installed dependency does it, use that; one line does it, write the line; otherwise the minimum;
- placement: the role decides the folder; no `utils`/`helpers`/`common` dumping grounds; no sibling variants (`_v2`, `_new`, `_copy`); a new file is fully wired (imports, exports, registration, routes) or it is dead code;
- every changed line traces to the request;
- verification by risk level: what a low-, medium- and high-risk change owes before it is reported done;
- the agent smells A1–A10 as a review checklist next to `agent-pitfalls.md`.

Its `audit` and `clean-up` modes and the structure map (`map_structure.py`, `.clean/structure.md`) are worth a look for a later project-wide cleanup mode, not for single tasks.

**Measure.** Candidate against `this-repo` and the baseline, held-out tasks, Sonnet and Opus, two runs. Done when design and readability do not get worse with Sonnet and improve with Opus.

## Concrete naming examples from ertugrul-dmr

**Why.** With Sonnet, ertugrul-dmr's Python and TypeScript skills beat this skill on readability (this skill: 43% of the verdicts). Its topic skills for names and functions show before/after code where this skill states the rule.

**What.** More before/after pairs for names and function size in `references/examples.md`, written for this repository and in several languages, not only Python and TypeScript.

**Measure.** Together with the btseee rules or alone; same setup.

## A strict mode with hooks

**Why.** A skill can only ask; a hook can enforce. The obvious candidate, a `Stop` hook that blocks when no test run came after the last edit, would barely move the numbers: on the held-out tasks with Sonnet, every condition already ran the tests after its last edit in 25 or 26 of 26 runs, no skill included. Two hooks look more useful:

- a hook that loads the skill on the first coding prompt: installed and never mentioned, the skill loads on its own on 11 of 13 tasks and misses the pull-request review and a performance task;
- a hook that runs the project's formatter and linter after each edit, where the project has them.

**What.** An optional plugin setting or a documented `settings.json` snippet, off by default.

**Measure.** A separate condition per hook (`this-repo` plus the hook), not mixed into the skill's own numbers.

## Other coding agents

**Why.** Only Claude models in Claude Code wrote the code. The skill uses the open Agent Skills format and claims to work in Codex, Cursor and others.

**What.** An agent runner next to `run_agent()` in `evals/agentic.py` for at least one other agent (Codex CLI first: it can run headless), with the same workspace, tools and transcript format so the checks work unchanged. The judge can already be a non-Claude model (`judge_pairwise.py --via gateway`).

**Measure.** No skill, the baseline and this skill on the held-out tasks, two runs.

## Human ratings

**Why.** Both judges are language models. The blind sample in `evals/results/agentic/human/` (15 pairs) is ready but not rated.

**What.** Rate the pairs, run `python evals/human_review.py score --other gpt-6.1-sol`, and report how often each judge agrees with the human, in both READMEs and the eval limits.
