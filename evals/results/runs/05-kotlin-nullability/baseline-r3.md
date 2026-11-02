```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**

- **Removed the null guard and early returns.** The safe call `?.` propagates `null` when the user isn't found, so the function becomes a single expression.
- **Replaced the nickname check with `takeIf` and the elvis operator.** `nickname?.takeIf { it.isNotBlank() }` handles both `null` and blank in one step. It also avoids the duplicated `nickname` access, which only compiled before because of a smart cast that depends on `nickname` being a stable `val`.
- **Extracted the naming rule into a private extension, `User.displayName()`.** The service method now says what it does (look up, then format), and the rule "nickname if present, otherwise full name" has its own named home.
- **Used a string template** instead of concatenation for the full name.

Behavior is unchanged: unknown id returns `null`, a non-blank nickname wins, and otherwise you get `"first last"`.

If you'd rather keep the naming logic with the data, move `displayName()` into `User` itself (as a member or an extension next to it). That makes it reusable and testable without a repository.