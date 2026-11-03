```kotlin
class UserService(private val repository: UserRepository) {

    fun displayName(id: Long): String? =
        repository.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname.takeUnless { it.isNullOrBlank() } ?: fullName()

    private fun User.fullName(): String = "$firstName $lastName"
}
```

**What changed and why**

- **Removed the null-guard boilerplate.** `if (user == null) return null` becomes `?.`, so the public method reads as one step: find the user, get their display name.
- **One level of abstraction per function.** `displayName(id)` handles lookup, `User.displayName()` holds the nickname-or-full-name rule, and `fullName()` handles string formatting.
- **Intention-revealing names.** `repo` became `repository`, and the "nickname if present, otherwise full name" rule is now a named concept.
- **Dropped the `// returns User?` comment.** The type already says it.
- **Replaced `+` concatenation with a string template.**
- **Simplified the nickname check.** `takeUnless { it.isNullOrBlank() }` replaces the manual null-and-blank test.

**Behavior is preserved.** The method still returns `null` for an unknown id, returns the nickname untrimmed when it isn't blank, and otherwise returns `"first last"`. I kept the `String?` return type because callers may depend on it. Switching to an exception or a result type would change the contract, so that would need to be a separate, deliberate decision.

**Design option:** if you own `User`, `displayName()` and `fullName()` fit better as members of `User`. Then `UserService` only does the lookup, and the naming rule sits next to its data.

I haven't run anything. Before merging, I'd add focused tests for four cases: unknown id, non-blank nickname, null nickname, and blank nickname (e.g. `"  "`).