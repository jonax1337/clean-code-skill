```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: fullName()

    private fun User.fullName(): String = "$firstName $lastName"
}
```

**What changed**

- **Removed the early-return null checks.** `?.` propagates the null from `findById` directly, so the function is a single expression.
- **Replaced the `nickname != null && nickname.isNotBlank()` check** with `nickname?.takeIf { it.isNotBlank() } ?: fullName()`. This is more idiomatic and avoids relying on smart casts (which only work here if `nickname` is a stable `val`).
- **Extracted `fullName()`** and used a string template instead of `+` concatenation, so the intent is named and readable.
- **Extracted `User.displayName()`** as a private extension so the public method only describes the lookup, and the naming rule lives in one place.

Behavior is unchanged: it returns `null` for an unknown id, the nickname if it's non-blank, otherwise "first last".

If you'd like to go one step further, `displayName()` and `fullName()` are really domain logic and could live on `User` itself, leaving `UserService` with just the repository lookup.