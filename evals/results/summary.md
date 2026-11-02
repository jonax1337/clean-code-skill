# Eval results

8 coding tasks, 3 runs each, graded blind. Coding model: sonnet, judge: opus.

| Condition | Assertions passed | Judge quality (1–10) | Avg. cost per task |
|---|---|---|---|
| No skill | 95.8% | 7.5 | $0.013 |
| sickn33/clean-code | 92.5% | 7.5 | $0.018 |
| This repo, v1 | 89.2% | 6.2 | $0.019 |
| This repo, v2 | 99.2% | 8.4 | $0.017 |

## By case (assertions passed)

| Case | No skill | sickn33/clean-code | This repo, v1 | This repo, v2 |
|---|---|---|---|---|
| Reuse existing helper (Python) | 80% | 87% | 93% | 100% |
| Refactor a function with many callers (TypeScript) | 100% | 100% | 100% | 100% |
| Clean up hot-path code (Java) | 93% | 60% | 80% | 93% |
| Error handling in Go | 100% | 100% | 93% | 100% |
| Nullability in Kotlin | 100% | 100% | 60% | 100% |
| Review a pull request (Python) | 100% | 100% | 100% | 100% |
| Follow codebase conventions (C#) | 100% | 100% | 100% | 100% |
| Minimal bugfix with regression test (JavaScript) | 93% | 93% | 87% | 100% |

## By case (judge quality, 1–10)

| Case | No skill | sickn33/clean-code | This repo, v1 | This repo, v2 |
|---|---|---|---|---|
| Reuse existing helper (Python) | 6.3 | 7.3 | 6.3 | 8.7 |
| Refactor a function with many callers (TypeScript) | 7.0 | 8.0 | 8.0 | 7.7 |
| Clean up hot-path code (Java) | 7.0 | 5.0 | 6.7 | 7.7 |
| Error handling in Go | 8.7 | 8.3 | 6.3 | 9.0 |
| Nullability in Kotlin | 8.0 | 7.7 | 4.0 | 9.0 |
| Review a pull request (Python) | 8.3 | 8.0 | 6.0 | 8.0 |
| Follow codebase conventions (C#) | 8.3 | 7.7 | 7.0 | 9.0 |
| Minimal bugfix with regression test (JavaScript) | 6.3 | 7.7 | 5.7 | 8.0 |
