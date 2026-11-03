---
name: clean-code
description: "Clean Code practices after Robert C. Martin (Beck's four rules of simple design, the C1–T9 smell catalog), adapted for coding agents: language idioms and project conventions win over dogma, edits stay in scope, and agent-typical failure modes are checked before finishing. Use this skill whenever you write, change, refactor, fix, or review code in any language — features, bugfixes, refactorings, PR reviews — even if the user never says \"clean code\". Also use it for /clean-code [path]."
license: MIT
metadata:
  version: "3.0.0"
---

# Clean Code for coding agents

> Clean code can be read, and enhanced by a developer other than its original author.
> — Dave Thomas, quoted in *Clean Code*

This skill condenses *Clean Code* (Robert C. Martin, 2008) into rules an agent can apply while it works. It is not affiliated with or endorsed by the author. The full smell catalog C1–T9 lives in [`references/heuristics.md`](references/heuristics.md). Cite those codes in reviews ("violates G5, F3") so findings stay short and checkable.

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
- **Keep public signatures stable** unless the task is to change them. If a refactoring has to change one, say so and list the callers.
- **No speculative generality.** No interfaces with one implementation, no options nobody passes, no plugin systems for one plugin. Add the abstraction when the second case arrives.
- **Leave nothing behind:** debug prints, commented-out code (C5), unused imports, scratch files, TODOs you could have resolved.

## 2. Names (ch. 2)

- A name says why the thing exists, what it does and how it is used. If it needs a comment, rename it (N1).
- No disinformation (`accountList` that is a map) and no noise distinctions (`data1/data2`, `ProductInfo` vs `ProductData`).
- Pronounceable and searchable. Name magic numbers (G25). Name length grows with scope (N5): `i` in a three-line loop is fine.
- Classes are nouns, methods are verbs. `Manager`, `Processor`, `Helper` usually hide a missing concept.
- One word per concept (`fetch`/`get`/`retrieve` — pick one). Side effects belong in the name (N7).
- Encodings (N6): avoid Hungarian notation and `m_`. Where the ecosystem uses a prefix by convention (C# `IRepository`), the convention wins.

## 3. Functions (ch. 3)

- **Small, and doing one thing** (G30). Test: if you can extract a function whose name is not just a restatement of its body, the original did more than one thing.
- **One level of abstraction per function** (G34). Read top-down: each function is followed by the ones it calls, one level lower (stepdown rule).
- Size is a symptom, not the goal. Do not split a clear 30-line function into six 5-line functions that the reader has to chase. Extract when the new name explains something the reader would otherwise have to work out.
- **Arguments:** fewer is better; more than three wants a parameter object (F1). No flag arguments (F3) or selector arguments (G15) — split the function. No output arguments (F2).
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
- Where the project has tests: a bugfix gets a regression test that fails without the fix. Test-first is the default for new behavior. Do not write tests that only assert the implementation's current internals.
- Never disable, skip or loosen a failing test to get green (G4). Find out why it fails.
- **Refactoring code that has no tests: pin its behavior first.** Write characterization tests that capture what the code does now, odd edge cases included, and run them against the original. Then refactor and run them again. They are part of the refactoring, not extra scope, so keep them in the diff.

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

- **Hot paths.** In measured performance-critical code (inner loops, per-frame/per-tick code, allocation-sensitive paths), a `switch` beats virtual dispatch, a manual loop beats a stream, and one longer function beats calls that the compiler might not inline. Keep the structure; still name things well and explain the trade-off.
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

1. **Before:** read the surrounding code. Find existing helpers and conventions. Pick the smallest change that solves the task.
2. **Write:** test first where the project has tests. Make it work, then make it clean while the tests stay green.
3. **Refactor** in small steps with behavior preserved. Run the tests after each meaningful step.
4. **Finish** with the checklist below, against your own diff.
5. **Report** back as described below.

### Final checklist

- [ ] Tests, type check and linter ran and pass. I ran them; I am not assuming.
- [ ] Where the project has tests, the new behavior or the fixed bug is covered by a test I added.
- [ ] The diff contains only what the task needs. Larger issues are mentioned, not fixed.
- [ ] No duplication with existing code (G5). Existing helpers are reused.
- [ ] Names reveal intent and match the codebase's vocabulary (N1–N7, G11).
- [ ] Functions do one thing at one level; no flag or output arguments (F1–F3, G30, G34).
- [ ] Errors carry context and none are swallowed.
- [ ] No magic numbers (G25), no train wrecks across boundaries (G36).
- [ ] No dead code, commented-out code, debug output or narrating comments (F4, G9, G12, C1–C5).
- [ ] Every new element earns its place (Beck rule 4).
- [ ] Where I bent a rule (hot path, convention, idiom), I said why.

### Reporting back

The final message is part of the deliverable: the reviewer decides from it what to check. Keep it short and accurate.

- What changed and why, in a few lines.
- Which commands you ran and their actual results ("pytest: 9 passed"). Say plainly what you did not run.
- Claims about the code only where you checked them. "No test covers X" needs every relevant test read; otherwise write "I did not find a test for X", or leave it out.
- What you deliberately left alone, and why.

## 15. Reviews

When asked to review code:

- Order findings by impact: correctness and security first, then design problems that make change hard, then readability. Style nits last, or not at all if a formatter handles them.
- For each finding give location, the problem, the heuristic code if one fits, and a concrete fix. Quote the line.
- Prefer a few findings that matter over many that do not. Say explicitly what is good and should stay.
- Do not propose rewriting the whole file unless that is the request.

## 16. `/clean-code <path>`

Refactor the given file or directory according to this skill, behavior preserved:

1. Run the existing tests first to get a baseline. If there are none, say so and keep refactorings mechanical and low-risk.
2. Refactor in small steps; rerun tests.
3. Report: the heuristic codes you addressed, anything you deliberately left (with the reason), test results, and the net line-count change.

## Examples

Before/after pairs in several languages: [`references/examples.md`](references/examples.md). Read them when you are unsure how strongly to apply a rule.
