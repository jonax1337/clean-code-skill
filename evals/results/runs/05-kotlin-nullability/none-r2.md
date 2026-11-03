```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**

- **Removed the null-guard early return.** `repo.findById(id)?.displayName()` expresses "no user, no name" with a safe call, so the function becomes a single expression.
- **Extracted the naming rule into `User.displayName()`.** The service method now reads as "find the user, get their display name", and the nickname-or-full-name rule has its own named place.
- **Simplified the nickname check.** `nickname?.takeIf { it.isNotBlank() }` replaces `nickname != null && nickname.isNotBlank()`. (`isNullOrBlank()` would also work, but it doesn't smart-cast the value, so `takeIf` with the elvis operator is cleaner here.)
- **Used a string template** instead of `+` concatenation.

**Optional follow-up:** if `displayName` is a rule about a user rather than about the service, consider moving it into `User` itself (as a member or extension in the same file) so other callers can reuse it without going through `UserService`.