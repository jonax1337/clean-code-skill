---
name: clean-code
description: "Load before your first edit whenever you write, change, fix, refactor, test or review source code in any language: features, bugfixes, cleanups, tests, pull-request reviews, even when the user never mentions clean code. It keeps the change in scope, reuses what the codebase already has, pins behavior with tests and checks the diff for the mistakes agents typically make before reporting back. Clean Code (Robert C. Martin) and Beck's rules of simple design, adapted so project conventions and language idioms win over dogma. Also for /clean-code [path]."
license: MIT
metadata:
  version: "4.0.0"
---

# Clean Code Skill

> Clean code can be read, and enhanced by a developer other than its original author.
> — Dave Thomas, quoted in *Clean Code*

This skill condenses *Clean Code* (Robert C. Martin, 2008) into rules an agent can apply while it works. It is not affiliated with or endorsed by the author. The full smell catalog C1–T9 lives in [`references/heuristics.md`](references/heuristics.md). In a review, state each problem in plain words; a catalog code may follow in parentheses for readers who know it.

The book was written for humans writing Java in 2008. You are an agent working in someone else's codebase today. Most of its advice transfers; some of it has to bend. Section 0 says how.

## 0. Precedence

When rules conflict, the higher one wins:

1. **Correct and verified.** Tests, type checks and linters pass. Behavior you did not mean to change did not change.
2. **The codebase and the language.** Existing project conventions, then the idioms of the language and its ecosystem. A consistent codebase is easier to read than a "correct" island in it (G11, G24).
3. **Beck's four rules of simple design**, in order: passes the tests, no duplication, expresses intent, fewest elements.
4. **The heuristics** in this file and in `references/heuristics.md`.

Why this order: the book's rules are means to readable, changeable code. When a rule fights the language (exceptions in Go, `Optional` in idiomatic Kotlin, dropping the `I` prefix in C#), following it makes the code *less* readable to the people who maintain it. See [`references/language-idioms.md`](references/language-idioms.md) for the common translations.

## 1. Scope discipline

An agent's most expensive mistake is not an ugly function. It is a diff that does more than was asked. Reviewers then have to separate the change they wanted from the changes they did not.

- **Solve the task that was asked.** Clean the code you touch (the Boy Scout Rule applies to the lines in your diff and their immediate neighbors). Name larger problems elsewhere in your reply instead of fixing them.
- **When the task is to clean up or refactor a unit, the whole unit is the task.** Improve it fully, types included, instead of deferring parts of it to "a follow-up". Scope discipline protects the code *outside* the unit you were asked to change, not the unit itself.
- **Let the toolchain decide what is safe.** When a type checker, compiler or test suite can verify a change (replacing an `any`, tightening a type, renaming a private symbol), make the change and run the tool. Do not skip an improvement because it *might* break callers; find out. Back out only what the tool shows to be wrong.
- **Search before you write.** Look for an existing helper, type, constant or pattern before adding one. A second `formatCurrency` is duplication (G5) even if yours is nicer.
- **Write the least code that does the job.** Not needed: write nothing. In the codebase: reuse it. In the standard library or an installed dependency: use that. Otherwise the minimum, without cutting validation or error handling.
- **Put new code where code of its kind already lives.** No new `utils`, `helpers` or `common` module, no `_v2` or `_new` copy next to the original. A new file is wired in (imports, exports, registration) or it is dead code.
- **Keep public signatures stable** unless the task is to change them. If a refactoring has to change one, say so and list the callers. Add new enum members, fields and options so that existing order and identity stay the same, usually at the end.
- **No speculative generality.** No interfaces with one implementation, no options nobody passes (a parameter with a default that no caller changes is one), no plugin systems for one plugin. Add the abstraction when the second case arrives.
- **Leave nothing behind:** debug prints, commented-out code (C5), unused imports, scratch files, TODOs you could have resolved.

## 2. Names (ch. 2)

