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

- **Null handling:** The early-return `if (user == null)` became a safe call (`?.`), so the null case propagates naturally.
- **Nickname check:** `nickname != null && nickname.isNotBlank()` became `nickname?.takeIf { it.isNotBlank() }`, with the elvis operator (`?:`) falling back to the full name. This also avoids relying on smart-casting a property from another class, which only works if `nickname` is a stable `val` in the same module.
- **Extraction:** Small private extension functions (`displayName`, `fullName`) give each rule a name, so the public method reads as one intention: find the user, then get their display name.
- **String building:** `firstName + " " + lastName` became a string template.
- **Expression body:** `displayName(id)` is now a single expression, since there's no remaining branching.

**Optional follow-up:** If `displayName` logic is purely about a `User`, consider moving it onto `User` itself (as a member or an extension next to the class). That keeps `UserService` focused on lookup and makes the naming rule reusable and easy to unit test.