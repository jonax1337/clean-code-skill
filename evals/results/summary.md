# Eval results

8 coding tasks, 3 runs each, graded blind. Coding model: sonnet, judge: opus.

| Condition | Assertions passed | Judge quality (1–10) | Avg. cost per task |
|---|---|---|---|
| No skill | 93.3% | 7.6 | $0.012 |
| This repo | 99.2% | 8.5 | $0.022 |
| unclebob/ub-mode | 95.0% | 6.5 | $0.023 |
| sickn33/clean-code | 92.5% | 7.2 | $0.018 |
| ertugrul-dmr/clean-code (3 of 8 tasks) | 88.9% | 6.7 | $0.022 |

## By case (assertions passed)

| Case | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| Reuse existing helper (Python) | 80% | 93% | 80% | 80% | 87% |
| Refactor a function with many callers (TypeScript) | 100% | 100% | 100% | 100% | 100% |
| Clean up hot-path code (Java) | 80% | 100% | 80% | 60% | n/a |
| Error handling in Go | 100% | 100% | 100% | 100% | n/a |
| Nullability in Kotlin | 100% | 100% | 100% | 100% | n/a |
| Review a pull request (Python) | 100% | 100% | 100% | 100% | 80% |
| Follow codebase conventions (C#) | 100% | 100% | 100% | 100% | n/a |
| Minimal bugfix with regression test (JavaScript) | 87% | 100% | 100% | 100% | n/a |

## By case (judge quality, 1–10)

| Case | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| Reuse existing helper (Python) | 7.7 | 8.7 | 6.0 | 6.7 | 6.3 |
| Refactor a function with many callers (TypeScript) | 7.7 | 8.0 | 6.0 | 7.7 | 8.0 |
| Clean up hot-path code (Java) | 6.7 | 8.0 | 6.0 | 5.3 | n/a |
| Error handling in Go | 9.0 | 9.0 | 7.0 | 7.7 | n/a |
| Nullability in Kotlin | 7.0 | 8.3 | 7.7 | 7.3 | n/a |
| Review a pull request (Python) | 8.3 | 9.0 | 7.0 | 7.7 | 5.7 |
| Follow codebase conventions (C#) | 7.7 | 8.7 | 6.0 | 7.7 | n/a |
| Minimal bugfix with regression test (JavaScript) | 6.7 | 8.7 | 6.7 | 8.0 | n/a |