- A name says why the thing exists, what it does and how it is used. If it needs a comment, rename it (N1).
- No disinformation (`accountList` that is a map) and no noise distinctions (`data1/data2`, `ProductInfo` vs `ProductData`).
- Pronounceable and searchable. Name magic numbers, and string literals that carry meaning such as codes, keys and statuses (G25). Name length grows with scope (N5): `i` in a three-line loop is fine.
- Name a value when the reader cannot tell its meaning at the use site. A unit factor next to its unit (`seconds * 1000` into `timeoutMs`) is already clear; a constant used in one file stays private to that file.
- Classes are nouns, methods are verbs. `Manager`, `Processor`, `Helper` usually hide a missing concept.
- One word per concept (`fetch`/`get`/`retrieve` — pick one). Side effects belong in the name (N7).
- Encodings (N6): avoid Hungarian notation and `m_`. Where the ecosystem uses a prefix by convention (C# `IRepository`), the convention wins.

## 3. Functions (ch. 3)

- **Small, and doing one thing** (G30). Test: if you can extract a function whose name is not just a restatement of its body, the original did more than one thing.
- **One level of abstraction per function** (G34). Read top-down: each function is followed by the ones it calls, one level lower (stepdown rule).
- Size is a symptom, not the goal. A function you write or substantially change should fit on one screen (about 30 lines) with little nesting; when it does not, look for the part that deserves a name of its own. Do not split a clear function into five-line pieces the reader has to chase. Extract when the new name explains something the reader would otherwise have to work out.
- **Arguments:** fewer is better; more than three wants a parameter object (F1). No flag arguments (F3) or selector arguments (G15) — split the function. No output arguments (F2).
- **Prefer the direct form.** A plain loop over a clever chain, an explicit assignment over a mutator's return value (`push(x) - 1`), one place that changes a piece of state over updates spread across helpers.
- **No hidden side effects.** Command–query separation: a function either changes state or answers a question. Make required ordering visible by passing results along (G31).
- **Errors:** use the language's error mechanism consistently. Keep error handling apart from the main path; a function that handles errors does little else.

## 4. Comments (ch. 4)

Comments explain what the code cannot: *why* this approach, warnings about consequences, references to specs or bug reports, the format behind a regex, legal headers, docs for public APIs.

Delete or avoid: comments that restate the code (C3), journal and author lines (C1), obsolete comments (C2), commented-out code (C5), position markers, closing-brace comments, mandatory boilerplate docs on private helpers.

Agent-specific: never write comments that narrate your edit (`// changed to use the new helper`, `// fixed bug`). That belongs in the commit message. Keep existing comments that carry rationale, security notes or license text, even when you rewrite the code around them.

## 5. Formatting (ch. 5)

- The project's formatter and style decide. Run it; do not hand-format against it.
- Newspaper order: high-level first, details below. Related code stays close together (G10); concepts are separated by a blank line.
- Declare variables near their use. Callers above callees.

## 6. Objects and data structures (ch. 6)

- Objects hide data behind behavior; data structures expose data and have no behavior. Pick one per type; avoid hybrids.
- Law of Demeter (G36): talk to direct collaborators. `order.customer().address().city()` across module boundaries is a train wreck; fluent builders and plain data records are not.
- Records, data classes and structs are the right tool for plain data.

## 7. Error handling (ch. 7)

- Fail loudly with context: which operation, which input, what went wrong.
- **Never swallow errors.** No empty `catch`, no `except: pass`, no `_ = err`, no catch-log-continue unless continuing is the documented intent.
- Define error types around what the caller needs to distinguish. Wrap third-party errors at the boundary.
- Avoid returning or passing `null` where the language gives you something better (empty collections, `Option`/`Result`, special-case objects). In languages with null-safe types (Kotlin, Swift, TypeScript strict), a nullable return for "not found" is idiomatic and fine.

## 8. Boundaries (ch. 8)

- Wrap third-party APIs where they enter your code; do not pass library types through your whole public API.
- Learning tests pin down how a foreign API behaves before you build on it.

## 9. Tests (ch. 9)

- Test code is production code: readable first. One concept per test, Arrange–Act–Assert, few asserts.
- F.I.R.S.T.: fast, independent, repeatable, self-validating, timely.
- Test boundaries (T5) and look around every bug you fix (T6) — bugs cluster.
- Test behavior where users see it: a bug found in a report gets a test on the report, not only on the helper you extracted. Every behavior you add that a user can see (a label, a message, a status) gets a test.
- Where code applies a rule per category (per currency, type or status), test each category's rule at its boundaries, not one representative.
- Where the project has tests: a bugfix gets a regression test that fails without the fix. Test-first is the default for new behavior. Do not write tests that only assert the implementation's current internals.
- Never disable, skip or loosen a failing test to get green (G4). Find out why it fails.
- **Refactoring code that has no tests: pin its behavior first.** Write characterization tests that capture what the code does now, odd edge cases included, and run them against the original. Then refactor and run them again. They are part of the refactoring, not extra scope, so keep them in the diff. Put the inputs in the test itself rather than reading sample data files that may change. When the current behavior is plainly a bug, pin it anyway, but say so in the test name and the report, so that a later fix is not mistaken for a regression.

## 10. Classes and systems (ch. 10–11)

- Small, measured in responsibilities: one reason to change (SRP). If the class name needs "and", it has two.
- High cohesion: methods use most of the fields. When a subset of fields and methods clusters, that is a new class.
- Depend on abstractions at real seams (I/O, external services, things you need to fake in tests) — not everywhere.
- Separate construction from use: wiring happens in `main`, factories or the DI container.
- Keep configuration at the top level (G35); avoid configurability nobody asked for.

## 11. Concurrency (ch. 13)

- Keep concurrency code separate from domain logic. Minimize shared mutable state; prefer immutable data and message passing.
- Use the platform's concurrent primitives instead of hand-rolled locking. Keep critical sections small.
- Treat a flaky failure as a real bug until proven otherwise.

## 12. When not to apply a rule

Rules serve readability and changeability. Bend them when they cost more than they return, and say why in one line:

- **Hot paths.** In measured performance-critical code (inner loops, per-frame/per-tick code, allocation-sensitive paths), a `switch` beats virtual dispatch, a manual loop beats a stream, and one longer function beats calls that the compiler might not inline. Keep the structure; still name things well and explain the trade-off. The limits are about allocation and dispatch, not about quality: error types, messages and names still improve.
- **Generated and vendored code.** Do not touch it; change the generator or the upstream.
- **Spikes, one-off scripts, notebooks.** Lighter standards are fine when the code is meant to be thrown away. Say so instead of polishing.
- **Legacy consistency.** In a file with an established pattern, a new function that follows the pattern beats one that is cleaner but different. Propose the migration separately.
- **Deep modules** (John Ousterhout, *A Philosophy of Software Design*). A module with a small interface that hides a lot of complexity is good design, even when its internals are longer than the "small functions" advice suggests.

## 13. Agent failure modes

Check your own diff for these before you report done. They are the mistakes reviewers most often find in agent-written code. Details and examples: [`references/agent-pitfalls.md`](references/agent-pitfalls.md).

1. Reimplemented something the codebase already has.
2. Changed code outside the task (renames, reformatting, "while I was here" refactors).
3. Added an abstraction, option or layer for a case that does not exist yet.
4. Defensive checks for states that cannot happen, hiding the cases that can.
5. Swallowed or downgraded an error to make something "work".
6. Comments that narrate the change, or docstrings that restate the signature.
7. Leftover debug output, dead code, unused imports.
8. Claimed "tests pass" without running them, or weakened a test to pass.
9. Applied a book rule against the language or project convention.

## 14. Workflow

1. **Before:** read the surrounding code. Find existing helpers and conventions. Note the facts the task states (durations, sizes, formats, volumes); your design has to hold for them. Pick the smallest change that solves the task.
2. **Write:** test first where the project has tests. Make it work, then make it clean while the tests stay green.
3. **Refactor** in small steps with behavior preserved. Run the tests after each meaningful step.
4. **Finish** with the checklist below, against your own diff.
5. **Report** back as described below.

### Final checklist

- [ ] Tests, type check and linter ran after my last edit and pass. I ran them; I am not assuming.
- [ ] Where the project has tests, the new behavior or the fixed bug is covered by a test I added.
- [ ] The diff contains only what the task needs. Larger issues are mentioned, not fixed.
- [ ] No duplication with existing code or within my diff (G5): each rule, format and constant lives in one place. Existing helpers are reused.
- [ ] Names reveal intent and match the codebase's vocabulary (N1–N7, G11).
- [ ] Functions do one thing at one level and fit on a screen; no flag or output arguments (F1–F3, G30, G34).
- [ ] Errors carry context and none are swallowed.
- [ ] No magic numbers or meaningful string literals (G25), no train wrecks across boundaries (G36).
- [ ] No dead code, commented-out code, debug output or narrating comments (F4, G9, G12, C1–C5).
- [ ] Every new element earns its place (Beck rule 4).
- [ ] Where I bent a rule (hot path, convention, idiom), I said why.

### Reporting back

The final message is part of the deliverable: the reviewer decides from it what to check. Keep it short and accurate.

- What changed and why, in a few lines.
- Which commands you ran and their actual results ("pytest: 9 passed"). Copy numbers such as test counts from the tool output instead of estimating them. Say plainly what you did not run.
- Claims about the code only where you checked them. "No test covers X" needs every relevant test read; otherwise write "I did not find a test for X", or leave it out. The same goes for incidental details such as line endings, encodings or counts: state them only when a command or a file you read showed them.
- Where the task states numbers (an outage lasts a minute, a file has a million rows), what your design does with them, worked out: "retries now span about 75 s; the outages last about 60 s".
- What you deliberately left alone, and why.
- Follow-up suggestions only when they hold against the code and the docs you read; do not propose what the documentation rules out.

## 15. Reviews

When asked to review code:

- Order findings by impact: correctness and security first, then design problems that make change hard, then readability.
- Separate what must change (bugs, security holes, data loss, broken contracts) from suggestions. A design preference that would change a public signature is a suggestion; say what it costs.
- For each finding: the location (file and line as the file reads after the change, not a line of the diff) with the line quoted, the problem in plain words, why it matters, and a concrete fix. A catalog code may follow in parentheses; never refer to this skill's sections.
- Prefer a few findings that matter over many that do not. Put style nits in one line, or leave them to the formatter.
- When the answer depends on something you cannot see (a database constraint, a caller, a configuration value), ask instead of assuming.
- Name the tests that would catch the bugs you found.
- Say what is good and should stay. Do not propose rewriting the whole file unless that is the request.

## 16. `/clean-code <path>`

Refactor the given file or directory according to this skill, behavior preserved:

1. Run the existing tests first to get a baseline. If there are none, say so and keep refactorings mechanical and low-risk.
2. Refactor in small steps; rerun tests.
3. Report: what you improved, anything you deliberately left (with the reason), test results, and the net line-count change.

## Examples

Before/after pairs in several languages: [`references/examples.md`](references/examples.md). Read them when you are unsure how strongly to apply a rule.
