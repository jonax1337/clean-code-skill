```kotlin
class UserService(private val repo: UserRepository) {

    fun displayName(id: Long): String? =
        repo.findById(id)?.displayName()

    private fun User.displayName(): String =
        nickname?.takeIf { it.isNotBlank() } ?: "$firstName $lastName"
}
```

**What changed**

- The null check and early return became a safe call (`?.`), which is idiomatic for a nullable "not found" in Kotlin.
- The nickname rule (use it unless null or blank) is now one expression with `takeIf` and the elvis operator, instead of a null check plus a blank check.
- The fallback uses a string template instead of concatenation.
- The rule for building a name moved into a small private extension, so `displayName(id)` only does the lookup and the extension only decides the name. That separates the two levels of abstraction.

Behavior is unchanged: unknown id gives `null`, a non-blank nickname wins (returned as-is, not trimmed), otherwise `"first last"`.

**Not run:** I couldn't run tests or the compiler in this session, and I haven't seen `UserService`'s existing tests, so please run yours. If none cover this, three cases worth pinning are: unknown id, blank nickname falling back to the full name, and a present nickname.

**Left alone:** the public signature and the `UserRepository` interface. If `User` is your own class, the name rule could later live on `User` itself, which would let other callers reuse it. I didn't do that since I can't see the class.