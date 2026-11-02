# Translating the book into your language

*Clean Code* uses Java. When a rule collides with how a language is normally written, write it the way the language is normally written and keep the rule's intent. These are the collisions agents hit most often.

## Errors: "use exceptions instead of error codes"

Intent: errors cannot be ignored silently, and the main path stays readable.

| Language | Idiomatic form |
|---|---|
| Go | Return `error`; wrap with `fmt.Errorf("load config %s: %w", path, err)`; `panic` only for programmer errors |
| Rust | `Result<T, E>` with `?`; `thiserror` for libraries, `anyhow` for applications |
| Kotlin | Exceptions; `Result` or sealed result types where the codebase already uses them |
| Swift | `throws`; `Result` for callbacks |
| TypeScript | Exceptions, or a `Result` union if the codebase uses one |
| Python | Specific exception types; never bare `except:` |
| C# / Java | Exceptions; no `catch` that only logs. "Prefer unchecked exceptions" is Java-specific advice |

## Absence: "don't return null"

Intent: callers should not be able to forget the empty case.

| Language | Idiomatic form |
|---|---|
| Go | Zero value plus `ok bool`, or `nil, err` |
| Rust | `Option<T>` |
| Kotlin, Swift | Nullable types (`T?`) with `?:` / `?.` / `guard let` are idiomatic. Do not replace them with `Optional` |
| TypeScript | `T \| undefined` under `strictNullChecks` is idiomatic |
| Python | `T \| None` with type hints; empty collections for "no results" |
| C# | Nullable reference types (`T?`) when enabled; `TryGet(out T value)` pattern |

## Names: "avoid encodings"

Intent: names describe meaning, not type or scope.

- C#: the `I` prefix for interfaces (`IOrderRepository`) **is** the convention. Keep it.
- Python: a leading underscore for non-public members is a convention, not an encoding.
- Everywhere else: no `m_`, no Hungarian notation, no type suffixes like `nameString`.

## Dispatch: "prefer polymorphism to switch"

Intent: each type decision lives in one place.

- Rust `match` on an enum, Kotlin `when` over a sealed class, Java `switch` expressions over a sealed interface and C# switch expressions are idiomatic and get completeness checks or warnings from the compiler. TypeScript gets the same with a discriminated union plus an `assertNever(x: never)` default. None of these is a smell.
- The smell is the *same* switch repeated in several places. Fix that.
- In hot paths, a switch is usually faster than virtual dispatch. Keep it.

## Data: "hide data behind behavior"

Intent: encapsulate behavior; do not expose internals that callers then manipulate.

- Plain data is fine as plain data: Go structs with exported fields, Rust structs, Kotlin `data class`, C#/Java `record`, Python `@dataclass`, TypeScript interfaces.
- Do not add getters and setters that only forward to a field.

## Function size

Intent: one thing per function.

- Go and C code often has longer functions with early returns. That is normal and readable.
- Split by meaning, not by line count.

## Rules of thumb

- **Consistency beats stylistic correctness.** If a Python codebase returns `None` everywhere, a new function that raises `NotFoundError` is the inconsistent one.
- **The project's formatter and linter are the style guide.** Do not argue with `gofmt`, `rustfmt`, `black`, `prettier` or `ktlint`.
