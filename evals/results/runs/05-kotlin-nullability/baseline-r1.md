```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: fullName()

    private fun User.fullName(): String = "$firstName $lastName"
}
```

**What changed and why**

- **Removed null-check boilerplate:** `repo.findById(id)?.…` replaces the early `return null`, so the null case propagates naturally.
- **Eliminated the smart-cast dance:** `nickname?.takeIf { it.isNotBlank() }` handles both null and blank in one expression. (The original only compiled if `nickname` was a stable `val`; this version doesn't depend on that.)
- **Extracted intention-revealing functions:** `displayName()` and `fullName()` name the two rules (prefer a non-blank nickname, otherwise use the full name), so the public method reads as a single step.
- **String template** instead of `+` concatenation.
- **Expression body** for the public function, since it's now a single expression.

**Optional follow-up:** if `displayName` logic is purely about `User`, consider moving it into `User` itself (as a member or extension in the domain package), leaving `UserService` only to look up the user. I kept it private here to avoid changing your public API.