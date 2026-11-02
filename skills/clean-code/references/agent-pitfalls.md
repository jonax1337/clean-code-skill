# Agent failure modes

*Clean Code* was written about human habits. Coding agents have their own. These are the patterns reviewers most often flag in agent-written diffs, with what to do instead.

## 1. Reimplementing what exists

**Looks like:** a new `formatPrice` next to an existing `formatCurrency`; a fresh HTTP client wrapper in a project that has one; a local retry loop when the codebase has a retry utility.

**Why it happens:** for an agent, writing is cheaper than reading, so it writes first.

**Instead:** search for the concept (names, synonyms, call sites of similar code) before writing. If you find something close but not quite right, extend it or explain why you did not.

## 2. Scope creep

**Looks like:** the task was "add a field"; the diff also renames three variables, reorders imports and converts a loop to a comprehension.

**Why it matters:** the reviewer can no longer see the change they asked for. Unrelated edits carry unrelated risk.

**Instead:** keep the diff to the task plus small cleanups on the lines you had to touch. List other problems at the end of your reply: "Not changed, but worth a look: …"

## 3. Speculative generality

**Looks like:** an interface with one implementation "for testability" when nothing fakes it; a `strategy` parameter with one strategy; config options for values nobody wants to change.

**Instead:** build for the cases that exist. When a second real case arrives, extract what the two actually share (G5); do not design for cases you only imagine.

## 4. Defensive noise

**Looks like:** `if (user != null)` after a call that cannot return null; `try/except Exception` around code that cannot raise; validating the same input at every layer.

**Why it matters:** each check for an impossible case tells the reader the case is possible. Real edge cases drown in fake ones.

**Instead:** validate at the boundary where untrusted data enters. Trust the types and invariants inside.

## 5. Making errors disappear

**Looks like:** `except: pass`, `catch (e) {}`, `_ = err`, returning a default value on failure, or `console.log(e)` and carrying on.

**Instead:** let the error propagate with context, or handle it in a way the caller can see. If ignoring is right, say why in a comment.

## 6. Narrating comments

**Looks like:** `// Updated to use the new validator`, `# Fixed the bug where…`, docstrings that repeat the parameter list.

**Instead:** comments say why the code is the way it is, for a reader who never saw the old version. History goes into the commit message.

## 7. Leftovers

**Looks like:** `print("DEBUG", x)`, unused imports from an abandoned approach, a `test_scratch.py`, commented-out code "for reference".

**Instead:** read your own diff top to bottom before reporting done.

## 8. Unverified claims

**Looks like:** "All tests pass" without having run them; marking a failing test as skipped; loosening an assertion until it passes.

**Instead:** run the checks and report the actual result, including failures. A failing test is information.

## 9. Dogma against the codebase

**Looks like:** wrapping every Go error in a custom exception-like type; replacing idiomatic Kotlin `T?` with `Optional<T>`; renaming `IOrderRepository` to `OrderRepository` in a C# project; splitting a hot loop into virtual calls.

**Instead:** follow `SKILL.md` section 0. Keep the book's intent and write it in the codebase's dialect.
