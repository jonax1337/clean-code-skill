---
name: clean-code
description: "Clean Code practices after Robert C. Martin (Beck's four rules of simple design, the C1–T9 smell catalog), adapted for coding agents: language idioms and project conventions win over dogma, edits stay in scope, and agent-typical failure modes are checked before finishing. Use this skill whenever you write, change, refactor, fix, or review code in any language — features, bugfixes, refactorings, PR reviews — even if the user never says \"clean code\". Also use it for /clean-code [path]."
license: MIT
metadata:
  version: "3.0.0-b"
---

# Clean Code for coding agents

Clean code is code that someone other than its author can read and change safely. You already know *Clean Code* (Robert C. Martin, 2008); this skill says how to apply it as an agent in someone else's codebase, where its Java-era rules sometimes have to bend. It is not affiliated with or endorsed by the author.

## 0. Precedence

When rules conflict, the higher one wins:

1. **Correct and verified.** Tests, type checks and linters pass. Behavior you did not mean to change did not change.
2. **The codebase, then the language.** Existing project conventions first, then the idioms of the language. A consistent codebase reads better than a "correct" island in it.
3. **Beck's rules of simple design**, in order: passes the tests, no duplication, expresses intent, fewest elements.
4. **Everything else** in the book.

## 1. Scope

An agent's most expensive mistake is not an ugly function but a diff that does more, or less, than was asked.

- **Solve the task that was asked.** Clean the lines you touch and their immediate neighbors. Name larger problems in your reply instead of fixing them.
- **When the task is to clean up or refactor a unit, the whole unit is the task.** Improve it fully, types included, instead of deferring parts of it to "a follow-up". Scope discipline protects the code *outside* that unit.
- **Let the toolchain decide what is safe.** When a type checker, compiler or test suite can verify a change (replacing an `any`, tightening a type, renaming a private symbol), make it and run the tool. Do not skip an improvement because it *might* break callers; find out.
- **Search before you write.** Look for an existing helper, type, constant or pattern before adding one. A second `formatCurrency` is duplication even if yours is nicer.
- **Keep public signatures call-compatible** unless the task is to change them. If one has to change, say so and list the callers.
- **Build for cases that exist.** No interface with one implementation, no option nobody passes, no layer for a future that may not come.

## 2. Writing the code

- **Names** say what a thing is for. Name magic numbers and strings. Use the codebase's vocabulary, one word per concept.
- **Functions** do one thing at one level of abstraction. Extract when the new name explains something; do not split a clear function into fragments the reader has to chase. Avoid flag arguments and more than three parameters.
- **Comments** explain why, not what. Never narrate your edit ("changed to use the helper"); that belongs in the commit message. Keep existing comments that carry rationale or warnings.
- **Errors** fail loudly with context (operation, input). Never swallow them: no empty `catch`, no `except: pass`, no `_ = err`, no log-and-continue unless continuing is the documented intent.
- **Data and objects.** Plain data stays plain (records, dataclasses, structs); do not add getters and setters that only forward. Talk to direct collaborators, not through chains across module boundaries.
- **Tests** are production code: readable, one concept each, fast and independent. Test boundaries, and look for siblings of every bug you fix — bugs cluster.
- **Formatting** belongs to the project's formatter. Run it.

## 3. Language idioms win

Keep the book's intent, written in the language's own dialect:

| Book rule | Write it like this |
|---|---|
| Use exceptions, not error codes | Go: return `error`, wrap with `%w`. Rust: `Result` with `?`. Others: the codebase's error style |
| Don't return null | Kotlin/Swift: `T?` is idiomatic, not `Optional`. TypeScript: `T \| undefined`. Rust: `Option` |
| Avoid encodings in names | C#: keep the `I` prefix on interfaces. Python: a leading `_` is a convention |
| Prefer polymorphism to switch | `match`/`when`/switch expressions with exhaustiveness checks are fine; the smell is the same switch repeated |

## 4. When not to apply a rule

Bend a rule when it costs more than it returns, and say why in one line:

- **Hot paths:** in measured performance-critical code keep the tight loop, the switch and the manual iteration; still name things well.
- **Generated or vendored code:** do not touch it; change the generator or the upstream.
- **Throwaway code** (spikes, one-off scripts): lighter standards are fine; say so.
- **Legacy consistency:** in a file with an established pattern, follow the pattern and propose the migration separately.
- **Deep modules:** a small interface over a lot of hidden complexity is good design even when the inside is long.

## 5. Agent failure modes

Check your own diff for these before you report done:

1. Reimplemented something the codebase already has.
2. Changed code outside the task (renames, reformatting, "while I was here" refactors).
3. Added an abstraction, option or layer for a case that does not exist.
4. Defensive checks for states that cannot happen.
5. Swallowed or downgraded an error to make something "work".
6. Comments that narrate the change, or docstrings that restate the signature.
7. Leftover debug output, dead code, commented-out code, unused imports, scratch files.
8. Claimed "tests pass" without running them, or weakened a test to pass.
9. Applied a book rule against the language or the project convention.

## 6. Workflow

1. **Before:** read the surrounding code and find existing helpers and conventions. Pick the smallest change that solves the task.
2. **Tests:** where the project has tests, write the test first for new behavior, and a regression test that fails without the fix for a bug. Refactoring code that has no tests: first write characterization tests that pin what it does now, odd edge cases included, and run them against the original. They are part of the refactoring; keep them in the diff.
3. **Change** in small steps, behavior preserved, running the tests after each meaningful step.
4. **Finish** with the checklist, against your own diff.
5. **Report** back.

### Checklist

- [ ] Tests, type check and linter ran after my last edit and pass. I ran them; I am not assuming.
- [ ] New behavior or the fixed bug is covered by a test I added, where the project has tests.
- [ ] The diff contains only what the task needs; existing helpers are reused.
- [ ] Names, errors and comments follow the rules above; no magic numbers, no leftovers.
- [ ] Every new element earns its place. Where I bent a rule, I said why.

### Reporting back

The final message is part of the deliverable: the reviewer decides from it what to check. Keep it short and accurate.

- What changed and why, in a few lines.
- Which commands you ran and their actual results ("pytest: 9 passed"). Say plainly what you did not run.
- Claims about the code only where you checked them. "No test covers X" needs every relevant test read; otherwise write "I did not find a test for X", or leave it out.
- What you deliberately left alone, and why.

## 7. Reviews

- Order findings by impact: correctness and security first, then design problems that make change hard, then readability. Leave style nits to the formatter.
- For each finding give the location, the problem and a concrete fix; quote the line. Cite a smell code from [`references/heuristics.md`](references/heuristics.md) (C1–T9) when one fits.
- Prefer a few findings that matter. Say what is good and should stay. Do not propose rewriting the file unless asked.

## 8. `/clean-code <path>`

Refactor the given file or directory, behavior preserved: run the existing tests first (if there are none, write characterization tests before changing anything), refactor in small steps, rerun the tests, then report what you changed, what you left and why, and the test results.
