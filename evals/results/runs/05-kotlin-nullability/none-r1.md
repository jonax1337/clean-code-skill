```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**

- **Null handling with `?.`**: the early `return null` guard is replaced by a safe call, so a missing user naturally yields `null`.
- **Expression body**: `displayName(id)` is now a single expression, which reads as "find the user, then get their display name."
- **Extracted `User.displayName()`**: the naming rule (nickname if present, otherwise full name) lives in one small, named function. It's private here, but it could move onto `User` itself if other callers need it.
- **`takeIf` + elvis**: `nickname?.takeIf { it.isNotBlank() } ?: ...` replaces the null check plus blank check, and it avoids the repeated `user.nickname` access.
- **String template**: `"$firstName $lastName"` replaces concatenation.

**Optional follow-up**

If `User` is your own class, consider putting `displayName()` there (as a member or property), since it only depends on `User`'s own data. `UserService` would then just be `repo.findById(id)?.displayName`.