# Smells and heuristics (Clean Code, ch. 17)

The catalog from chapter 17 of *Clean Code*. Titles are the book's; descriptions and fixes are a condensed paraphrase. Cite the code in reviews.

Every entry is subject to the precedence in `SKILL.md` section 0: project conventions and language idioms come first.

## Contents

- [Comments (C)](#comments-c)
- [Environment (E)](#environment-e)
- [Functions (F)](#functions-f)
- [General (G)](#general-g)
- [Java (J)](#java-j)
- [Names (N)](#names-n)
- [Tests (T)](#tests-t)

## Comments (C)

| Code | Title | Symptom → fix |
|---|---|---|
| C1 | Inappropriate Information | Changelog, author, ticket metadata in comments → belongs in VCS or tracker; delete |
| C2 | Obsolete Comment | Refers to something that no longer exists → update or delete |
| C3 | Redundant Comment | Paraphrases the code (`i++ // increment i`) → delete |
| C4 | Poorly Written Comment | Vague or sloppy → short, precise, correct |
| C5 | Commented-Out Code | Dead code in comments → delete; version control remembers |

## Environment (E)

| Code | Title | Symptom → fix |
|---|---|---|
| E1 | Build Requires More Than One Step | Several manual steps to build → one command |
| E2 | Tests Require More Than One Step | Tests need a setup ritual → one command |

## Functions (F)

| Code | Title | Symptom → fix |
|---|---|---|
| F1 | Too Many Arguments | More than three → parameter object or split the function |
| F2 | Output Arguments | Argument mutated to return a result → return a value or change own state |
| F3 | Flag Arguments | Boolean selects behavior → two functions |
| F4 | Dead Function | Never called → delete |

## General (G)

| Code | Title | Symptom → fix |
|---|---|---|
| G1 | Multiple Languages in One Source File | HTML, SQL, JS mixed in one file → separate where the stack allows |
| G2 | Obvious Behavior Is Unimplemented | Function does not do what its name promises → least surprise |
| G3 | Incorrect Behavior at the Boundaries | Edge cases wrong → test every boundary, do not trust intuition |
| G4 | Overridden Safeties | Warnings ignored, tests disabled, checks off → never |
| G5 | Duplication | Same code or logic twice, repeated `switch` chains → function, type, polymorphism |
| G6 | Code at Wrong Level of Abstraction | High- and low-level mixed; details in base class → separate levels |
| G7 | Base Classes Depending on Their Derivatives | Base knows subclasses → polymorphism |
| G8 | Too Much Information | Wide interfaces, many public members → expose little, minimize coupling |
| G9 | Dead Code | Unreachable branches → delete |
| G10 | Vertical Separation | Declaration far from use → move together |
| G11 | Inconsistency | Same thing done or named two ways → pick one |
| G12 | Clutter | Empty constructors, unused variables, noise → remove |
| G13 | Artificial Coupling | Coupling without reason (general enum inside a specific class) → move it |
| G14 | Feature Envy | Method mostly uses another object's data → move the method there |
| G15 | Selector Arguments | Enum/int/bool picks behavior → separate functions |
| G16 | Obscured Intent | Cryptic expressions, abbreviations → spell out, use structure |
| G17 | Misplaced Responsibility | Code is not where a reader would look → move it |
| G18 | Inappropriate Static | Static method that should be polymorphic → instance method |
| G19 | Use Explanatory Variables | Complex expression → named intermediate variables |
| G20 | Function Names Should Say What They Do | `date.add(5)` → `addDays(5)` |
| G21 | Understand the Algorithm | Works by trial and error → understand it, then write it cleanly |
| G22 | Make Logical Dependencies Physical | Module assumes knowledge of another → ask for it explicitly |
| G23 | Prefer Polymorphism to If/Else or Switch/Case | Same type switch in many places → one switch in a factory, polymorphism elsewhere (hot paths excepted) |
| G24 | Follow Standard Conventions | Team or language conventions ignored → follow them |
| G25 | Replace Magic Numbers with Named Constants | Unexplained literals → named constants |
| G26 | Be Precise | Floats for money, unchecked nulls, unchecked concurrency → precise types and decisions |
| G27 | Structure over Convention | Correctness relies on a naming convention → enforce with types or abstract methods |
| G28 | Encapsulate Conditionals | Long inline condition → `if (shouldBeDeleted(timer))` |
| G29 | Avoid Negative Conditionals | `if (!buffer.shouldNotCompact())` → positive form |
| G30 | Functions Should Do One Thing | Function with sections → split |
| G31 | Hidden Temporal Couplings | Invisible ordering requirement → pass results along |
| G32 | Don't Be Arbitrary | Structure without visible reason → structure deliberately and consistently |
| G33 | Encapsulate Boundary Conditions | `+1`/`-1` scattered → one named variable or method |
| G34 | Functions Should Descend Only One Level of Abstraction | Several levels in one function → one level down per function |
| G35 | Keep Configurable Data at High Levels | Defaults buried deep → define at the top, pass down |
| G36 | Avoid Transitive Navigation | `a.getB().getC().doIt()` → ask direct collaborators |

## Java (J)

Applies by analogy to other languages; the project's linter wins.

| Code | Title | Symptom → fix |
|---|---|---|
| J1 | Avoid Long Import Lists by Using Wildcards | Long import lists → wildcards (only where the project's style allows it) |
| J2 | Don't Inherit Constants | Inheriting an interface just for constants → static import or direct reference |
| J3 | Constants versus Enums | Groups of `static final int` → enum |

## Names (N)

| Code | Title | Symptom → fix |
|---|---|---|
| N1 | Choose Descriptive Names | Name hides purpose → rename, revisit as meaning evolves |
| N2 | Choose Names at the Appropriate Level of Abstraction | Name reveals implementation (`dial` for a modem) → `connect` |
| N3 | Use Standard Nomenclature Where Possible | Invented terms → pattern names, domain language |
| N4 | Unambiguous Names | `doRename` → unambiguous, even if longer |
| N5 | Use Long Names for Long Scopes | Short name, wide scope → length grows with scope |
| N6 | Avoid Encodings | `m_`, Hungarian notation → drop (ecosystem conventions like the C# `I` prefix excepted) |
| N7 | Names Should Describe Side-Effects | `getOos()` creates an object → `createOrReturnOos()` |

## Tests (T)

| Code | Title | Symptom → fix |
|---|---|---|
| T1 | Insufficient Tests | What can break is untested → test it |
| T2 | Use a Coverage Tool! | Unknown gaps → measure coverage |
| T3 | Don't Skip Trivial Tests | "Too simple to test" → test anyway, it documents |
| T4 | An Ignored Test Is a Question about an Ambiguity | Unclear requirement → record as pending test and clarify |
| T5 | Test Boundary Conditions | Boundaries untested → test them deliberately |
| T6 | Exhaustively Test Near Bugs | Bugs cluster → test around each bug |
| T7 | Patterns of Failure Are Revealing | Failure pattern ignored → use it for diagnosis |
| T8 | Test Coverage Patterns Can Be Revealing | Code not executed by failing tests → hints at the cause |
| T9 | Tests Should Be Fast | Slow tests do not get run → keep them fast |
