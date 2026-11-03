# Refactor untested code with many callers (TypeScript)

Tests: behavior preserved without existing tests (characterization tests first), callers and types stay compatible, magic numbers named, `any` replaced by a type that fits every caller, no over-engineering, verified with tests and the type checker.

## Prompt

Please clean up `getPrice` in `src/pricing.ts`, it's hard to read. It's used all over the codebase, so don't break anything.
