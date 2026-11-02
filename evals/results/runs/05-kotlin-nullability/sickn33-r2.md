```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: fullName()

    private fun User.fullName(): String =
        "$firstName $lastName"
}
```

**What changed and why**

- **Removed the null-check ladder.** `repo.findById(id)?.displayName()` expresses "if there's a user, get its display name" in one line, and the public function now reads at a single level of abstraction.
- **Extracted the naming rule.** `displayName()` states the policy (nickname if it has content, otherwise full name), and `fullName()` holds the formatting detail. Each function does one thing.
- **Used idiomatic Kotlin.** `nickname?.takeIf { it.isNotBlank() }` replaces the `!= null && isNotBlank()` check, and the string template replaces the `+` concatenation.
- **Removed the comment.** `// returns User?` was only restating the repository's signature.

**Behavior preserved**

- I kept `String?` as the return type. Returning `null` for an unknown user is the contract callers rely on, and nullable types are idiomatic in Kotlin. Switching to an exception or a result type would change behavior, so I left that alone.
- The nickname is returned untrimmed, exactly as before.

**Suggestions I haven't applied**

- If you can modify `User`, `displayName()` and `fullName()` would fit better there, since they only use `User`'s own data. `UserService` would then just call `repo.findById(id)?.displayName()`.
- I couldn't run anything here, so I haven't verified this. Focused tests would cover: unknown id → `null`, a nickname → the nickname, a `null` nickname → full name, and a blank nickname → full name.